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
def calculate_step_delay(axis_value):
    # Map joystick position to step delay
    axis_range = [-1.0, 1.0]  # Axis 5 range
    delay_range = [0.001, 0.0000001]  # Step delay range

    # Linearly interpolate between delay_range[0] and delay_range[1]
    fraction = (axis_value - axis_range[0]) / (axis_range[1] - axis_range[0])
    delay = delay_range[0] + fraction * (delay_range[1] - delay_range[0])

    return delay


# Main loop
try:
    if pygame.joystick.get_count() == 0:
        raise Exception("No joystick found. Please connect a joystick.")

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick {joystick.get_name()} initialized.")

    while True:
        pygame.event.pump()

        # Control Motor 1 with Axis 0
        axis_0_value = joystick.get_axis(0)
        if abs(axis_0_value) >= 0.4:  # Apply dead zone to axis value
            steps_motor1 = 1
            Motor1.TurnStep(Dir='forward' if axis_0_value > 0 else 'backward', steps=steps_motor1, stepdelay=calculate_step_delay(joystick.get_axis(5)))

        # Control Motor 2 with Axis 1
        axis_1_value = joystick.get_axis(1)
        if abs(axis_1_value) >= 0.4:  # Apply dead zone to axis value
            steps_motor2 = 1
            Motor2.TurnStep(Dir='forward' if axis_1_value > 0 else 'backward', steps=steps_motor2, stepdelay=calculate_step_delay(joystick.get_axis(5)))

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
