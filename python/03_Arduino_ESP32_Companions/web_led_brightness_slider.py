from flask import Flask, request

import serial
import socket

# -----------------------------
# Arduino Serial Port
# -----------------------------
arduino = serial.Serial("COM5", 9600, timeout=1)

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