import sys
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QLabel
import cv2
import mediapipe as mp
from PyQt6.QtCore import Qt
from face_mesh_utils import LEFT_EYE, RIGHT_EYE, EAR_THRESH, CONSEC_FRAMES, eye_aspect_ratio
import numpy as np

class BlinkCounterThread(QThread):
    blink_count_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True
        self.blink_count = 0

    def run(self):
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        cap = cv2.VideoCapture(0)
        blink_count = 0
        left_counter = 0
        import time
        last_blink_time = 0
        ms_per_frame = 60
        max_blink_frames = int(0.8 * 1000 / ms_per_frame)  # 0.8s max
        while self._running:
            ret, frame = cap.read()
            if not ret:
                continue
            h, w = frame.shape[:2]
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame.flags.writeable = False
            results = face_mesh.process(rgb_frame)
            rgb_frame.flags.writeable = True
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                landmarks = face_landmarks.landmark
                left_ear = eye_aspect_ratio(landmarks, LEFT_EYE, w, h)
                right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE, w, h)
                avg_ear = (left_ear + right_ear) / 2.0
                if avg_ear < EAR_THRESH:
                    left_counter += 1
                else:
                    now = time.time()
                    # Only count as blink if closed for short time and not too soon after previous blink
                    if CONSEC_FRAMES <= left_counter <= max_blink_frames and (now - last_blink_time > 0.2):
                        blink_count += 1
                        self.blink_count_changed.emit(blink_count)
                        last_blink_time = now
                    left_counter = 0
            self.msleep(ms_per_frame)  # ~16 FPS
        cap.release()

    def stop(self):
        self._running = False
        self.wait()

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer

class BlinkCounterLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        self.label = QLabel("Blinks: 0")
        self.label.setStyleSheet("color: #4f8cff; font-size: 18px; font-weight: bold; background: transparent; padding: 6px 18px; border-radius: 16px;")
        self.label.setFixedWidth(120)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dot = QLabel()
        self.dot.setFixedSize(14, 14)
        self.dot.setStyleSheet("background: white; border-radius: 7px; margin-left: 6px;")
        self.dot.setVisible(False)
        layout.addWidget(self.label)
        layout.addWidget(self.dot)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.blink_thread = BlinkCounterThread()
        self.blink_thread.blink_count_changed.connect(self.update_count)
        self.dot_timer = QTimer()
        self.dot_timer.setSingleShot(True)
        self.dot_timer.timeout.connect(self.hide_dot)
        self._blinking = False

    def update_count(self, count):
        self.label.setText(f"Blinks: {count}")
        self.dot.setVisible(True)
        self.dot.raise_()
        self.dot_timer.start(350)

    def hide_dot(self):
        self.dot.setVisible(False)

    def start_blinking(self):
        if not self._blinking:
            self.blink_thread = BlinkCounterThread()
            self.blink_thread.blink_count_changed.connect(self.update_count)
            self.blink_thread.start()
            self._blinking = True

    def stop_blinking(self):
        if self._blinking:
            self.blink_thread.stop()
            self._blinking = False

    def closeEvent(self, event):
        self.stop_blinking()
        event.accept()
