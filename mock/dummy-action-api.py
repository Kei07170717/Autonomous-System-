import json_numpy
import numpy as np
from flask import Flask, request, jsonify

# Patch json module to handle numpy arrays seamlessly
json_numpy.patch()

app = Flask(__name__)

@app.route('/act', methods=['POST'])
def act():
    try:
        # 1. Parse the incoming JSON payload
        payload = request.get_json()
        if not payload or "encoded" not in payload:
            return jsonify({"error": "Invalid payload format. Missing 'encoded' key."}), 400

        # 2. Decode the client's observation data (for testing/verification)
        decoded_data = json_numpy.loads(payload["encoded"])
        
        print("\n--- 📥 Received Observation ---")
        print(f"Instruction : {decoded_data.get('instruction')}")
        print(f"Image shape : {decoded_data.get('full_image').shape}")
        print(f"Robot state : {decoded_data.get('state')}")

        # Extract the current state from the decoded data
        current_state = decoded_data.get('state') 
        current_joints = current_state[:6]
        current_gripper = current_state[6]

        num_steps = 5
        actions = []
        
        for _ in range(num_steps):
            # Add a very tiny random "wiggle" (e.g., max 0.01 radians) to the current joints
            safe_joint_delta = np.random.uniform(-0.01, 0.01, size=6)
            next_joints = current_joints + safe_joint_delta
            
            # Keep the gripper mostly the same
            next_gripper = np.clip(current_gripper + np.random.uniform(-1, 1), 0, 100)
            
            actions.append(np.append(next_joints, next_gripper))
            
            # Update current_joints for the next step in the trajectory
            current_joints = next_joints 
            current_gripper = next_gripper
            
        actions = np.array(actions, dtype=np.float32)

        print("--- 📤 Sending Mock Actions ---")
        print(f"Actions shape : {actions.shape}")
        print(f"First action  : {actions[0]}")

        # 4. Encode the numpy array back to a string 
        encoded_actions = json_numpy.dumps(actions)
        
        # Return as a JSON string so resp.json() in your client parses it correctly 
        # into a string that json_numpy.loads() can then process.
        return jsonify(encoded_actions)

    except Exception as e:
        print(f"❌ Server Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Mock OpenVLA Server on http://0.0.0.0:8777...")
    # Host 0.0.0.0 allows connections if your client ('cerulean') is on another machine
    app.run(host='0.0.0.0', port=8777)
