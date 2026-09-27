# import serial
# import time


# # --------------------------------------------------
# # STEP 1: Open communication with Arduino
# # --------------------------------------------------

# # Change this according to your computer.

# # Linux example:
# # PORT = "/dev/ttyACM0"

# # Windows example:
# PORT = "COM5"


# # This MUST match Arduino's Serial.begin()
# BAUD_RATE = 115200


# # Create the serial connection
# arduino = serial.Serial(PORT, BAUD_RATE)

# # Give Arduino time to reset after
# # the serial connection is opened.
# time.sleep(2)


# # --------------------------------------------------
# # STEP 2: Continuously receive data
# # --------------------------------------------------

# while True:

#     # Read one complete line sent by Arduino.
#     #
#     # Arduino sends:
#     #
#     # Temperature:28.50,Humidity:65.00
#     #
#     line = arduino.readline()


#     # Convert bytes → normal Python string
#     #
#     # Serial data arrives as bytes.
#     #
#     # Example:
#     #
#     # b'Temperature:28.50,Humidity:65.00\r\n'
#     #
#     # decode() converts it into:
#     #
#     # 'Temperature:28.50,Humidity:65.00'
#     #
#     line = line.decode("utf-8").strip()


#     # Print what Arduino sent
#     print(line)



