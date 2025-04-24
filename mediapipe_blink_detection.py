import cv2
import mediapipe as mp
import math
import time
import numpy as np
import sys
from attention_plotter_qtgraph import AttentionPlotterQtGraph
from PyQt6.QtWidgets import QApplication

# Eye landmark indices for MediaPipe Face Mesh (left and right)
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
# Iris center indices (MediaPipe FaceMesh)
LEFT_IRIS_CENTER = 468
RIGHT_IRIS_CENTER = 473
# Head pose indices (nose, eyes, mouth, chin)
POSE_LANDMARKS = [1, 33, 263, 61, 291, 199]  # nose tip, left eye, right eye, left mouth, right mouth, chin
EAR_THRESH = 0.21    # Tuned threshold for blink detection
CONSEC_FRAMES = 2    # Number of consecutive frames for a blink
MAX_BLINK_FRAMES = 8 # If eyes closed for more than this, don't count as blink

def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def eye_aspect_ratio(landmarks, eye_indices, image_w, image_h):
    # 6 points: [0, 1, 2, 3, 4, 5] around the eye
    pts = [(int(landmarks[i].x * image_w), int(landmarks[i].y * image_h)) for i in eye_indices]
    # EAR calculation
    A = euclidean_distance(pts[1], pts[5])
    B = euclidean_distance(pts[2], pts[4])
    C = euclidean_distance(pts[0], pts[3])
    ear = (A + B) / (2.0 * C)
    return ear

mp_face_mesh = mp.solutions.face_mesh

