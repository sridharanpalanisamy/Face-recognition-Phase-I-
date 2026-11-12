import cv2
from pathlib import Path

# Folder containing the test images
PROJECT_FOLDER = Path(__file__).resolve().parent
TEST_IMAGE_FOLDER = PROJECT_FOLDER / "test_images"

# Expected face count for each test image
TEST_CASES = {
    "single_face.jpg": 1,
    "multiple_faces.jpg": 2,
    "no_face.jpg": 0,
}

# Load OpenCV's pretrained Haar Cascade model
face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

if face_detector.empty():
    raise SystemExit(
        "ERROR: Could not load the Haar Cascade face detection model."
    )


def count_faces(image_path):
    """Read an image and return the number of faces detected."""
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError("Image could not be opened. Check the file format.")

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray_image,
        scaleFactor=1.3,
        minNeighbors=5
    )

    return len(faces)


def main():
    print("\nPHASE I - FACE DETECTION TESTS")
    print("=" *  40)

    if not TEST_IMAGE_FOLDER.exists():
        print(f"Test image folder not found: {TEST_IMAGE_FOLDER}")
        print("Create a folder named 'test_images' and add the three test images.")
        raise SystemExit(1)

    passed = 0
    failed = 0
    missing = 0

    for filename, expected_count in TEST_CASES.items():
        image_path = TEST_IMAGE_FOLDER / filename

        if not image_path.exists():
            print(f"NOT RUN: {filename} (image file is missing)")
            missing += 1
            continue

        try:
            actual_count = count_faces(image_path)

            if actual_count == expected_count:
                print(
                    f"PASS: {filename} | "
                    f"Expected: {expected_count} | Detected: {actual_count}"
                )
                passed += 1
            else:
                print(
                    f"FAIL: {filename} | "
                    f"Expected: {expected_count} | Detected: {actual_count}"
                )
                failed += 1

        except (ValueError, cv2.error) as error:
            print(f"ERROR: {filename} | {error}")
            failed += 1

    print("=" * 40)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Missing images: {missing}")
    print(f"Total test cases: {len(TEST_CASES)}")

    if failed > 0 or missing > 0:
        raise SystemExit(1)

    print("\nAll face detection tests passed!")


if __name__ == "__main__":
    main()
