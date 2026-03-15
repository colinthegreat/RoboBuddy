from gpiozero import Motor
from time import sleep

# Define the motors based on your pin configuration
# Motor 1 (Left?) connected to GPIO 5 and 6
motor_left = Motor(forward=5, backward=6)

# Motor 2 (Right?) connected to GPIO 13 and 19
motor_right = Motor(forward=13, backward=19)

print("Starting Motor Test...")

try:
    print("Moving Forward...")
    motor_left.forward()
    motor_right.forward()
    sleep(2)

    print("Stopping...")
    motor_left.stop()
    motor_right.stop()
    sleep(1)

    print("Moving Backward...")
    motor_left.backward()
    motor_right.backward()
    sleep(2)

    print("Stopping...")
    motor_left.stop()
    motor_right.stop()
    sleep(1)

    print("Spinning Left...")
    motor_left.backward()
    motor_right.forward()
    sleep(1)

    print("Stopping...")
    motor_left.stop()
    motor_right.stop()
    sleep(1)

    print("Spinning Right...")
    motor_left.forward()
    motor_right.backward()
    sleep(1)

    print("Stopping...")
    motor_left.stop()
    motor_right.stop()
    sleep(1)

    print("Test Complete!")

except KeyboardInterrupt:
    print("\nTest interrupted by user. Stopping motors.")
    motor_left.stop()
    motor_right.stop()
except Exception as e:
    print(f"\nAn error occurred: {e}")
    motor_left.stop()
    motor_right.stop()
finally:
    # Ensure motors are stopped even if error occurs
    motor_left.close()
    motor_right.close()
