# ======================================================================
#  LED Brightness Web Slider  -  dim an LED from ANYWHERE in the world
#  (old name: inoledblink.py)
#
#  HOW IT WORKS (follow the arrows)
#    friend's phone -> ngrok link -> THIS program on your laptop
#                   -> USB cable  -> Arduino Uno -> LED on pin 11 dims
#
#  STEP BY STEP
#   1. Upload arduino/LED_Brightness_WebSlider to the Uno
#      (LED + 220 ohm resistor on pin 11, short leg to GND).
#   2. CLOSE the Arduino Serial Monitor (only one program can use the port).
#   3. Check PORT below matches Arduino IDE -> Tools -> Port.
#   4. Run this program:      python web_led_brightness_slider.py
#   5. Test it on the laptop: open http://127.0.0.1:5000 and move the slider.
#   6. Share it with the world: in a SECOND window run   ngrok http 5000
#      and send the https://....ngrok-free.dev link to your friend.
#   7. Finished? Press Ctrl+C in both windows. The link stops working.
#
#  SAFETY: anyone who has the ngrok link can move your slider.
#          Only share it with people you know, and stop ngrok afterwards.
# ======================================================================

from flask import Flask, request

import serial
import socket
import sys

# -----------------------------
# Arduino Serial Port
# -----------------------------
PORT = "COM5"      # CHANGE THIS if Arduino IDE -> Tools -> Port shows a different COM number
BAUD = 9600        # must match Serial.begin(9600) in the Uno sketch

try:
    arduino = serial.Serial(PORT, BAUD, timeout=1)
except serial.SerialException:
    print(f"Could not open {PORT}. Is the Uno plugged in, and is the Serial Monitor closed?")
    sys.exit(1)

app = Flask(__name__)

HTML = """

<!DOCTYPE html>

<html>

<head>

<title>Arduino PWM LED</title>

<style>

body{

background:#111827;

font-family:Arial;

text-align:center;

color:white;

margin-top:50px;

}

.card{

width:450px;

margin:auto;

background:#1f2937;

padding:30px;

border-radius:20px;

box-shadow:0 0 20px cyan;

}

h1{

color:cyan;

}

.slider{

width:100%;

}

.value{

font-size:45px;

color:lime;

margin:20px;

}

button{

padding:15px 40px;

border:none;

background:#06b6d4;

color:white;

font-size:20px;

border-radius:10px;

cursor:pointer;

margin:10px;

}

button:hover{

background:#0891b2;

}

</style>

</head>

<body>

<div class="card">

<h1>Arduino LED PWM Control</h1>

<h2>Pin 11</h2>

<div class="value">

<span id="v">0</span>

</div>

<input

type="range"

min="0"

max="255"

value="0"

class="slider"

id="slider"

oninput="change(this.value)"

>

<br><br>

<button onclick="off()">OFF</button>

<button onclick="full()">FULL</button>

</div>

<script>

function change(val){

document.getElementById("v").innerHTML=val;

fetch("/set?value="+val);

}

function off(){

document.getElementById("slider").value=0;

change(0);

}

function full(){

document.getElementById("slider").value=255;

change(255);

}

</script>

</body>

</html>

"""

@app.route("/")
def home():
    return HTML

@app.route("/set")
def set_value():
    value = request.args.get("value")

    arduino.write((value + "\n").encode())

    return "OK"

if __name__ == "__main__":

    hostname = socket.gethostname()

    ip = socket.gethostbyname(hostname)

    print("="*50)
    print("Server Started")
    print("Localhost : http://127.0.0.1:5000")
    print(f"Network   : http://{ip}:5000")
    print("="*50)

    app.run(host="0.0.0.0", port=5000)