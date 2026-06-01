import os
import sys
import warnings
import contextlib
import subprocess
import cv2
import time

# Suppress system-level logs for a clean public console
os.environ['GLOG_minloglevel'] = '2'          
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'      
warnings.filterwarnings("ignore")             

subprocess.run('cls' if os.name == 'nt' else 'clear', shell=True)

@contextlib.contextmanager
def suppress_stderr():
    fd = sys.stderr.fileno()
    saved_stderr = os.dup(fd)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, fd)
    try:
        yield
    finally:
        os.dup2(saved_stderr, fd)
        os.close(devnull)
        os.close(saved_stderr)

from config import *
from vision_engine import initialize_detector, process_frame 
from audio_engine import play_audio, determine_focus_wave
from iron_dome import engage_iron_dome, disengage_iron_dome

print(r"""
 _____ _                 ____  _        _       
|  ___| | _____      __ / ___|| |_ __ _| |_ ___ 
| |_  | |/ _ \ \ /\ / / \___ \| __/ _` | __/ _ \
|  _| | | (_) \ V  V /   ___) | || (_| | ||  __/
|_|   |_|\___/ \_/\_/   |____/ \__\__,_|\__\___|
""")
print("="*55)
print(" 🚀 THE ULTIMATE FLOW-STATE ENGINE 🚀")
print("="*55)

try:
    work_input = input("Work Duration (minutes) [Press ENTER for 25]: ")
    WORK_MINS = float(work_input) if work_input.strip() else 25.0
    
    break_input = input("Break Duration (minutes) [Press ENTER for 5]: ")
    BREAK_MINS = float(break_input) if break_input.strip() else 5.0
except ValueError:
    print("[INFO] Invalid input. Defaulting to 25 min Work / 5 min Break.")
    WORK_MINS, BREAK_MINS = 25.0, 5.0

PRESET_SITES = {
    1: ["youtube.com", "www.youtube.com"],
    2: ["instagram.com", "www.instagram.com"],
    3: ["facebook.com", "www.facebook.com"],
    4: ["reddit.com", "www.reddit.com"],
    5: ["twitter.com", "www.twitter.com", "x.com"],
    6: ["netflix.com", "www.netflix.com"]
}

print("\n--- Select Websites to Block ---")
print("1. YouTube")
print("2. Instagram")
print("3. Facebook")
print("4. Reddit")
print("5. Twitter / X")
print("6. Netflix")
print("7. Other (Type your own)")
print("8. Block ALL of the above (1-6)")

sites_input = input("Enter choices (e.g. 1,2,7) [Press ENTER to skip blocking]: ")
BLOCKED_SITES = []

if sites_input.strip():
    choices = [c.strip() for c in sites_input.split(",")]

    if "8" in choices:
        for i in range(1, 7):
            BLOCKED_SITES.extend(PRESET_SITES[i])
    else:
        for choice in choices:
            if choice.isdigit():
                c_num = int(choice)
                if c_num in PRESET_SITES:
                    BLOCKED_SITES.extend(PRESET_SITES[c_num])

    if "7" in choices:
        custom_input = input("Enter other websites (comma separated): ")
        if custom_input.strip():
            raw_sites = [s.strip() for s in custom_input.split(",")]
            for site in raw_sites:
                # Custom URLs ko 100% clean karega (https, www, aur trailing slash hata dega)
                clean_site = site.replace("https://", "").replace("http://", "").replace("www.", "").split('/')[0]
                BLOCKED_SITES.append(clean_site)
                BLOCKED_SITES.append(f"www.{clean_site}")

BLOCKED_SITES = list(set(BLOCKED_SITES))

# System ko bata do ki Iron Dome ON rakhna hai ya OFF
ENABLE_IRON_DOME = len(BLOCKED_SITES) > 0

if ENABLE_IRON_DOME:
    print(f"\n[INFO] Iron Dome activated for: {', '.join(BLOCKED_SITES)}")
else:
    print("\n[INFO] Iron Dome skipped. No sites will be blocked.")

# Agar Iron Dome ON hai, tabhi No-Escape puchega, warna default False manega
NO_ESCAPE_MODE = False
if ENABLE_IRON_DOME:
    no_escape_input = input("\nEnable No-Escape Mode? (y/n) [Press ENTER for n]: ").strip().lower()
    NO_ESCAPE_MODE = (no_escape_input == 'y')
    if NO_ESCAPE_MODE:
        print("[INFO] Background Guardian Sleeping Mode Activated!")

