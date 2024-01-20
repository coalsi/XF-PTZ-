import pygame
import requests
import time
import math

# Initialize pygame and joystick
pygame.init()
pygame.joystick.init()
print("Pygame and joystick initialized.")

# Camera IP and base URL
camera_ip = "192.168.1.XXX"
base_url = f"http://{camera_ip}/-wvhttp-01-/control.cgi?"

# Define the dead zone threshold (adjust as needed)
dead_zone_threshold = 0.1

# Function to send HTTP request for relative zoom in and then stop
def zoom_in():
    print("Zooming in (relative)...")
    requests.get(base_url + "c.1.zoom=tele")  # Start zooming in
    time.sleep(0.5)  # Short delay
    response = requests.get(base_url + "c.1.zoom=stop")  # Stop zooming
    print(f"Response from camera (Stop Zoom): {response.status_code}, {response.text}")

# Function to send HTTP request for relative zoom out and then stop
def zoom_out():
    print("Zooming out (relative)...")
    requests.get(base_url + "c.1.zoom=wide")  # Start zooming out
    time.sleep(0.5)  # Short delay
    response = requests.get(base_url + "c.1.zoom=stop")  # Stop zooming
    print(f"Response from camera (Stop Zoom): {response.status_code}, {response.text}")

# Function to send HTTP request for auto focus
def auto_focus():
    print("Auto focusing...")
    # Add your code here to send the HTTP request for auto focus
    print("Auto focus request sent.")

# Function to send HTTP request for recording
def record():
    print("Recording...")
    # Add your code here to send the HTTP request for recording
    print("Recording request sent.")

# Function to toggle white balance auto on/off
def toggle_white_balance():
    print("Toggling White Balance Auto...")
    # Add your code here to send the HTTP request to toggle white balance auto
    print("White Balance Auto toggled.")

# Main loop
try:
    if pygame.joystick.get_count() == 0:
        raise Exception("No joystick found. Please connect a joystick.")

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick {joystick.get_name()} initialized.")

    while True:
        pygame.event.pump()

        # Check for button presses
        if joystick.get_button(0):  # A button for auto focus
            auto_focus()
            time.sleep(0.5)
        if joystick.get_button(1):  # B button for recording
            record()
            time.sleep(0.5)
        if joystick.get_button(3):  # Y button for white balance auto on/off
            toggle_white_balance()
            time.sleep(0.5)
        if joystick.get_button(9):  # Y button for white balance auto on/off
            zoom_out()
            time.sleep(0.5)
        if joystick.get_button(10):  # Y button for white balance auto on/off
            zoom_in()
            time.sleep(0.5)

        # Check for axis positions with dead zone
        right_stick_x = joystick.get_axis(3)  # Right Stick X-axis for zoom in/out
        right_stick_y = joystick.get_axis(4)  # Right Stick Y-axis for zoom in/out
        left_trigger = joystick.get_axis(2)   # Left Trigger for zoom out
        right_trigger = joystick.get_axis(5)  # Right Trigger for zoom in


except Exception as e:
    print(f"Error: {e}")

finally:
    pygame.quit()
    print("Pygame quit. Script ended.")
