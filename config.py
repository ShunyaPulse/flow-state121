import os
import sys

# --- PYINSTALLER DYNAMIC PATH SETUP ---
if getattr(sys, 'frozen', False):
    # Agar app .exe (software) ki tarah chal rahi hai
    EXE_DIR = os.path.dirname(sys.executable) # .exe file ki real location
    ASSETS_DIR = os.path.join(EXE_DIR, "assets") # 👈 Naya Fix: Seedha bahar wale folder se jodeca
else:
    # Agar VS Code mein normal script ki tarah chal rahi hai
    EXE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(EXE_DIR, "assets")

# --- PATHS ---
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT_IP = "127.0.0.1"

FOCUS_GAMMA_FILE = os.path.join(ASSETS_DIR, "GAMMA WAVES1.wav")      
FOCUS_BETA_FILE = os.path.join(ASSETS_DIR, "BETA WAVES1.wav")        
FOCUS_ALPHA_FILE = os.path.join(ASSETS_DIR, "ALPHA WAVES1.wav")      
ALARM_WAVE_FILE = os.path.join(ASSETS_DIR, "ALARM.wav")
SLOUCH_WAVE_FILE = os.path.join(ASSETS_DIR, "SLOUCH ALERT.wav")

MODEL_FILENAME = os.path.join(ASSETS_DIR, "face_landmarker.task")
# Scorecard humesha wahi banega jahan aapki .exe file rakhi hogi
SUMMARY_LOG_FILE = os.path.join(EXE_DIR, "daily_scorecard_summary.csv")

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
NOSE_TIP = 1
LEFT_EDGE = 234
RIGHT_EDGE = 454
FOREHEAD = 10
CHIN = 152

EAR_THRESHOLD = 0.22
SLEEP_THRESHOLD = 2.0       
DISTRACTION_THRESHOLD = 3.0 
SLOUCH_TIME_THRESHOLD = 3.0 

YAW_LEFT_LIMIT = 0.33       
YAW_RIGHT_LIMIT = 0.67      
PITCH_UP_LIMIT = 0.33       
PITCH_DOWN_LIMIT = 0.75     

SLOUCH_PROXIMITY_LIMIT = 0.33 
SLOUCH_DROP_LIMIT = 0.66