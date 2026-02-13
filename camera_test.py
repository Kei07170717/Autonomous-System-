import cv2

camera_num = int(input("Enter camera number: "))
filename = input("Enter filename to save (e.g., photo.jpg): ")

cap = cv2.VideoCapture(camera_num)

if not cap.isOpened():
    print(f"Error: Could not open camera {camera_num}")
    exit()

print("Press SPACE to take photo, ESC to cancel")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame")
        break
    
    cv2.imshow(f"Camera {camera_num}", frame)
    
    key = cv2.waitKey(1)
    if key == 32:  # SPACE
        cv2.imwrite(filename, frame)
        print(f"Photo saved to {filename}")
        break
    elif key == 27:  # ESC
        print("Cancelled")
        break

cap.release()
cv2.destroyAllWindows()