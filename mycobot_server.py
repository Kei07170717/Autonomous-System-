import socket
import serial
import time
import threading
import json 

from pymycobot import PI_PORT, PI_BAUD
from pymycobot.mycobot280 import MyCobot280
from queue import Queue, Empty #Queue is Thread-safe design


robot_freq = 10
T = 1.0/ robot_freq
gripper_interval = 25
host = "0.0.0.0"
port = 9000


class RobotController:
    def __init__(self):
        
        self.mc = MyCobot280(PI_PORT, PI_BAUD)
        self.mc.power_on()
        time.sleep(1)
        self.mc.send_angles([0,0,0,0,0,0], 100)
        time.sleep(2)

        
        self.queue = Queue(maxsize = 20) #max size of the buffer 
        self.running = True
        self.current_angles = [0,0,0,0,0,0]

        self.last_gripper_val = -1
        self.gripper_steps_counter = gripper_interval + 1

    def execute_loop(self):

        while self.running == True:
            start_time = time.time()

            try:
                angles =self.mc.get_angles()
                if angles:
                    self.current_angles = angles
            except Exception:
                pass

            if self.queue.empty() == False:
                try:
                    action_chunks = self.queue.get_nowait()
                    arm_val = action_chunks[0] #arm value
                    gripper_val_binary = action_chunks[1]

                    self.mc.send_angles(arm_val, 100)

                    if gripper_val_binary != self.last_gripper_val:
                        if self.gripper_steps_counter >= gripper_interval:
        
                            time.sleep(0.02)
                            self.mc.set_gripper_value(gripper_val_binary, 100)
                            time.sleep(0.02) 
                                
                            self.last_gripper_val = gripper_val_binary
                            self.gripper_steps_counter = 0 # Reset cooldown
                        else:
                            pass
                        
                    self.gripper_steps_counter += 1
                except Empty:
                    pass

            elapsed_time = time.time() - start_time #Fixed time stop loop
            sleep_time = T - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)

    def reset(self):
        t = threading.Thread(target = self.execute_loop) #clone of the program
        t.daemon = True # if the program crahes, kill the server
        t.start() #the clone starts running simultaneously with main code

    def add_chunk(self, chunk):
        for movement in chunk:
            self.queue.put(movement)

    def get_state(self):
        return self.current_angles
    

def main():
    mycobot280 = RobotController()
    mycobot280.reset()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket.socket: communication end point, AF_INET: address family, SOCK_STREAM: tcp connection 
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(1)

    print(f"Server will listen to {host}:{port}")

    try:
        while True:
            print("Connecting to OpenVLA")
            client, addr = server_sock.accept()
            print(f"Connected by {addr}")

            while client:
                while True:
                    try:
                        length_bytes = client.recv(4) #4byte length header
                        if not length_bytes:
                            break

                        msg_len = int.from_bytes(length_bytes, byteorder='big')
                        data_bytes = client.recv(msg_len)
                        
                        if not data_bytes: 
                            break

                        request = json.loads(data_bytes.decode('utf-8'))
                        
                        
                        if 'action_chunk' in request: #chunking action 
                            mycobot280.add_chunk(request['action_chunk'])
                            
                        
                        response = { "joint_angles": mycobot280.get_state(), "buffer_size": mycobot280.queue.qsize()}
                        
                        resp_json = json.dumps(response).encode('utf-8')
                        client.sendall(len(resp_json).to_bytes(4, byteorder='big') + resp_json)
                    except Exception: 
                        break
    except KeyboardInterrupt:
        print("\n Stopping the robot")
    finally:
        mycobot280.running = False
        server_sock.close()

if __name__ == "__main__":
    main()


