import math

# Eye landmark indices for MediaPipe Face Mesh (left and right)
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
EAR_THRESH = 0.21    # Threshold for blink detection
CONSEC_FRAMES = 2    # Number of consecutive frames for a blink

def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def eye_aspect_ratio(landmarks, eye_indices, image_w, image_h):
    # 6 points: [0, 1, 2, 3, 4, 5] around the eye
    p = [(int(landmarks[idx].x * image_w), int(landmarks[idx].y * image_h)) for idx in eye_indices]
    # EAR formula
    A = euclidean_distance(p[1], p[5])
    B = euclidean_distance(p[2], p[4])
    C = euclidean_distance(p[0], p[3])
    ear = (A + B) / (2.0 * C)
    return ear
