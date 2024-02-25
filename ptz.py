import RPi.GPIO as GPIO
import pygame
from time import sleep, time, strftime
import os
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
AN1, AN2, DIG1, DIG2 = 12, 13, 26, 24
GPIO.setup([AN1, AN2, DIG1, DIG2], GPIO.OUT)
p1, p2 = GPIO.PWM(AN1, 100), GPIO.PWM(AN2, 100)
p1.start(0)
p2.start(0)
pygame.init()
pygame.joystick.init()
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
else:
    print("No joystick found at startup.")
    joystick = None
dead_zone = 0.05
multiplier_dead_zone = 0.15

def reboot_system():
    print("Rebooting the system...")
    os.system('sudo reboot')
def remap_axis_value(axis_value, cap_at_15_percent=False):
    # Scale the input from -0.75 to 0.75 to full range (-1.0 to 1.0)
    max_input_value = 0.77
    scaled_value = axis_value / max_input_value if axis_value != 0 else 0  # Avoid division by zero
    scaled_value = max(min(scaled_value, 1.0), -1.0)  # Clamp the value to [-1.0, 1.0]

    if abs(scaled_value) <= dead_zone:
        return 0

    # Adjust the remapping logic for the scaled input
    remapped_value = (abs(scaled_value) - dead_zone) / (1 - dead_zone)
    curved_value = remapped_value ** 4

    if cap_at_15_percent:
        # If the cap is at 20 percent, adjust the output accordingly
        return min(curved_value * 20, 20)  # Assuming 20 is your intended max cap here for 20%
    else:
        # For full range output without capping at 20 percent
        return curved_value * 100

def calculate_multiplier(axis_value):
    if axis_value <= -1.0:
        return 1  # Ensure the multiplier is 1x at the minimum
    elif axis_value >= 1.0:
        return 10  # Ensure the multiplier is 4x at the maximum
    else:
        # Linear interpolation for values between -1.0 and 1.0
        return ((axis_value + 1) * 1.5) + 1

def set_motor_speed_and_direction(axis_value, pwm, dir_pin, speed_multiplier=1):
    if abs(axis_value) <= dead_zone:
        pwm.ChangeDutyCycle(0)
        return
    direction = GPIO.HIGH if axis_value > 0 else GPIO.LOW
    GPIO.output(dir_pin, direction)
    speed = remap_axis_value(abs(axis_value))
    speed *= speed_multiplier
    pwm.ChangeDutyCycle(min(speed, 100))
def graceful_shutdown():
    """Stop motors, cleanup GPIO, and quit Pygame."""
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p1.stop()
    p2.stop()
    GPIO.cleanup()
    pygame.quit()
    print("Motors stopped, GPIO cleaned up, and Pygame quit.")
try:
    button_10_pressed_time = None  # Track when button 15 was pressed
    while True:
        if not joystick or pygame.joystick.get_count() == 0:
            print("Joystick disconnected during operation.")
            break

        pygame.event.pump()
        button_10 = joystick.get_button(8)  # Button indices are 0-based; button 12 is index 14

        # Check if button 12 is pressed
        if button_10:
            if button_10_pressed_time is None:
                button_10_pressed_time = time()  # Record the time button 12 was pressed
        else:
            if button_10_pressed_time is not None:
                elapsed_time = time() - button_10_pressed_time
                button_10_pressed_time = None
                print(f"Button 12 was released after {elapsed_time} seconds.")

        # Check if button 15 has been held for 10 seconds
        if button_10_pressed_time and time() - button_10_pressed_time >= 2:
            print("Button 12 held for 2 seconds. Initiating reboot...")
            reboot_system()
            break  # Exit the loop since the system is about to reboot

        axis0, axis1, axis2, axis3, axis4, axis5 = joystick.get_axis(0), joystick.get_axis(1), joystick.get_axis(2), joystick.get_axis(3), joystick.get_axis(4), joystick.get_axis(5)  # Corrected for axis 4 as axis 5
        axis0_multiplier = calculate_multiplier(axis2)
        axis1_multiplier = calculate_multiplier(axis2)
        remapped_value_axis0 = remap_axis_value(axis0, cap_at_15_percent=True)
        remapped_value_axis1 = remap_axis_value(axis1, cap_at_15_percent=True)
        final_speed_axis0 = min(remapped_value_axis0 * axis0_multiplier, 100)
        final_speed_axis1 = min(remapped_value_axis1 * axis1_multiplier, 100)

        # Check if both axes are outside the dead zone and apply the rule
        if abs(axis0) > multiplier_dead_zone and abs(axis1) > multiplier_dead_zone:
            final_speed_axis0 = min(final_speed_axis0 * 1.25, 100)
            final_speed_axis1 = min(final_speed_axis1 * 1.25, 100)

        set_motor_speed_and_direction(axis0, p1, DIG1, final_speed_axis0 / 100)
        set_motor_speed_and_direction(axis1, p2, DIG2, final_speed_axis1 / 100)
        sleep(0.1)
except KeyboardInterrupt:
    print("Script termination requested via keyboard interrupt.")
finally:
    graceful_shutdown()
