# Face Recognition Attendance System

## Phase 1 – Real-Time Face Detection using OpenCV

### 📌 Description

This phase implements **real-time face detection** using OpenCV and Haar Cascade Classifier.
The webcam captures video frames, detects faces, and draws rectangles around detected faces.

---

## 📂 File

`faceid.py`

---

## 🧠 Code Explanation (Line by Line)

```python
import cv2
```

➡️ Imports the OpenCV library used for image processing and face detection.

```python
model_for_cv = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
```

➡️ Loads the **Haar Cascade face detection model** provided by OpenCV.
➡️ This XML file contains trained data for detecting human faces.

```python
webcam = cv2.VideoCapture(0)
```

➡️ Starts the webcam.
➡️ `0` means default camera (usually laptop webcam).

```python
while True:
```

➡️ Creates an infinite loop to continuously capture video frames.

```python
status, video = webcam.read()
```

➡️ Reads a frame from the webcam.
➡️ `status` → True if frame captured successfully
➡️ `video` → Captured image frame

```python
gray_color = cv2.cvtColor(video, cv2.COLOR_BGR2GRAY)
```

➡️ Converts the frame from **color to grayscale**.
➡️ Face detection works faster in grayscale.

```python
face = model_for_cv.detectMultiScale(gray_color, 1.3, 5)
```

➡️ Detects faces in the grayscale image.
Parameters:

* `1.3` → Scale factor (image size reduction)
* `5` → Minimum neighbors (accuracy control)

```python
for (x, y, w, h) in face:
```

➡️ Loops through each detected face.
➡️ `x, y` → top-left coordinates
➡️ `w, h` → width and height of face

```python
cv2.rectangle(video, (x,y), (x+w,y+h), (0,0,200), 2)
```

➡️ Draws a rectangle around the detected face.
➡️ `(0,0,200)` → Red color
➡️ `2` → Rectangle thickness

```python
cv2.imshow("Display the capture", video)
```

➡️ Displays the webcam output with detected faces.

```python
if cv2.waitKey(1) == ord("e"):
```

➡️ Waits for key press.
➡️ Press **"e"** to exit the program.

```python
break
```

➡️ Stops the loop when "e" is pressed.

```python
webcam.release()
```

➡️ Releases the webcam.

```python
cv2.destroyAllWindows()
```

➡️ Closes all OpenCV windows.

---

## ▶️ How to Run

```bash
python faceid.py
```

Press **E** to exit.

---

## 📦 Requirements

* Python 3.x
* OpenCV

Install OpenCV:

```bash
pip install opencv-python
```

---

## 🎯 Output

* Opens webcam
* Detects face
* Draws rectangle around face
* Press **E** to exit

---

## 🚀 Phase 1 Completed

Real-time face detection using Haar Cascade model.

