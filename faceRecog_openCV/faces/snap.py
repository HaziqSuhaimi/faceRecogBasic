import cv2
from time import sleep

cap = cv2.VideoCapture(0)

while True:
    
    ret , frame = cap.read()
    
    cv2.imshow("preview",frame)
    
    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.imwrite("koqi.jpg",frame)
        cv2.imshow("preview",frame)
        sleep(2)
        break

    
cap.release()
cv2.destroyAllWindows()
