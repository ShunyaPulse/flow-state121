import math
import os
import urllib.request
import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from config import *

# --- STATE TRACKERS FOR VISION ENGINE ---
vision_timers = {
    "eyes_closed_start": None,
    "distracted_start": None,
    "slouch_start": None
}

def initialize_detector():
    if not os.path.exists(MODEL_FILENAME):
        print(f"\n[INFO] Downloading AI Face Model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_FILENAME)
    
    base_options = python.BaseOptions(model_asset_path=MODEL_FILENAME)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options, 
        num_faces=1, 
        min_face_detection_confidence=0.5, 
        min_tracking_confidence=0.5
    )
    return vision.FaceLandmarker.create_from_options(options)

def euclidean_distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def calculate_ear(eye_landmarks):
    v1 = euclidean_distance(eye_landmarks[1], eye_landmarks[5])
    v2 = euclidean_distance(eye_landmarks[2], eye_landmarks[4])
    h = euclidean_distance(eye_landmarks[0], eye_landmarks[3])
    return (v1 + v2) / (2.0 * h)

def process_frame(frame, detector):
    """
    Frame ko process karke Sleep, Distraction aur Slouch check karta hai.
    """
    # 1. Prepare image for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # 2. Detect Face Landmarks
    result = detector.detect(mp_image)
    
    if not result.face_landmarks:
        return "NO_FACE"
        
    landmarks = result.face_landmarks[0]
    current_time = time.time()
    
    # ==========================================
    # A. SLEEP DETECTION (EAR Check)
    # ==========================================
    left_eye_points = [landmarks[i] for i in LEFT_EYE]
    right_eye_points = [landmarks[i] for i in RIGHT_EYE]
    
    avg_ear = (calculate_ear(left_eye_points) + calculate_ear(right_eye_points)) / 2.0
    
    if avg_ear < EAR_THRESHOLD:
        if vision_timers["eyes_closed_start"] is None:
            vision_timers["eyes_closed_start"] = current_time
        elif (current_time - vision_timers["eyes_closed_start"]) > SLEEP_THRESHOLD:
            return "SLEEPING"
    else:
        vision_timers["eyes_closed_start"] = None

    # ==========================================
    # B. DISTRACTION DETECTION (Head Pose Check)
    # ==========================================
    nose = landmarks[NOSE_TIP]
    left_edge = landmarks[LEFT_EDGE]
    right_edge = landmarks[RIGHT_EDGE]
    forehead = landmarks[FOREHEAD]
    chin = landmarks[CHIN]
    
    # Calculate relative position (Yaw & Pitch)
    yaw = (nose.x - left_edge.x) / (right_edge.x - left_edge.x + 1e-6)
    pitch = (nose.y - forehead.y) / (chin.y - forehead.y + 1e-6)
    
    is_distracted = (yaw < YAW_LEFT_LIMIT or yaw > YAW_RIGHT_LIMIT or 
                     pitch < PITCH_UP_LIMIT or pitch > PITCH_DOWN_LIMIT)
                     
    if is_distracted:
        if vision_timers["distracted_start"] is None:
            vision_timers["distracted_start"] = current_time
        elif (current_time - vision_timers["distracted_start"]) > DISTRACTION_THRESHOLD:
            return "DISTRACTED"
    else:
        vision_timers["distracted_start"] = None

    # ==========================================
    # C. SLOUCH DETECTION (Posture Check)
    # ==========================================
    face_height = chin.y - forehead.y
    # Agar chehra camera ke bohot paas aa jaye ya screen mein bohot neeche chala jaye
    is_slouching = (face_height > SLOUCH_PROXIMITY_LIMIT) or (nose.y > SLOUCH_DROP_LIMIT)
    
    if is_slouching:
        if vision_timers["slouch_start"] is None:
            vision_timers["slouch_start"] = current_time
        elif (current_time - vision_timers["slouch_start"]) > SLOUCH_TIME_THRESHOLD:
            return "SLOUCHING"
    else:
        vision_timers["slouch_start"] = None

    # Agar sab theek hai toh user Focused hai
    return "FOCUSED"