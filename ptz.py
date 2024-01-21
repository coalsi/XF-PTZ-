import pygame
import requests
import time
import RPi.GPIO as GPIO
from DRV8825 import DRV8825

# Initialize pygame and joystick
pygame.init()
pygame.joystick.init()
print("Pygame and joystick initialized.")

# Initialize Motors
Motor1 = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
Motor2 = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))

# Manually set microstepping mode
microstepping_mode = 'fullstep'  # Example mode, change as needed
Motor1.SetMicroStep('hardware', microstepping_mode)
Motor2.SetMicroStep('hardware', microstepping_mode)

# Function to calculate step delay based on joystick position
def calculate_step_delay(axis_2_value, axis_5_value):
    # Adjust the axis values to be in the range 0.0 to 2.0
    adjusted_axis_2_value = axis_2_value + 1.0
    adjusted_axis_5_value = axis_5_value + 1.0

    # Axis range after adjustment
    adjusted_axis_range = [0.0, 2.0]
    delay_range = [0.0001, 0.0]  # Step delay range

    # Determine which axis to use for delay calculation
    if abs(adjusted_axis_2_value) >= 0.01:  # Priority to Axis 2
        axis_value = adjusted_axis_2_value
    elif abs(adjusted_axis_5_value) >= 0.01:
        axis_value = adjusted_axis_5_value
    else:
        return 0.0001  # Default delay if neither axis is active

    # Linearly interpolate between delay_range[0] and delay_range[1]
    fraction = (axis_value - adjusted_axis_range[0]) / (adjusted_axis_range[1] - adjusted_axis_range[0])
    delay = delay_range[0] + fraction * (delay_range[1] - delay_range[0])

    return delay

# Main loop and other parts of the script remain unchanged...


# Main loop
try:
    if pygame.joystick.get_count() == 0:
        raise Exception("No joystick found. Please connect a joystick.")

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick {joystick.get_name()} initialized.")

    while True:
        pygame.event.pump()

        # Read axis values
        axis_0_value = joystick.get_axis(0)
        axis_1_value = joystick.get_axis(1)
        axis_2_value = joystick.get_axis(2)
        axis_5_value = joystick.get_axis(5)

        step_delay = calculate_step_delay(axis_2_value, axis_5_value)

        # Control Motor 1 with Axis 0
        if abs(axis_0_value) >= 0.3:  # Apply dead zone to axis value
            steps_motor1 = 10
            Motor1.TurnStep(Dir='forward' if axis_0_value > 0 else 'backward', steps=steps_motor1, stepdelay=step_delay)

        # Control Motor 2 with Axis 1
        if abs(axis_1_value) >= 0.3:  # Apply dead zone to axis value
            steps_motor2 = 10
            Motor2.TurnStep(Dir='forward' if axis_1_value > 0 else 'backward', steps=steps_motor2, stepdelay=step_delay)

        # time.sleep(0.1)  # Adjust loop frequency as needed

except Exception as e:
    print(f"Error: {e}")
finally:
    # Stop the motors and clean up GPIO
    Motor1.Stop()
    Motor2.Stop()
    GPIO.cleanup()
    pygame.quit()
    print("Pygame quit. Script ended.")
