"""
pc_clock_sender.py
-------------------
Reads the PC's real-time clock and sends it over serial (COM5)
to an Arduino once per second, in the format:

    HH:MM:SS|DD|MM|YYYY|DOW\n

Example line sent: 14:32:07|11|08|2026|TUE

Requirements:
    pip install pyserial

Change SERIAL_PORT below if your Arduino shows up on a different
COM port (check Arduino IDE -> Tools -> Port).
"""

import serial
import time
from datetime import datetime

SERIAL_PORT = "COM5"
BAUD_RATE   = 115200

def main():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # give the Arduino time to reset after the port opens

    print(f"Connected to {SERIAL_PORT} @ {BAUD_RATE} baud")
    print("Sending time every second. Press Ctrl+C to stop.\n")

    day_names = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

    try:
        last_sent_second = None
        while True:
            now = datetime.now()

            # only send once per second (avoid duplicate sends in the same tick)
            if now.second != last_sent_second:
                last_sent_second = now.second

                time_str = now.strftime("%H:%M:%S")
                day_str  = now.strftime("%d")
                month_str = now.strftime("%m")
                year_str  = now.strftime("%Y")
                dow_str   = day_names[now.weekday()]

                line = f"{time_str}|{day_str}|{month_str}|{year_str}|{dow_str}\n"
                ser.write(line.encode("utf-8"))

                print(f"Sent: {line.strip()}")

            time.sleep(0.05)  # small sleep to avoid hammering the CPU

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        ser.close()

if __name__ == "__main__":
    main()