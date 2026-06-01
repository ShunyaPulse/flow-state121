import sys
import time
from iron_dome import disengage_iron_dome

def main():
    if len(sys.argv) < 3:
        return

    try:
        target_timestamp = float(sys.argv[1])
        blocked_sites = sys.argv[2].split(",")

        time_to_sleep = target_timestamp - time.time()

        if time_to_sleep > 0:
            time.sleep(time_to_sleep)

        disengage_iron_dome(blocked_sites)

    except Exception:
        pass 

if __name__ == "__main__":
    main()