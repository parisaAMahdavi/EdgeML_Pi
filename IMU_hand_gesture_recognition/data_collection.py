import time
import csv
import os
from IMU import GY85_IMUSensor

# Initialize IMU sensor
imu = GY85_IMUSensor()

# Define folder name for collected data
DATA_FOLDER = "collected_data"

# Ensure the folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)

# Function to collect data for a gesture
def collect_gesture(person_name, gesture_name, duration=5, sample_rate=50, repetitions=5):
    filename = os.path.join(DATA_FOLDER, f"{person_name}_{gesture_name}.csv")

    # Check if the file exists to add headers only once
    file_exists = os.path.isfile(filename)

    for i in range(repetitions):  # Repeat for multiple gestures
        print(f"Recording gesture '{gesture_name}' for '{person_name}' ({i+1}/{repetitions})...")
        data_buffer = []  # Store data in a list before writing to file
        start_time = time.perf_counter()
        end_time = start_time + duration  # Stop time after 'duration' seconds

        while time.perf_counter() < end_time:
            loop_start = time.perf_counter()  # Track loop start time
            # Read sensor data
            ax, ay, az = imu.get_accel_data()
            gx, gy, gz = imu.get_gyro_data()
            timestamp = time.perf_counter()

            # Store data in buffer
            data_buffer.append([timestamp, ax, ay, az, gx, gy, gz, person_name, gesture_name])

            # Wait to maintain sampling rate
            while time.perf_counter() < loop_start + (1 / sample_rate):
                pass  # Busy-wait

        # Write collected data to CSV
        with open(filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            # Write header only if file is new
            if not file_exists:
                writer.writerow(["Timestamp", "Acc_X", "Acc_Y", "Acc_Z", "Gyro_X", "Gyro_Y", "Gyro_Z", "Person", "Gesture"])
                file_exists = True  # Ensure header is not written again

            writer.writerows(data_buffer)

        print(f"Gesture '{gesture_name}' recorded for {duration} seconds.")
        if i < repetitions - 1:  # Avoid delay after last gesture
            print("Pausing for 5 seconds before next recording...")
            time.sleep(5)
    print(f"Finished recording {repetitions} gestures of '{gesture_name}' for '{person_name}'.")

# User input for person's name, gesture name, and number of repetitions
person_name = input("Enter person's name: ").strip().replace(" ", "_")  # Replace spaces with underscores
gesture_name = input("Enter gesture name (e.g., swipe_left, swipe_right): ").strip().replace(" ", "_")
num_repetitions = int(input("Enter the number of times to record this gesture: "))

collect_gesture(person_name, gesture_name, repetitions=num_repetitions)
