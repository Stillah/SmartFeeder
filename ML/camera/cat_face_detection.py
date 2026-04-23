import serial
import argparse
import requests
import cv2
import time
import logging
from datetime import datetime, timedelta
from requests.exceptions import HTTPError, RequestException
from weights import Weights

logger = logging.Logger("Camera")
url = "http://localhost/internal/images/"
FRAMES_IN_CYCLE = 30
FRAMES_THRESHOLD = 20
INTERVAL_SEC = 1


def start_camera(user_id: str, display: bool = False) -> None:
    # Load the pre-trained Haar Cascade Classifiers for cat face and smile detection
    cat_face_cascade = cv2.CascadeClassifier(
        "haarcascade/haarcascade_frontalcatface_extended.xml"
    )  # Use custom path for cat face cascade
    smile_cascade = cv2.CascadeClassifier(
        "haarcascade/haarcascade_smile.xml"
    )  # Use custom path for smile cascade

    weights = Weights("/dev/ttyUSB0", 115200, 0.1)
    # Start video capture from the webcam
    cap = cv2.VideoCapture(0)
    last = None
    prev_weight = None
    cnt_cats = 0

    cycle = 1
    cat_here = False
    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()
        weight_delta = None
        current_weight = weights.get_weight()

        prev_cat_here = cat_here

        # Convert the frame to grayscale (Haar cascades work on grayscale images)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect cat faces in the image
        cat_faces = cat_face_cascade.detectMultiScale(gray, 1.3, 5)

        # Exactly one cat
        if len(cat_faces) == 1:
            cnt_cats += 1

        if cycle == FRAMES_IN_CYCLE:
            if cnt_cats > FRAMES_THRESHOLD:
                cat_here = True
            else:
                cat_here = False
                if prev_weight and current_weight and prev_cat_here:
                    # Here we calculated delta and ready to send it
                    weight_delta = current_weight - prev_weight
                if current_weight:
                    prev_weight = current_weight

        # save image to send to the API
        if cat_here and (
            not last or datetime.now() - last > timedelta(seconds=INTERVAL_SEC)
        ):
            # Convert RGB to BGR for correct colors
            bgr_array = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            success, encoded_img = cv2.imencode(".jpg", bgr_array)
            if not success:
                logger.warning("Failed to encode image")
                raise RuntimeError("Failed to encode image")

            files = {"file": encoded_img.tobytes()}
            params = {"user_id": user_id}

            try:
                response = requests.post(url, params=params, files=files)
                image_id = response.json()
                logging.info(f"Scucessfully sent image. Image_id: {image_id}")
            except HTTPError as e:
                # Server returned an error (e.g., 500, 422, 404)
                logger.warning(
                    f"HTTP error {e.response.status_code}: {e.response.text}"
                )
            except RequestException as e:
                # Network errors, timeouts, etc.
                logging.warning(f"Request failed: {e}")

            last = datetime.now()

        if cycle == FRAMES_IN_CYCLE:
            cnt_cats = 0
        cycle = cycle % FRAMES_IN_CYCLE + 1

        if not display:
            continue

        # Loop through all cat faces detected
        for x, y, w, h in cat_faces:
            # Draw rectangle around the cat face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Region of interest for detecting smiles (mouth area)
            roi_gray = gray[y : y + h, x : x + w]
            roi_color = frame[y : y + h, x : x + w]

            # Detect smiles in the cat face region
            smiles = smile_cascade.detectMultiScale(roi_gray, 1.8, 20)

            # Loop through all smiles detected
            for sx, sy, sw, sh in smiles:
                # Draw rectangle around the smile
                cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (0, 255, 0), 2)

        # Break the loop when the user presses 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        # Display the resulting frame
        cv2.imshow("Cat Face and Smile Detection", frame)

    # Release the webcam and close the window
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Run with -display flag to see the camera
    # --user_id to provide user_id
    parser = argparse.ArgumentParser(prefix_chars="-")
    parser.add_argument(
        "-display", action="store_true", help="Display what camera sees"
    )
    parser.add_argument(
        "--user_id",
        type=str,
        default="123e4567-e89b-12d3-a456-426614174000",
        help="User UUID",
    )
    args = parser.parse_args()

    start_camera(args.display, args.user_id)
