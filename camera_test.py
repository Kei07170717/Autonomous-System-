import cv2

for i in [0,1,2,3]:
    cap = cv2.VideoCapture(i)
    ret, frame = cap.read()
    if ret:
        print(f"/dev/video{i} works")
    else:
        print(f"/dev/video{i} no frame")
    cap.release()


