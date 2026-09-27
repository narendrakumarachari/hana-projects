# ======================================================================
#  ESP32 LED Web Remote  -  control an LED from ANYWHERE in the world
#  (old name: wificomunication.py)
#
#  HOW IT WORKS (follow the arrows)
#    friend's phone  ->  ngrok link  ->  THIS program on your laptop
#                    ->  Wi-Fi       ->  ESP32  ->  LED turns on!
#
#  STEP BY STEP
#   1. Upload arduino/ESP32_WiFi_LED_WebAPI to the ESP32.
#      Its Serial Monitor (9600 baud) shows its address, e.g. 192.168.1.248
#   2. Type that address in ESP32_IP below and save this file.
#   3. Run this program:      python web_esp32_led_control.py
#   4. Test it on the laptop: open http://127.0.0.1:5000 and press ON.
#   5. Share it with the world: in a SECOND window run   ngrok http 5000
#      and send the https://....ngrok-free.dev link to your friend.
#   6. Finished? Press Ctrl+C in both windows. The link stops working.
#
#  SAFETY: anyone who has the ngrok link can press your buttons.
#          Only share it with people you know, and stop ngrok afterwards.
# ======================================================================

import requests
import threading
import time
from flask import Flask, render_template_string

app = Flask(__name__)

# The ESP32's address on your home Wi-Fi. CHANGE THIS to the number the
# ESP32 prints in its Serial Monitor. (It can change after a router restart.)
ESP32_IP = "192.168.1.248"

blinking = False        # True while the BIRD button keeps the LED blinking


def tell_esp32(command):
    """Send /on or /off to the ESP32. Returns True if the ESP32 answered."""
    try:
        requests.get(f"http://{ESP32_IP}/{command}", timeout=3)
        return True
    except requests.exceptions.RequestException:
        # ESP32 is off, on another Wi-Fi, or ESP32_IP is wrong.
        print(f"Could not reach the ESP32 at {ESP32_IP}. Is it on the same Wi-Fi?")
        return False


def blink_loop():
    """Runs in the background: LED on 1 second, off 1 second, until BIRD is pressed again."""
    global blinking

    while blinking:

        # ON
        tell_esp32("on")
        print("LED ON")

        time.sleep(1)

        # Check if BIRD was pressed again
        if not blinking:
            break

        # OFF
        tell_esp32("off")
        print("LED OFF")

        time.sleep(1)

    # Make sure LED is OFF
    tell_esp32("off")


# The web page everyone sees: three buttons. Each button asks THIS program
# for /on, /off or /bird, and shows the answer under the buttons.
HTML = """
<!DOCTYPE html>

<html>

<head>

<title>ESP32 Control</title>

<style>

body {
    font-family: Arial;
    text-align: center;
    padding-top: 80px;
}

button {
    font-size: 20px;
    padding: 15px 30px;
    margin: 10px;
}

</style>

</head>

<body>

<h1>ESP32 LED Control</h1>

<button onclick="send('on')">
ON
</button>

<button onclick="send('off')">
OFF
</button>

<button onclick="send('bird')">
BIRD
</button>

<p id="result">Ready</p>

<script>

function send(endpoint) {

    fetch("/" + endpoint)

    .then(response => response.text())

    .then(data => {

        document.getElementById("result").innerText = data;

    });

}

</script>

</body>

</html>
"""


@app.route("/")
def home():

    return render_template_string(HTML)


@app.route("/on")
def on():

    global blinking

    blinking = False

    return "LED ON" if tell_esp32("on") else "Can't reach the ESP32 - check it is on and ESP32_IP is right"


@app.route("/off")
def off():

    global blinking

    blinking = False

    return "LED OFF" if tell_esp32("off") else "Can't reach the ESP32 - check it is on and ESP32_IP is right"


@app.route("/bird")
def bird():

    global blinking

    # Start blinking
    if not blinking:

        blinking = True

        thread = threading.Thread(
            target=blink_loop,
            daemon=True
        )

        thread.start()

        return "BIRD: BLINKING"

    # Stop blinking
    else:

        blinking = False

        return "BIRD: STOPPED"


if __name__ == "__main__":

    print("=" * 50)
    print("ESP32 LED Web Remote is running!")
    print("On this laptop : http://127.0.0.1:5000")
    print("For the world  : open a 2nd window and run   ngrok http 5000")
    print("Stop           : Ctrl+C")
    print("=" * 50)

    # host="0.0.0.0" lets ngrok (and phones on your Wi-Fi) reach this program.
    # debug=False keeps Flask's debugger OFF: this page is shared with the
    #   world, and the debugger would let strangers run code on this laptop.
    # use_reloader=False stops Flask from starting the program twice.
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )
