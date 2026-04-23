import cv2
import numpy as np


class CatDetectionCamera:
    """Class to check that cat face is present in the image."""

    def __init__(self, camera_index: int = 0) -> None:
        # Start video capture from the webcam
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

        self.cat_face_cascade = cv2.CascadeClassifier(
            "haarcascade/haarcascade_frontalcatface_extended.xml"
        )  # Use custom path for cat face cascade
        self.smile_cascade = cv2.CascadeClassifier(
            "haarcascade/haarcascade_smile.xml"
        )  # Use custom path for smile cascade

        self._curr_frame = self.cap.read()[1]

    def check_cat_presence(self) -> bool:
        """Check if the image contains exactly 1 cat face."""
        # Read from the cam
        ret, self._curr_frame = self.cap.read()

        # Convert the frame to grayscale (Haar cascades work on grayscale images)
        self.gray = cv2.cvtColor(self._curr_frame, cv2.COLOR_BGR2GRAY)

        # Detect cat faces in the image
        self.cat_faces = self.cat_face_cascade.detectMultiScale(
            self.gray, scaleFactor=1.3, minNeighbors=5
        )

        # Exactly one cat in the image
        return len(self.cat_faces) == 1

    def get_image(self) -> tuple[bool, bytes]:
        """Get last taken image."""
        # Convert RGB to BGR for correct colors
        bgr_array = cv2.cvtColor(self._curr_frame, cv2.COLOR_RGB2BGR)
        success, encoded_img = cv2.imencode(".jpg", bgr_array)

        return (success, encoded_img.tobytes())

    def display(self) -> None:
        """Display last taken image with cat's face on it."""
        # Loop through all cat faces detected
        # Usually should be one face
        for x, y, w, h in self.cat_faces:
            # Draw rectangle around the cat face
            cv2.rectangle(self._curr_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Region of interest for detecting smiles (mouth area)
            roi_gray = self.gray[y : y + h, x : x + w]
            roi_color = self._curr_frame[y : y + h, x : x + w]

            # Detect smiles in the cat face region
            smiles = self.smile_cascade.detectMultiScale(roi_gray, 1.8, 20)

            # Loop through all smiles detected
            for sx, sy, sw, sh in smiles:
                # Draw rectangle around the smile
                cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow("Cat Face and Smile Detection", self._curr_frame)

    def display_collected_files(self, images: list[bytes]):
        # display images here
        for idx, img_bytes in enumerate(images):
            img_array = cv2.imdecode(
                np.frombuffer(img_bytes, np.uint8),
                cv2.IMREAD_COLOR
            )
            if img_array is not None:
                cv2.imshow(f"Image {idx}", img_array)

    def check_close_display(self) -> bool:
        """Break the loop when the user presses 'q'."""
        return cv2.waitKey(1) & 0xFF == ord("q")

    def stop(self) -> None:
        """Release the webcam and close the window."""
        self.cap.release()
        cv2.destroyAllWindows()