# ==========================================
# 👻 GHOST SPAWNER FUNCTION
# ==========================================
def spawn_ghost():
    if NO_ESCAPE_MODE and BLOCKED_SITES:
        target_timestamp = time.time() + (WORK_MINS * 60)
        sites_arg = ",".join(BLOCKED_SITES)
        
        flags = 0x00000008 | 0x00000200 | 0x08000000 # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
        
        # 1. Agar App Public .exe ban chuki hai
        if getattr(sys, 'frozen', False):
            subprocess.Popen(["ghost_blocker.exe", str(target_timestamp), sites_arg], creationflags=flags)
        
        # 2. Agar VS Code/CMD se chal rahi hai
        else:
            if sys.platform == "win32":
                python_path = sys.executable.replace("python.exe", "pythonw.exe")
                subprocess.Popen([python_path, "ghost_blocker.py", str(target_timestamp), sites_arg], creationflags=flags)
            else:
                subprocess.Popen([sys.executable, "ghost_blocker.py", str(target_timestamp), sites_arg])
if NO_ESCAPE_MODE:
    print("[INFO] Background Guardian Sleeping Mode Activated!")

ENABLE_POMODORO = True
ENABLE_WEBCAM_TRACKING = True
ENABLE_BRAINWAVES = True
ENABLE_POSTURE = True

print("\n[INFO] Starting Camera and AI Vision Engine (Silently)...")
cap = cv2.VideoCapture(0)

with suppress_stderr():
    detector = initialize_detector()

session_stats = {"work_sessions": 1, "distractions": 0, "sleep_warnings": 0, "slouch_warnings": 0}
last_state = "STARTING"  # 👈 Yeh line add kijiye taaki hum pichla state yaad rakh sakein
pomo_start_time = time.time()
pomo_state = "WORK"
current_state = "STARTING"
is_paused = False
time_elapsed_pomo = 0.0

engage_iron_dome(ENABLE_IRON_DOME, BLOCKED_SITES)
wave_state = determine_focus_wave(pomo_start_time, ENABLE_BRAINWAVES)
play_audio(wave_state, ENABLE_BRAINWAVES)
spawn_ghost() # Spawn ghost for the first session

