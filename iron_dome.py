import os
import subprocess
from config import HOSTS_PATH, REDIRECT_IP

def flush_dns():
    """Windows ki memory saaf karne ke liye taaki purani sites cache se na khulein"""
    try:
        if os.name == 'nt': 
            CREATE_NO_WINDOW = 0x08000000
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True, creationflags=CREATE_NO_WINDOW)
    except Exception:
        pass

def is_browser_running():
    """Check karta hai ki kya koi bhi major internet browser currently open hai."""
    if os.name != 'nt': return False
    try:
        CREATE_NO_WINDOW = 0x08000000
        output = subprocess.check_output(
            'tasklist',
            shell=True,
            creationflags=CREATE_NO_WINDOW,
            text=True
        ).lower()
        
        browsers = ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe"]
        
        for browser in browsers:
            if browser in output:
                return True
                
        return False
    except Exception:
        return False

def engage_iron_dome(enable_iron_dome, blocked_sites):
    if not enable_iron_dome or not blocked_sites: return
    
    while is_browser_running():
        print("\n⚠️ [WARNING] Your Internet Browser is running! Please close all browser windows to apply the block perfectly.")
        input("Press ENTER after completely closing the Internet Browser to start your session...")
        
    try:
        with open(HOSTS_PATH, 'r+') as file:
            content = file.read()
            
            if content and not content.endswith('\n'):
                file.write('\n')
                
            for site in blocked_sites:
                if site not in content: 
                    file.write(f"{REDIRECT_IP} {site}\n")
        
        flush_dns()
        
    except PermissionError:
        print("\n❌ IRON DOME ERROR: Please run as Administrator to block websites!")
    except Exception as e:
        print(f"\n❌ UNKNOWN ERROR: {e}")

def disengage_iron_dome(blocked_sites):
    if not blocked_sites: return
    try:
        with open(HOSTS_PATH, 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            for line in lines:
                if not any(site in line for site in blocked_sites): file.write(line)
            file.truncate()
            
        flush_dns()
        
    except PermissionError: 
        pass