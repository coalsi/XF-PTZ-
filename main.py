import subprocess
import os
import pygame
import time

def init_pygame():
    """Initialize only the necessary Pygame modules."""
    pygame.display.init()  # Initialize display module to prevent errors
    pygame.joystick.init()  # Initialize joystick module specifically
    os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Use a dummy video driver to avoid needing a GUI

def wait_for_joystick():
    """Wait for the joystick to be connected."""
    print("Waiting for joystick to be connected...")
    while pygame.joystick.get_count() == 0:
        pygame.event.pump()
        time.sleep(1)
    print("Joystick connected.")

def run_scripts():
    """Run the PTZ and XF control scripts."""
    ptz_process = subprocess.Popen(["python3", "ptz.py"])
    xf_process = subprocess.Popen(["python3", "xf.py"])
    print("Both scripts are running concurrently...")
    return [ptz_process, xf_process]

def monitor_joystick(subprocesses):
    """Monitor the joystick and restart scripts if it's disconnected."""
    try:
        while True:
            pygame.event.pump()
            if pygame.joystick.get_count() == 0:
                print("Joystick disconnected. Terminating scripts...")
                for proc in subprocesses:
                    proc.terminate()
                    proc.wait()  # Wait for the process to terminate
                subprocesses.clear()  # Clear the list after terminating processes
                wait_for_joystick()  # Wait for the joystick to be reconnected
                subprocesses.extend(run_scripts())  # Restart the scripts
            time.sleep(1)
    finally:
        pygame.quit()

if __name__ == "__main__":
    os.environ['SDL_AUDIODRIVER'] = 'dummy'  # Set dummy audio driver
    init_pygame()  # Initialize Pygame with necessary modules
    wait_for_joystick()  # Initial wait for the joystick to be connected
    subprocesses = run_scripts()  # Start the subprocesses
    monitor_joystick(subprocesses)  # Monitor the joystick status