try:
    while True:
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.flip(frame, 1)

        if not is_paused:
            time_elapsed_pomo = (time.time() - pomo_start_time) / 60.0
        else:
            pomo_start_time = time.time() - (time_elapsed_pomo * 60.0)

        remaining_time_sec = 0
        mins_left = 0
        secs_left = 0

        if ENABLE_POMODORO:
            if pomo_state == "WORK":
                remaining_time_sec = (WORK_MINS * 60) - (time.time() - pomo_start_time)
                if remaining_time_sec <= 0:
                    pomo_state = "BREAK"
                    pomo_start_time = time.time()
                    disengage_iron_dome(BLOCKED_SITES)
                    play_audio("POMODORO_BREAK", ENABLE_BRAINWAVES)
            else:
                remaining_time_sec = (BREAK_MINS * 60) - (time.time() - pomo_start_time)
                if remaining_time_sec <= 0:
                    pomo_state = "WORK"
                    pomo_start_time = time.time()
                    session_stats["work_sessions"] += 1
                    engage_iron_dome(ENABLE_IRON_DOME, BLOCKED_SITES)
                    spawn_ghost() # Spawn ghost for subsequent sessions
                    wave_state = determine_focus_wave(pomo_start_time, ENABLE_BRAINWAVES)
                    play_audio(wave_state, ENABLE_BRAINWAVES)
            
            if remaining_time_sec > 0:
                mins_left = int(remaining_time_sec // 60)
                secs_left = int(remaining_time_sec % 60)

        if ENABLE_WEBCAM_TRACKING and not is_paused and pomo_state == "WORK":
            current_state = process_frame(frame, detector) 

            # ======================================================================
            # 📊 STATE CHANGE TRACKER: Prevents counter from spamming on every frame
            # ======================================================================
            if current_state != last_state:
                if current_state == "SLEEPING":
                    session_stats["sleep_warnings"] += 1
                elif current_state == "DISTRACTED":
                    session_stats["distractions"] += 1
                elif current_state == "SLOUCHING":
                    session_stats["slouch_warnings"] += 1
                
                last_state = current_state  # 👈 State ko sync kar lijiye
            # ======================================================================
            
            if current_state in ["SLEEPING", "DISTRACTED", "SLOUCHING"]:
                play_audio(current_state, ENABLE_BRAINWAVES)
            elif current_state == "FOCUSED_GAMMA" or current_state == "FOCUSED":
                wave_state = determine_focus_wave(pomo_start_time, ENABLE_BRAINWAVES)
                play_audio(wave_state, ENABLE_BRAINWAVES)

        color = (0, 255, 0)
        ui_text = f"STATE: {current_state}"
        
        if is_paused:
            ui_text = "STATE: PAUSED"
            color = (0, 255, 255) 
        elif pomo_state == "BREAK": 
            color = (255, 175, 200)
        elif current_state in ["SLEEPING", "DISTRACTED", "SLOUCHING"]:
            color = (0, 0, 255) 

        if ENABLE_POMODORO:
            ui_text += f" | {pomo_state}: {mins_left:02d}:{secs_left:02d}"

        cv2.putText(frame, ui_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        p_stat = "ON" if ENABLE_POMODORO else "OFF"
        w_stat = "ON" if ENABLE_WEBCAM_TRACKING else "OFF"
        b_stat = "ON" if ENABLE_BRAINWAVES else "OFF"
        s_stat = "ON" if ENABLE_POSTURE else "OFF"
        
        hotkey_text = f"[P] Pomo: {p_stat} | [W] Cam: {w_stat} | [B] Waves: {b_stat} | [S] Posture: {s_stat} | [SPACE] Pause"
        cv2.putText(frame, hotkey_text, (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 255, 255), 1)

        cv2.imshow("Flow-State Engine", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
        elif key in [ord('p'), ord('P')]: 
            ENABLE_POMODORO = not ENABLE_POMODORO
        elif key in [ord('w'), ord('W')]: 
            ENABLE_WEBCAM_TRACKING = not ENABLE_WEBCAM_TRACKING
        elif key in [ord('b'), ord('B')]: 
            ENABLE_BRAINWAVES = not ENABLE_BRAINWAVES
            if not ENABLE_BRAINWAVES: play_audio("SILENT_FOCUS", False)
            elif not is_paused: play_audio(determine_focus_wave(pomo_start_time, True) if pomo_state == "WORK" else "POMODORO_BREAK", True)
        elif key in [ord('s'), ord('S')]: 
            ENABLE_POSTURE = not ENABLE_POSTURE
        elif key == 32: 
            is_paused = not is_paused 
            if is_paused:
                play_audio("SILENT_FOCUS", False)
            else:
                play_audio(determine_focus_wave(pomo_start_time, True) if pomo_state == "WORK" else "POMODORO_BREAK", True)

except KeyboardInterrupt:
    print("\n[WARNING] App manually stopped!")

finally:
    if 'detector' in locals():
        try:
            detector.close()
        except Exception:
            pass

    cap.release()
    cv2.destroyAllWindows()
    play_audio("SILENT_FOCUS", False)

    # ==========================================
    # 📊 AUTOMATIC SCORECARD SAVING LOGIC
    # ==========================================
    try:
        import csv
        from datetime import datetime
        
        file_exists = os.path.exists(SUMMARY_LOG_FILE)
        
        with open(SUMMARY_LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Agar file pehli baar ban rahi hai, toh headers daal do
            if not file_exists:
                writer.writerow(["Timestamp", "Work Sessions", "Distractions Count", "Sleep Warnings", "Slouch Warnings"])
            
            # Data write karo
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                session_stats["work_sessions"] if pomo_state == "WORK" else session_stats["work_sessions"] - 1,
                session_stats["distractions"],
                session_stats["sleep_warnings"],
                session_stats["slouch_warnings"]
            ])
        print("[INFO] Daily scorecard updated successfully in daily_scorecard_summary.csv! 📈")
    except Exception as e:
        print(f"[WARNING] Could not save scorecard: {e}")

    # ==========================================
    # Clean Exit Logic
    # ==========================================
    if not NO_ESCAPE_MODE or pomo_state == "BREAK":
        if ENABLE_IRON_DOME:
            print("[INFO] Normal Exit / Work Completed. Disengaging Iron Dome immediately...")
            disengage_iron_dome(BLOCKED_SITES)
            print("[INFO] Flow-State Engine closed safely. All sites UNBLOCKED. ✅")
        else:
            print("[INFO] Normal Exit / Work Completed.")
            print("[INFO] Flow-State Engine closed safely.")
    else:
        print("\n🚨 [NO-ESCAPE MODE ACTIVE] 🚨")
        print("Program closed during Work Session. Websites remain BLOCKED.")
        print("The Ghost Process is sleeping in the background and will unblock exactly when the timer hits zero!")