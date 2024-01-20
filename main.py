import pygame
import requests
import time
import math

# Initialize pygame and joystick
pygame.init()
pygame.joystick.init()
print("Pygame and joystick initialized.")

# Camera IP and base URL
camera_ip = "192.168.4.244"
base_url = f"http://{camera_ip}/-wvhttp-01-/"
control_cmd = "control.cgi?"
# video_cmd = "image.cgi?"

# Define the dead zone threshold
dead_zone_threshold = 0.1

# Zoom speed settings
min_zoom_speed = 2  # Minimum zoom speed
max_zoom_speed = 23  # Maximum zoom speed for fast zoom

# Function to send HTTP request for relative zoom in and then stop
def zoom_in():
    print("Zooming in...")
    requests.get(base_url + control_cmd + "c.1.zoom=v150")  # Start zooming in

# Function to send HTTP request for relative zoom out and then stop
def zoom_out():
    print("Zooming out...")
    requests.get(base_url + control_cmd + "c.1.zoom=v50")  # Start zooming out

# Function to send HTTP request for stopping zoom out and then stop
def zoom_stop():
    requests.get(base_url + control_cmd + "c.1.zoom=stop")  # Start zooming out
    print("Zoom Stopped...")

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

# Global variable to store the current ND filter value
current_nd_value = 0
nd_values = [0, 400, 1600, 6400]  # Possible ND filter values

def nd_more():
    global current_nd_value
    # Find the next higher value in nd_values, if any
    next_value = next((x for x in nd_values if x > current_nd_value), current_nd_value)
    current_nd_value = next_value
    print(f"Increasing ND Filter to {current_nd_value}")
    requests.get(base_url + control_cmd + f"c.1.nd.filter={current_nd_value}")
    print("ND Filter increased")

def nd_less():
    global current_nd_value
    # Find the next lower value in nd_values, if any
    next_value = next((x for x in reversed(nd_values) if x < current_nd_value), current_nd_value)
    current_nd_value = next_value
    print(f"Decreasing ND Filter to {current_nd_value}")
    requests.get(base_url + control_cmd + f"c.1.nd.filter={current_nd_value}")
    print("ND Filter decreased")

# Now, nd_more() will increase the ND filter value, and nd_less() will decrease it

last_zoom_command = None

def handle_zoom(axis_value):
    global last_zoom_command

    # Calculate the zoom speed based on the axis_value
    def calculate_zoom_speed(axis_value):
        # Normalize the axis value to be in the range [0, 1]
        normalized_value = (abs(axis_value) - dead_zone_threshold) / (1 - dead_zone_threshold)
        # Map the normalized value to the zoom speed range
        zoom_speed = int(normalized_value * (max_zoom_speed - min_zoom_speed)) + min_zoom_speed
        return zoom_speed

    # Determine zoom speed and direction based on joystick tilt
    if abs(axis_value) > dead_zone_threshold:
        zoom_speed = calculate_zoom_speed(axis_value)
        # Reversing the direction: up (negative axis_value) zooms in, down (positive axis_value) zooms out
        zoom_direction = "wide" if axis_value > 0 else "tele"
        zoom_speed_param = f"c.1.zoom.speed={zoom_speed}"
    else:
        zoom_direction = "stop"
        zoom_speed_param = ""

    # Construct the zoom command
    zoom_command = f"{base_url}{control_cmd}c.1.zoom={zoom_direction}&{zoom_speed_param}" if zoom_speed_param else f"{base_url}{control_cmd}c.1.zoom=stop"

    # Send the command only if it's different from the last sent command or if the joystick is continuously tilted
    if zoom_command != last_zoom_command or abs(axis_value) > dead_zone_threshold:
        requests.get(zoom_command)
        last_zoom_command = zoom_command

# Main loop
try:
    if pygame.joystick.get_count() == 0:
        raise Exception("No joystick found. Please connect a joystick.")

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick {joystick.get_name()} initialized.")

    while True:
        pygame.event.pump()
        # Axis Mappings
        axis_0 = joystick.get_axis(0)
        axis_1 = joystick.get_axis(1)
        axis_2 = joystick.get_axis(2)
        axis_3 = joystick.get_axis(3)
        axis_4 = joystick.get_axis(4)
        axis_5 = joystick.get_axis(5)

        handle_zoom(joystick.get_axis(3))
        time.sleep(0.1)  # Adjust loop frequency as needed

        # Check for button presses
        if joystick.get_button(0):  # A button for auto focus
            auto_focus()
        if joystick.get_button(1):  # B button for recording
            record()
        if joystick.get_button(3):  # Y button for white balance auto on/off
            toggle_white_balance()
        if joystick.get_button(9):  # Y button for white balance auto on/off
            zoom_out()
        if joystick.get_button(10):  # Y button for white balance auto on/off
            zoom_in()
        if joystick.get_button(2): # X button for Stop Zoom
            zoom_stop()
        if joystick.get_button(11): # X button for Stop Zoom
            nd_more()
        if joystick.get_button(12): # X button for Stop Zoom
            nd_less()
        # Determine zoom direction and speed based on Y-axis value
        zoom_speed = None
        # Determine zoom direction and speed based on Y-axis value
        if abs(axis_3) > 0.1:
            if abs(axis_3) > 0.5:  # Maximum tilt
                zoom_speed_param = "c.1.zoom.speed.max"
            else:  # Moderate tilt
                zoom_speed_param = "c.1.zoom.speed.min"
            zoom_direction = "tele" if axis_3 > 0 else "wide"
        else:
            zoom_speed_param = ""
            zoom_direction = "stop"

        # Construct and send the zoom command
        if zoom_speed_param:
            zoom_command = f"{base_url}{control_cmd}c.1.zoom={zoom_direction}&{zoom_speed_param}"
            requests.get(zoom_command)
        else:
            # Stop the zoom if the joystick is near the center position
            stop_command = f"{base_url}{control_cmd}c.1.zoom=stop"
            requests.get(stop_command)


        handle_zoom(joystick.get_axis(3))  # Assuming axis 3 is the relevant axis for zoom

        time.sleep(0.05)  # Adjust the sleep duration as needed for responsiveness

except Exception as e:
    print(f"Error: {e}")
finally:
    pygame.quit()
    print("Pygame quit. Script ended.")
