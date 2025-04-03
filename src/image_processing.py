import os
import cv2
import cvzone
import numpy as np
from src.config import WIDTH, HEIGHT, OCCUPANCY_THRESHOLD
from tkinter import messagebox  # Add this import for error messages

class ParkingMonitor:
    def __init__(self, pos_list, database):
        self.pos_list = pos_list
        self.database = database

    def check_spaces(self, img_thres, img):
        """Check parking spaces and mark them as free/occupied."""
        spaces = 0
        for i, pos in enumerate(self.pos_list):
            x, y = pos
            img_crop = img_thres[y:y + HEIGHT, x:x + WIDTH]
            count = cv2.countNonZero(img_crop)
            color = (0, 200, 0) if count < OCCUPANCY_THRESHOLD else (0, 0, 200)
            thickness = 2 if count < OCCUPANCY_THRESHOLD else 1
            if count < OCCUPANCY_THRESHOLD:
                spaces += 1
            cv2.rectangle(img, (x, y), (x + WIDTH, y + HEIGHT), color, thickness)
            cvzone.putTextRect(img, str(i + 1), (x + 5, y + 20), scale=1, thickness=1)
        return spaces

    def monitor_parking(self, source, camera_id):
        """Monitor parking spaces using the specified video source."""
        if "Camera" in source:
            camera_index = int(source.split("Camera ")[1].split(" ")[0])
            cap = cv2.VideoCapture(camera_index)
        else:
            if not os.path.exists(source):
                messagebox.showerror("Error", f"Video file not found: {source}")
                return False
            cap = cv2.VideoCapture(source)

        fps = cap.get(cv2.CAP_PROP_FPS)
        while True:
            success, img = cap.read()
            if not success:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # Image processing
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
            img_thres = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY_INV, 25, 16)
            img_thres = cv2.medianBlur(img_thres, 5)
            kernel = np.ones((3, 3), np.uint8)
            img_thres = cv2.dilate(img_thres, kernel, iterations=1)

            # Check spaces
            spaces = self.check_spaces(img_thres, img)

            # Display information
            cvzone.putTextRect(img, f'Free: {spaces}/{len(self.pos_list)}', (50, 60), thickness=2, offset=10,
                              colorR=(0, 200, 0) if spaces > 0 else (0, 0, 200))
            cvzone.putTextRect(img, f'FPS: {int(fps)}', (50, 100), scale=1, thickness=1)
            cvzone.putTextRect(img, f'Camera: {camera_id}', (50, 140), scale=1, thickness=1)

            # Log data to database
            self.database.log_monitoring_data(camera_id, spaces, len(self.pos_list))

            cv2.imshow(f"Parking Monitor - Camera {camera_id}", img)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p'):
                cv2.waitKey(-1)

        cap.release()
        cv2.destroyWindow(f"Parking Monitor - Camera {camera_id}")
        return True