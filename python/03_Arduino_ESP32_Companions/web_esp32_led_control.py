import requests
import threading
import time
from flask import Flask, render_template_string

app = Flask(__name__)

ESP32_IP = "192.168.1.248"

blinking = False


def blink_loop():

    global blinking

    while blinking:

        # ON
        requests.get(f"http://{ESP32_IP}/on")
        print("LED ON")

        time.sleep(1)

        # Check if BIRD was pressed again
        if not blinking:
            break

        # OFF
        requests.get(f"http://{ESP32_IP}/off")
        print("LED OFF")

        time.sleep(1)

    # Make sure LED is OFF
    requests.get(f"http://{ESP32_IP}/off")


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

    requests.get(f"http://{ESP32_IP}/on")

    return "LED ON"


@app.route("/off")
def off():

    global blinking

    blinking = False

    requests.get(f"http://{ESP32_IP}/off")

    return "LED OFF"


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

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )