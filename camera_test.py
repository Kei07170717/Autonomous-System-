import cv2

cap0 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(2)

while True:
    _, f0 = cap0.read()
    _, f2 = cap2.read()

    cv2.imshow("cam0", f0)
    cv2.imshow("cam2", f2)

    if cv2.waitKey(1)==27:
        break

    

