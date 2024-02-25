import pygame
import requests
import time

# Initialize pygame and joystick
pygame.init()
pygame.joystick.init()
print("Pygame and joystick initialized.")

# Camera IP and base URL
camera_ip = "192.168.1.2"  # REPLACE WITH CAMERA IP ADDRESS
base_url = f"http://{camera_ip}/-wvhttp-01-/"
control_cmd = "control.cgi?"
info_cmd = "info.cgi?"
video_cmd = "image.cgi?"
menu_cmd = "menu.cgi?"

# Define the dead zone threshold and other global variables
dead_zone_threshold = 0.2
current_wb_mode = 'auto'  # Assume the initial mode is auto
wb_modes = ['auto', 'manual', 'wb_a', 'wb_b', 'daylight', 'tungsten', 'kelvin']
current_wb_index = 0  # Start with the first mode in the list
min_zoom_speed = 1  # Minimum zoom speed
max_zoom_speed = 25  # Maximum zoom speed for fast zoom
FOCUS_SPEED_MIN = 0  # Minimum focus speed
FOCUS_SPEED_MAX = 7  # Maximum focus speed
last_zoom_command = None
current_nd_value = 0
last_press_time = {
    'nd_more': 0,
    'nd_less': 0
}
nd_values = [0, 400, 1600, 6400]  # Possible ND filter values
autofocus_locked = False  # Start with continuous AF enabled by default
last_toggle_time = 0  # Track the last time the autofocus lock was toggled
current_mode_index = 0  # Start with the first mode
# Global variable to track the on-screen display state
display_state = 'off'  # Initial state is off

def toggle_display():
    global display_state  # Use the global variable

    # Determine the new state based on the current state
    new_state = 'off' if display_state == 'on' else 'on'

    # Construct the URL with the new state
    command_url = f"{base_url}menu.cgi?onscreen={new_state}"

    # Send the command to toggle the display state
    try:
        response = requests.get(command_url)
        if response.status_code == 200:
            print(f"On-screen display toggled to {new_state}.")
            display_state = new_state  # Update the global variable to the new state
        else:
            print(f"Failed to toggle on-screen display. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error toggling on-screen display: {e}")
def toggle_menu():
    global current_menu_type  # Use a global variable to track the current menu type

    # Initialize the current menu type if not already done
    if 'current_menu_type' not in globals():
        globals()['current_menu_type'] = -1  # Start before the first type so the first toggle goes to 0

    # Increment the current menu type, wrapping around to 0 after reaching the last type
    current_menu_type = (current_menu_type + 1) % 2  # There are four types, 0 through 3

    # Construct the URL with the new menu type
    command_url = f"{base_url}menu.cgi?type={current_menu_type}"

    # Send the command to change the menu type
    try:
        response = requests.get(command_url)
        if response.status_code == 200:
            print(f"Menu type changed to {current_menu_type}.")
        else:
            print(f"Failed to change menu type. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error changing menu type: {e}")


def navigate_menu(direction):
    """
    Navigate the camera's menu in the specified direction.

    :param direction: A string indicating the direction to navigate ('up', 'down', 'left', 'right', 'enter', 'cancel').
    """
    command_url = f"{base_url}{menu_cmd}cmd={direction}"
    try:
        response = requests.get(command_url)
        if response.status_code == 200:
            print(f"Menu navigation ({direction}) successful.")
        else:
            print(f"Failed to navigate menu. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error navigating menu: {e}")

def up():
    navigate_menu("up")

def down():
    navigate_menu("down")

def left():
    navigate_menu("left")

def right():
    navigate_menu("right")

def select():
    navigate_menu("enter")  # Assuming 'enter' is used for select

def cancel():
    navigate_menu("cancel")  # Assuming 'cancel' is used for back/menu

def toggle_autofocus_lock():
    global autofocus_locked, last_toggle_time
    current_time = time.time()
    # Check if enough time has passed since the last toggle (e.g., 0.5 seconds)
    if current_time - last_toggle_time < 0.5:
        return  # If not, exit the function without toggling
    print("Toggling autofocus lock...")
    new_state = 'off' if autofocus_locked else 'on'
    af_lock_url = f"{base_url}{control_cmd}c.1.focus.auto.lock={new_state}"
    response = requests.get(af_lock_url)
    autofocus_locked = not autofocus_locked
    last_toggle_time = current_time  # Update the last toggle time
    print(f"Autofocus lock set to {new_state}. Response: {response.status_code}")
def adjust_focus(axis_value):
    dead_zone = 0.5
    if abs(axis_value) < dead_zone:
        focus_stop_url = f"{base_url}{control_cmd}c.1.focus.action=stop"
        response = requests.get(focus_stop_url)
        return  # Exit the function
    focus_speed = map_axis_to_focus_speed(axis_value, FOCUS_SPEED_MIN, FOCUS_SPEED_MAX)
    if axis_value < 0:
        focus_direction = "near"  # Pull focus in
    else:
        focus_direction = "far"    # Take focus out
    focus_url = f"{base_url}{control_cmd}c.1.focus.action={focus_direction}&c.1.focus.speed={focus_speed}"
    response = requests.get(focus_url)
def map_axis_to_focus_speed(axis_value, speed_min, speed_max):
    normalized_value = (abs(axis_value) - 0.15) / (1 - 0.15)
    focus_speed = int(normalized_value * (speed_max - speed_min)) + speed_min
    return focus_speed