cap = cv2.VideoCapture(0)
with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7) as face_mesh:
    blink_count = 0
    left_counter = 0
    eye_closed_start = None
    last_blink_time = 0
    min_blink_time = 0.10  # 0.1s (100ms)
    max_blink_time = 0.40  # 0.4s (400ms)
    long_closure_time = 0.80  # 0.8s
    drowsy_time = 1.5        # 1.5s
    min_blink_gap = 0.20     # 0.2s between blinks (eye must stay open)
    ms_per_frame = 1/16
    eye_closed = False
    eye_open_since = None
    in_long_closure = False
    # --- Start AttentionPlotter ---
    app = QApplication.instance() or QApplication(sys.argv)
    plotter = AttentionPlotterQtGraph(max_points=600)
    plotter.show()  # Ensure dashboard window is visible
    script_start = time.time()
    last_yaw = 0
    # For blink rate and durations
    blink_times = []
    closure_durations = []
    distraction_durations = []
    distraction_start = None
    last_state = None
    last_blink_rate = 0
    last_closure_duration = 0
    last_distraction_duration = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        blink_rate = last_blink_rate
        closure_duration = last_closure_duration
        distraction_duration = last_distraction_duration
        h, w = frame.shape[:2]
        # --- Lighting normalization ---
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray_eq = clahe.apply(gray)
        frame_clahe = cv2.cvtColor(gray_eq, cv2.COLOR_GRAY2BGR)
        # Use enhanced frame for detection
        rgb_frame = cv2.cvtColor(frame_clahe, cv2.COLOR_BGR2RGB)
        # --- Brightness check ---
        brightness = np.mean(gray)
        LOW_LIGHT_THRESH = 55
        low_light = brightness < LOW_LIGHT_THRESH
        results = face_mesh.process(rgb_frame)
        attention_state = "Attentive"
        distraction_timer = getattr(attention_state, 'distraction_timer', 0)
        head_not_focused = False
        # --- Detection failure smoothing ---
        if not hasattr(locals(), 'fail_counter'):
            fail_counter = 0
        if not hasattr(locals(), 'ear_buffer'):
            ear_buffer = []
        if not hasattr(locals(), 'gaze_buffer'):
            gaze_buffer = []
        if low_light:
            attention_state = "Low Light"
            cv2.putText(frame, "Low Light: Detection Unreliable", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            plot_time = time.time() - script_start
            blink_rate = blink_rate if hasattr(locals(), 'blink_rate') else 0
            closure_duration = closure_duration if hasattr(locals(), 'closure_duration') else 0
            distraction_duration = distraction_duration if hasattr(locals(), 'distraction_duration') else 0
            plotter.add_point(
                plot_time,
                0,
                0,
                0,
                attention_state,
                blink_rate,
                closure_duration,
                distraction_duration
            )
            cv2.putText(frame, f"Attention: {attention_state}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow('MediaPipe Blink Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue
        if results.multi_face_landmarks:
            fail_counter = 0
            face_landmarks = results.multi_face_landmarks[0]
            landmarks = face_landmarks.landmark
            left_ear = eye_aspect_ratio(landmarks, LEFT_EYE, w, h)
            right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE, w, h)
            avg_ear = (left_ear + right_ear) / 2.0
            # --- Smoothing ---
            ear_buffer.append(avg_ear)
            if len(ear_buffer) > 5:
                ear_buffer.pop(0)
            smooth_ear = sum(ear_buffer) / len(ear_buffer)

            # --- Gaze direction ---
            left_eye_pts = [landmarks[i] for i in LEFT_EYE]
            right_eye_pts = [landmarks[i] for i in RIGHT_EYE]
            left_iris = landmarks[LEFT_IRIS_CENTER]
            right_iris = landmarks[RIGHT_IRIS_CENTER]
            def gaze_ratio(eye_pts, iris, w, h):
                x0 = int(eye_pts[0].x * w)
                x1 = int(eye_pts[3].x * w)
                ix = int(iris.x * w)
                return (ix - x0) / (x1 - x0 + 1e-6)  # normalized
            gaze_left = gaze_ratio(left_eye_pts, left_iris, w, h)
            gaze_right = gaze_ratio(right_eye_pts, right_iris, w, h)
            gaze_val = (gaze_left + gaze_right) / 2.0
            gaze_buffer.append(gaze_val)
            if len(gaze_buffer) > 5:
                gaze_buffer.pop(0)
            smooth_gaze = sum(gaze_buffer) / len(gaze_buffer)
            gaze_centered = 0.25 < smooth_gaze < 0.75

            # --- Head pose estimation ---
            image_points = np.array([
                [landmarks[i].x * w, landmarks[i].y * h] for i in POSE_LANDMARKS
            ], dtype=np.float64)
            # 3D model points for generic face (approximate)
            model_points = np.array([
                [0.0, 0.0, 0.0],         # Nose tip
                [-30.0, -30.0, -30.0],   # Left eye
                [30.0, -30.0, -30.0],    # Right eye
                [-30.0, 30.0, -30.0],    # Left mouth
                [30.0, 30.0, -30.0],     # Right mouth
                [0.0, 60.0, -50.0]       # Chin
            ], dtype=np.float64)
            focal_length = w
            camera_center = (w / 2, h / 2)
            camera_matrix = np.array([
                [focal_length, 0, camera_center[0]],
                [0, focal_length, camera_center[1]],
                [0, 0, 1]
            ], dtype=np.float64)
            dist_coeffs = np.zeros((4, 1))
            try:
                success, rotation_vector, translation_vector = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
                rmat, _ = cv2.Rodrigues(rotation_vector)
                pose_angles, _ = cv2.RQDecomp3x3(rmat)
                yaw = pose_angles[1]
                pitch = pose_angles[0]
                if abs(yaw) > 25 or abs(pitch) > 20:
                    head_not_focused = True
            except Exception:
                head_not_focused = False
                yaw = last_yaw

            # --- Send to plotter ---
            plot_time = time.time() - script_start
            plotter.add_point(
                plot_time,
                smooth_ear,
                smooth_gaze,
                float(yaw),
                attention_state,
                blink_rate,
                closure_duration,
                distraction_duration
            )
            
            
            

            # --- Blink, closure, drowsiness ---
            now = time.time()
            if avg_ear < EAR_THRESH:
                if not eye_closed:
                    eye_closed = True
                    eye_closed_start = now
                    in_long_closure = False
                else:
                    closed_duration = now - eye_closed_start
                    if closed_duration > drowsy_time:
                        attention_state = "Sleeping"
                    elif closed_duration > long_closure_time:
                        attention_state = "Drowsy"
            else:
                if eye_closed:
                    closed_duration = now - eye_closed_start
                    if (min_blink_time <= closed_duration <= max_blink_time) and (eye_open_since is None or (now - eye_open_since) > min_blink_gap):
                        blink_count += 1
                        last_blink_time = now
                        blink_times.append(now)
                        closure_durations.append(closed_duration * 1000.0)  # ms
                    elif closed_duration > long_closure_time:
                        closure_durations.append(closed_duration * 1000.0)
                    eye_closed = False
                    eye_closed_start = None
                    eye_open_since = now

            # --- Attention state logic ---
            if not gaze_centered:
                if distraction_start is None:
                    distraction_start = now
                distraction_timer += ms_per_frame
                if distraction_timer > 2:
                    attention_state = "Distracted"
            else:
                if distraction_start is not None:
                    distraction_durations.append(now - distraction_start)
                    distraction_start = None
                distraction_timer = 0
            if head_not_focused:
                attention_state = "Not Focused"
            if attention_state == "Attentive" and not (avg_ear > EAR_THRESH and gaze_centered and not head_not_focused):
                attention_state = "Attentive"  # fallback

            # --- Rolling blink rate (blinks/min, 60s window) ---
            blink_times = [t for t in blink_times if now - t <= 60]
            blink_rate = len(blink_times)
            # --- Closure duration (ms, last event) ---
            closure_duration = closure_durations[-1] if closure_durations else 0
            # --- Distraction duration (s, last event) ---
            distraction_duration = distraction_durations[-1] if distraction_durations else 0
            last_blink_rate = blink_rate
            last_closure_duration = closure_duration
            last_distraction_duration = distraction_duration

            # Draw overlays
            cv2.putText(frame, f'Blinks: {blink_count}', (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Attention: {attention_state}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        else:
            # Detection failed
            fail_counter += 1
            if fail_counter < 5:
                # Keep last known state and overlay
                try:
                    last_state
                except NameError:
                    last_state = "Not Present"
                attention_state = last_state
                cv2.putText(frame, "Detection Lost: Holding State", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 255), 2)
                cv2.putText(frame, f"Attention: {attention_state}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 255), 2)
            else:
                attention_state = "Not Present"
                cv2.putText(frame, "NO FACE", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, f"Attention: {attention_state}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            plot_time = time.time() - script_start
            plotter.add_point(
                plot_time,
                0,
                0,
                0,
                attention_state,
                blink_rate,
                closure_duration,
                distraction_duration
            )
        cv2.imshow('MediaPipe Blink Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    plotter.close()
    app.exec()  # Start Qt event loop so dashboard stays open
