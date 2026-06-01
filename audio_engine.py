import winsound
import os
import time
import datetime
from config import *

# --- THE MAGIC FIX ---
# Yeh variable yaad rakhega ki current mein konsi aawaz baj rahi hai.
# Iski wajah se har frame par aawaz restart nahi hogi aur clear sound aayegi!
_current_playing_state = None

def determine_focus_wave(focus_start_time, enable_brainwaves):
    if not enable_brainwaves: 
        return "SILENT_FOCUS"
        
    now = datetime.datetime.now()
    current_hour, current_minute = now.hour, now.minute
    focus_duration_minutes = (time.time() - focus_start_time) / 60.0
    
    if current_hour >= 20 or current_hour < 3 or (current_hour == 3 and current_minute <= 30): 
        return "FOCUSED_ALPHA"  
    if current_hour >= 17 or focus_duration_minutes >= 25.0: 
        return "FOCUSED_BETA"   
    
    return "FOCUSED_GAMMA"      

def play_audio(state, enable_brainwaves):
    global _current_playing_state
    
    # 1. Agar brainwaves OFF hain, toh focus wali saari states ko silent maan lo
    if not enable_brainwaves and state in ["FOCUSED_GAMMA", "FOCUSED_BETA", "FOCUSED_ALPHA", "POMODORO_BREAK", "SILENT_FOCUS"]:
        actual_target_state = "SILENT_FOCUS"
    else:
        actual_target_state = state

    # 2. THE STUTTER FIX: Agar naya state purane jaisa hi hai, toh audio wapas start mat karo!
    if actual_target_state == _current_playing_state:
        return

    # Update state
    _current_playing_state = actual_target_state

    # 3. Audio Playback Logic
    if actual_target_state == "SILENT_FOCUS":
        winsound.PlaySound(None, winsound.SND_PURGE)
        return

    audio_map = {
        "FOCUSED_GAMMA": FOCUS_GAMMA_FILE, 
        "FOCUSED_BETA": FOCUS_BETA_FILE, 
        "FOCUSED_ALPHA": FOCUS_ALPHA_FILE,
        "POMODORO_BREAK": FOCUS_ALPHA_FILE, 
        "SLEEPING": ALARM_WAVE_FILE, 
        "DISTRACTED": ALARM_WAVE_FILE,
        "SLOUCHING": SLOUCH_WAVE_FILE, 
        "SILENT_FOCUS": None
    }
    
    target_file = audio_map.get(actual_target_state)
    
    if target_file and os.path.exists(target_file): 
        # Loop mein async aawaz bajate raho jab tak state change na ho
        winsound.PlaySound(target_file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
    else:
        # Fallback (Agar .wav file gayab ho jaye toh Windows ki default beep bajegi)
        if actual_target_state in ["SLEEPING", "DISTRACTED", "SLOUCHING"]: 
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP)
        else: 
            winsound.PlaySound(None, winsound.SND_PURGE)