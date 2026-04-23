import argparse, requests, logging
from datetime import datetime, timedelta
from requests.exceptions import HTTPError, RequestException
from weights import Weights, WeightsMock
from cat_camera import CatDetectionCamera
import numpy as np
import cv2

logger = logging.Logger("Camera")
url = "http://localhost/internal/logs/"
FRAMES_IN_CYCLE = 6
FRAMES_THRESHOLD = 3
INTERVAL_MS = 250


def send_request(user_id: str, images: list[bytes], food_weight: float) -> None:
    """Send data to the backend about the cat and its food eaten."""
    params = {"user_id": user_id, "food_weight": food_weight}
    files = []
    for img in images:
        files.append(("files_batch", img))

    try:
        response = requests.post(url, params=params, files=files)
        image_ids = response.json()
        logging.info(f"Scucessfully sent images. Image_ids: {image_ids}")
    except HTTPError as e:
        # Server returned an error (e.g., 500, 422, 404)
        logger.warning(f"HTTP error {e.response.status_code}: {e.response.text}")
    except RequestException as e:
        # Network errors, timeouts, etc.
        logging.warning(f"Request failed: {e}")


def start_camera(user_id: str, display: bool = False) -> None:
    """Constantly check the camera to detect cat presence and send info about food weight to backend."""

    camera = CatDetectionCamera()
    weights = WeightsMock(port="/dev/ttyUSB0", baud_rate=115200, timeout=0.1)

    last = None
    prev_weight = None
    cat_is_visible = False

    cnt_cats = 0
    frame_number = 1

    images = []

    while True:
        if display and last:
            camera.display()
        if last and (datetime.now() - last < timedelta(milliseconds=INTERVAL_MS)):
            continue
        weight_delta = None
        current_weight = weights.get_weight()

        prev_cat_here = cat_is_visible

        # Exactly one cat
        cnt_cats += camera.check_cat_presence()

        if frame_number == FRAMES_IN_CYCLE:
            if cnt_cats >= FRAMES_THRESHOLD:
                cat_is_visible = True
            else:
                cat_is_visible = False
                # Cat finished eating
                if prev_weight and current_weight and prev_cat_here:
                    weight_delta = current_weight - prev_weight
                    sz = len(images)
                    images = [images[0], images[sz // 2], images[-1]]
                    # Send API request
                    send_request(
                        user_id=user_id, images=images, food_weight=weight_delta
                    )
                    # Display images sent to the API
                    camera.display_collected_files(images)
                    images = []

                if current_weight:
                    prev_weight = current_weight
            cnt_cats = 0

        frame_number += 1
        frame_number %= FRAMES_IN_CYCLE + 1

        if cat_is_visible:
            success, img = camera.get_image()
            if not success:
                logger.warning("Failed to encode image")
                raise RuntimeError("Failed to encode image")

            images.append(img)

        last = datetime.now()

        if camera.check_close_display():
            break

    camera.stop()


if __name__ == "__main__":
    """
    Usage: python cat_face_detection.py

    Flags:
    -display to display the cam
    --user_id <user_id> to use a specific user_id
    """
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
