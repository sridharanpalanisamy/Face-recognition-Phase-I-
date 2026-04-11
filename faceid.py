import cv2
model_for_cv = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
webcam = cv2.VideoCapture(0)
while True:
    status, video = webcam.read()
    gray_color=cv2.cvtColor(video,cv2.COLOR_BGR2GRAY)
    face=model_for_cv.detectMultiScale(gray_color,1.3,5)
    for(x,y,w,h) in face:
        cv2.rectangle(video,(x,y), (x+w,y+h),(0,0,200),2)
    cv2.imshow("Display the capture", video)
    if cv2.waitKey(1) == ord("e"):
        break
webcam.release()
cv2.destroyAllWindows()