def toggle_white_balance():
    global current_wb_mode
    print("Toggling White Balance mode...")
    if current_wb_mode == 'auto':
        new_wb_mode = 'manual'
    else:
        new_wb_mode = 'auto'
    wb_url = base_url + control_cmd + f"c.1.wb={new_wb_mode}"
    response = requests.get(wb_url)
    current_wb_mode = new_wb_mode
    print(f"White Balance mode set to {new_wb_mode}. Response: {response.status_code}")
def nd_more():
    global current_nd_value
    current_time = time.time()
    # Check if enough time has passed since the last press
    if current_time - last_press_time['nd_more'] < 0.5:
        return  # Exit if not enough time has passed
    # Find the next higher value in nd_values, if any
    next_value = next((x for x in nd_values if x > current_nd_value), current_nd_value)
    current_nd_value = next_value
    print(f"Increasing ND Filter to {current_nd_value}")
    requests.get(base_url + control_cmd + f"c.1.nd.filter={current_nd_value}")
    print("ND Filter increased")
    last_press_time['nd_more'] = current_time  # Update the last press time
def nd_less():
    global current_nd_value
    current_time = time.time()
    if current_time - last_press_time['nd_less'] < 0.5:
        return
    next_value = next((x for x in reversed(nd_values) if x < current_nd_value), current_nd_value)
    current_nd_value = next_value
    print(f"Decreasing ND Filter to {current_nd_value}")
    requests.get(base_url + control_cmd + f"c.1.nd.filter={current_nd_value}")
    print("ND Filter decreased")
    last_press_time['nd_less'] = current_time
def none():
    pass
def handle_zoom(zoom_axis):
    global last_zoom_command
    def calculate_zoom_speed(axis_value):
        normalized_value = (abs(axis_value) - dead_zone_threshold) / (1 - dead_zone_threshold)
        normalized_value = max(0, normalized_value)
        zoom_speed = int(normalized_value * (max_zoom_speed - min_zoom_speed)) + min_zoom_speed
        return zoom_speed
    zoom_command = ""
    if zoom_axis > dead_zone_threshold:  # Positive axis value for tele
        zoom_speed = calculate_zoom_speed(zoom_axis)
        zoom_command = f"{base_url}{control_cmd}c.1.zoom=wide&c.1.zoom.speed={zoom_speed}"
    elif zoom_axis < -dead_zone_threshold:  # Negative axis value for wide, note the condition change
        zoom_speed = calculate_zoom_speed(zoom_axis)
        zoom_command = f"{base_url}{control_cmd}c.1.zoom=tele&c.1.zoom.speed={zoom_speed}"
    else:
        zoom_command = f"{base_url}{control_cmd}c.1.zoom=stop"
    if zoom_command != last_zoom_command:
        requests.get(zoom_command)
        last_zoom_command = zoom_command
def toggle_recording():
    try:
        status_response = requests.get(base_url + info_cmd + "f.rec.status")
        status_text = status_response.text.strip()
        if "f.rec.status:=rec" in status_text:
            new_state = 'off'
        elif "f.rec.status:=idle" in status_text:
            new_state = 'on'
        else:
            print("Unable to determine recording status.")
            return
        response = requests.get(base_url + control_cmd + "f.rec=" + new_state)
        print(f"Recording {'started' if new_state == 'on' else 'stopped'}. Response: {response.status_code}")
    except Exception as e:
        print(f"Error in toggle_recording: {e}")
def main():
    if pygame.joystick.get_count() == 0:
        print("No joystick found. Please connect a joystick.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick {joystick.get_name()} initialized.")

    try:
        while True:
            pygame.event.pump()
            if pygame.joystick.get_count() == 0:
                print("Joystick disconnected. Exiting script.")
                break

            # Existing joystick axis and button handling
            handle_zoom(joystick.get_axis(4))
            adjust_focus(joystick.get_axis(3))
            if joystick.get_button(0): # A button
                toggle_autofocus_lock()
                time.sleep(0.2)
            if joystick.get_button(1): # B button
                toggle_recording()
                time.sleep(0.2)
            if joystick.get_button(2):  # X Button
                cancel()
                time.sleep(0.2)
            if joystick.get_button(3):  # Y button
                select()
                time.sleep(0.2)
            if joystick.get_button(6):  #  Start Button
                none()
                time.sleep(0.2)
            if joystick.get_button(7):  #  Menu Button
                toggle_menu()
                time.sleep(0.2)
            if joystick.get_button(4):  # Left Button
                nd_less()
                time.sleep(0.2)
            if joystick.get_button(5):  # Right Button
                nd_more()
                time.sleep(0.2)
            if joystick.get_button(9):  # Left Joystick Button
                none()
                time.sleep(0.2)
            if joystick.get_button(10):  # Right Joystick Button
                toggle_display()
                time.sleep(0.2)

            # D-pad inputs handling
            dpad = joystick.get_hat(0)  # Read the state of hat 0
            if dpad == (0, 1):  # D-pad Up
                up()  # Increase ND filter for D-pad Up
                time.sleep(0.2)
            elif dpad == (0, -1):  # D-pad Down
                down()  # Decrease ND filter for D-pad Down
                time.sleep(0.2)
            elif dpad == (1, 0):  # D-pad Right
                right()  # Placeholder for D-pad Right action
                time.sleep(0.2)
            elif dpad == (-1, 0):  # D-pad Left
                left()  # Placeholder for D-pad Left action
                time.sleep(0.2)

            time.sleep(0.01)  # Adjust the sleep duration as needed for responsiveness

    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()
        print("Pygame quit. Script ended.")

if __name__ == "__main__":
    main()
