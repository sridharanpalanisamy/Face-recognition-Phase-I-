import cv2

# Step 1: Load the Haar Cascade face detection model
model_for_cv = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Step 2: Check whether the model loaded successfully
if model_for_cv.empty():
    print("Error: Face detection model could not be loaded.")
    raise SystemExit(1)

# Step 3: Open the default webcam (usually camera index 0)
webcam = cv2.VideoCapture(0)

# Step 4: Check whether the webcam opened successfully
if not webcam.isOpened():
    print("Error: Could not access the webcam.")
    raise SystemExit(1)

try:
    while True:
        # Step 5: Capture one frame from the webcam
        status, video = webcam.read()

        # Step 6: Stop if the frame was not captured successfully
        if not status or video is None:
            print("Error: Could not capture a video frame.")
            break

        # Step 7: Convert the color frame to grayscale
        gray_color = cv2.cvtColor(video, cv2.COLOR_BGR2GRAY)

        # Step 8: Detect faces in the grayscale frame
        faces = model_for_cv.detectMultiScale(
            gray_color,
            scaleFactor=1.3,
            minNeighbors=5
        )

        # Step 9: Draw a rectangle around every detected face
        for (x, y, w, h) in faces:
            cv2.rectangle(
                video,
                (x, y),
                (x + w, y + h),
                (0, 0, 200),
                2
            )

        # Step 10: Display the number of faces detected
        face_count = len(faces)
        cv2.putText(
            video,
            f"Faces detected: {face_count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 200, 0),
            2
        )

        # Step 11: Display the webcam frame
        cv2.imshow("Face Detection - Phase I", video)

        # Step 12: Press E to exit
        if cv2.waitKey(1) & 0xFF == ord("e"):
            break

finally:
    # Step 13: Always release the webcam and close OpenCV windows
    webcam.release()
    cv2.destroyAllWindows()
