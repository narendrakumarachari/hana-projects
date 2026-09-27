import serial
import keyboard

PORT = "COM5"
BAUDRATE = 9600

ser = serial.Serial(PORT, BAUDRATE, timeout=1)

print(f"Listening on {PORT}...")

while True:
    if ser.in_waiting:
        data = ser.readline().decode("utf-8", errors="ignore").strip()

        if data:
            print(f"Received: {data}")

        if data == "=":
            keyboard.write("=")
            print("Pressed '='")