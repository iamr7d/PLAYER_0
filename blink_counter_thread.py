from PyQt6.QtCore import QThread, pyqtSignal
import cv2
import mediapipe as mp
import numpy as np
import time

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [263, 387, 385, 362, 380, 373]

def calculate_ear(eye_landmarks):
    A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
    B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
    C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
    ear = (A + B) / (2.0 * C)
    return ear

def normalize_lighting(frame):
    yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
    yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
    return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)


class BlinkCounterThread(QThread):
    blink_count_changed = pyqtSignal(int)
    calibration_complete = pyqtSignal(float)

    def __init__(self, log_base_name="blink_log", movie_name="", user_name=None, parent=None):
        super().__init__(parent)
        self._running = True
        self.blink_count = 0
        self.blink_threshold = 0.22
        self.log_base_name = log_base_name
        self.movie_name = movie_name
        self.user_name = user_name

    def run(self):
        import csv
        import os
        from datetime import datetime, timedelta
        cap = cv2.VideoCapture(0)
        blink_count = self.blink_count  # Start from the last known count
        closed_frames = 0
        consecutive_frames = 2
        ear_history = []
        max_history = 5
        csv_dir = os.path.join(os.getcwd(), 'csv')
        os.makedirs(csv_dir, exist_ok=True)
        log_path = os.path.join(csv_dir, f'{self.log_base_name}.csv')
        log_header = ['real_time_12h', 'elapsed_hms', 'blink_count']
        start_time = datetime.now()
        # Write header if file doesn't exist
        if not os.path.exists(log_path):
            with open(log_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(log_header)
        real_time_log_path = os.path.join(os.getcwd(), 'csv', 'realtime', 'realtime_log.csv')
        real_time_log_header = ['real_time', 'elapsed_time', 'blink_count', 'movie_name']
        # Write header if file doesn't exist
        if not os.path.exists(real_time_log_path):
            with open(real_time_log_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(real_time_log_header)
        with mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        ) as face_mesh:
            # Get initial frame size for calibration
            ret, frame = cap.read()
            if not ret:
                return
            ih, iw, _ = frame.shape
            self.blink_threshold = self.calibrate_ear(face_mesh, cap, iw, ih)
            self.calibration_complete.emit(self.blink_threshold)
            while self._running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                frame = normalize_lighting(frame)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(rgb_frame)
                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        left_eye = np.array([(int(face_landmarks.landmark[i].x * iw), int(face_landmarks.landmark[i].y * ih)) for i in LEFT_EYE])
                        right_eye = np.array([(int(face_landmarks.landmark[i].x * iw), int(face_landmarks.landmark[i].y * ih)) for i in RIGHT_EYE])
                        left_ear = calculate_ear(left_eye)
                        right_ear = calculate_ear(right_eye)
                        ear = (left_ear + right_ear) / 2.0
                        ear_history.append(ear)
                        if len(ear_history) > max_history:
                            ear_history.pop(0)
                        smooth_ear = np.median(ear_history)
                        if smooth_ear < self.blink_threshold:
                            closed_frames += 1
                        else:
                            if closed_frames >= consecutive_frames:
                                blink_count += 1
                                self.blink_count = blink_count
                                self.blink_count_changed.emit(blink_count)
                                # Log to CSV
                                now = datetime.now()
                                elapsed = now - start_time
                                elapsed_hms = str(timedelta(seconds=int(elapsed.total_seconds())))
                                real_time_12h = now.strftime('%I:%M:%S %p')
                                # Read all rows, replace any with matching elapsed_hms, else append
                                import csv
                                import os
                                rows = []
                                replaced = False
                                if os.path.exists(log_path):
                                    with open(log_path, 'r', newline='') as f:
                                        reader = list(csv.reader(f))
                                        header = reader[0] if reader else []
                                        rows = reader[1:] if len(reader) > 1 else []
                                # Replace any row with the same elapsed_hms
                                for i, row in enumerate(rows):
                                    if len(row) > 1 and row[1] == elapsed_hms:
                                        rows[i] = [real_time_12h, elapsed_hms, blink_count]
                                        replaced = True
                                        break
                                if not replaced:
                                    rows.append([real_time_12h, elapsed_hms, blink_count])
                                # Write header and all rows
                                with open(log_path, 'w', newline='') as f:
                                    writer = csv.writer(f)
                                    if header:
                                        writer.writerow(header)
                                    writer.writerows(rows)
                                # Upload to Firebase in real time
                                from firebase_upload import upload_viewer_log
                                import re
                                def clean_movie_name(name):
                                    name = re.sub(r'\.[^.]+$', '', name)
                                    name = re.sub(r'[._]+', ' ', name)
                                    match_year = re.search(r'(19|20)\d{2}', name)
                                    cut_idx = match_year.end() if match_year else None
                                    if cut_idx:
                                        name = name[:cut_idx]
                                    # Remove trailing | and spaces
                                    name = re.sub(r'[|]+$', '', name)
                                    name = re.sub(r'[^\w\s]+$', '', name)
                                    name = re.sub(r'\s+', ' ', name).strip()
                                    return name.title()
                                import os
                                filename_only = os.path.basename(self.movie_name) if self.movie_name else ""
                                movie_name = clean_movie_name(filename_only) if filename_only else 'Unknown'
                                upload_viewer_log(blink_count, elapsed_hms, now.strftime('%Y-%m-%d %H:%M:%S'), movie_name, self.user_name)

                            closed_frames = 0
                time.sleep(0.05)
        cap.release()

    def calibrate_ear(self, face_mesh, cap, iw, ih):
        closed_ears = []
        for _ in range(20):
            ret, frame = cap.read()
            if not ret:
                continue
            frame = normalize_lighting(frame)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                left_eye = np.array([(int(face_landmarks.landmark[i].x * iw), int(face_landmarks.landmark[i].y * ih)) for i in LEFT_EYE])
                right_eye = np.array([(int(face_landmarks.landmark[i].x * iw), int(face_landmarks.landmark[i].y * ih)) for i in RIGHT_EYE])
                ear = (calculate_ear(left_eye) + calculate_ear(right_eye)) / 2.0
                closed_ears.append(ear)
        open_ears = []
        for _ in range(20):
            ret, frame = cap.read()
            if not ret:
                continue
            frame = normalize_lighting(frame)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                left_eye = np.array([(int(face_landmarks.landmark[i].x * iw), int(face_landmarks.landmark[i].y * ih)) for i in LEFT_EYE])
                right_eye = np.array([(int(face_landmarks.landmark[i].x * iw), int(face_landmarks.landmark[i].y * ih)) for i in RIGHT_EYE])
                ear = (calculate_ear(left_eye) + calculate_ear(right_eye)) / 2.0
                open_ears.append(ear)
        closed_mean = np.median(closed_ears) if closed_ears else 0.18
        open_mean = np.median(open_ears) if open_ears else 0.3
        blink_threshold = (closed_mean + open_mean) / 2.2
        return blink_threshold

    def stop(self):
        self._running = False
        self.wait()
