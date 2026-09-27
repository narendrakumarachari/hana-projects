from flask import Flask, request, jsonify, render_template_string
import serial
import serial.tools.list_ports
import threading
import time

# =====================================================
#                  CONFIGURATION
# =====================================================
SERIAL_PORT = "COM5"
BAUD_RATE = 115200

app = Flask(__name__)

ser = None
serial_lock = threading.Lock()   # prevents overlapping writes from concurrent requests

ANIMATIONS = [
    {"id": 0, "name": "Bouncing Ball"},
    {"id": 1, "name": "Starfield Warp"},
    {"id": 2, "name": "Pulsing Circles"},
    {"id": 3, "name": "Color Wave"},
    {"id": 4, "name": "Rotating Square"},
]


# =====================================================
#           SERIAL CONNECTION (opened ONCE at startup)
# =====================================================
def open_serial():
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2.5)  # allow Arduino to reset & print READY
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        print(f"[Serial] Connected on {SERIAL_PORT}")
    except Exception as e:
        ser = None
        print(f"[Serial] Failed to open {SERIAL_PORT}: {e}")


def send_command(cmd: str):
    """Thread-safe write with auto-reconnect if the port dropped."""
    global ser
    with serial_lock:
        try:
            if ser is None or not ser.is_open:
                open_serial()
            if ser is None:
                return False, "Serial port not available"

            ser.reset_input_buffer()
            ser.write((cmd + "\n").encode("utf-8"))
            ser.flush()
            time.sleep(0.05)  # tiny settle time, avoids back-to-back write collisions
            return True, "sent"
        except Exception as e:
            # Try one reconnect + retry
            try:
                open_serial()
                if ser:
                    ser.write((cmd + "\n").encode("utf-8"))
                    ser.flush()
                    return True, "sent (after reconnect)"
            except Exception as e2:
                return False, str(e2)
            return False, str(e)


# =====================================================
#                  HTML TEMPLATE
# =====================================================
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>TFT Display Controller</title>
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: 'Segoe UI', Arial, sans-serif;
    background: linear-gradient(135deg, #0f1c2e, #163350);
    color: #e6f1ff;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
  }
  .container {
    background: #10233a;
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 32px;
    width: 420px;
    box-shadow: 0 0 30px rgba(0, 200, 255, 0.15);
  }
  h1 { text-align: center; font-size: 22px; color: #4fc3f7; margin-bottom: 4px; }
  .subtitle { text-align: center; color: #7fa8c9; font-size: 13px; margin-bottom: 28px; }
  .section {
    background: #0c1b2e; border-radius: 12px; padding: 18px;
    margin-bottom: 20px; border: 1px solid #1e3a5f;
  }
  .section h2 {
    font-size: 15px; color: #4fc3f7; margin: 0 0 12px 0;
    display: flex; align-items: center; gap: 8px;
  }
  select, input[type="text"] {
    width: 100%; padding: 10px 12px; border-radius: 8px;
    border: 1px solid #2a4d73; background: #16283f; color: #e6f1ff;
    font-size: 14px; outline: none;
  }
  select:focus, input[type="text"]:focus { border-color: #4fc3f7; }
  button {
    width: 100%; margin-top: 12px; padding: 10px; border: none;
    border-radius: 8px; background: #4fc3f7; color: #0a1929;
    font-weight: 600; font-size: 14px; cursor: pointer; transition: background 0.2s;
  }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
  button:hover:not(:disabled) { background: #7fd8ff; }
  #status { margin-top: 16px; text-align: center; font-size: 13px; min-height: 18px; }
  .ok { color: #4fd68c; }
  .error { color: #ff6b6b; }
  .dot { height: 8px; width: 8px; background: #4fd68c; border-radius: 50%; display: inline-block; }
</style>
</head>
<body>

<div class="container">
  <h1>TFT Display Controller</h1>
  <div class="subtitle"><span class="dot"></span> Connected via {{ port }}</div>

  <div class="section">
    <h2>🎞️ Animation Mode</h2>
    <select id="animSelect">
      {% for a in animations %}
      <option value="{{ a.id }}">{{ a.name }}</option>
      {% endfor %}
    </select>
    <button id="animBtn" onclick="applyAnimation()">Apply Animation</button>
  </div>

  <div class="section">
    <h2>📢 Wireless Noticeboard</h2>
    <input type="text" id="noticeText" placeholder="Type your message...">
    <button id="noticeBtn" onclick="sendNotice()">Send to Display</button>
  </div>

  <div id="status"></div>
</div>

<script>
function setStatus(msg, isError) {
  const el = document.getElementById("status");
  el.textContent = msg;
  el.className = isError ? "error" : "ok";
}

function setBusy(btn, busy) {
  btn.disabled = busy;
}

function applyAnimation() {
  const btn = document.getElementById("animBtn");
  const animId = document.getElementById("animSelect").value;
  setBusy(btn, true);
  setStatus("Sending...", false);
  fetch("/set_animation", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({anim_id: parseInt(animId)})
  })
  .then(r => r.json())
  .then(data => {
    setStatus(data.message, data.status !== "ok");
    setBusy(btn, false);
  })
  .catch(err => {
    setStatus("Connection error: " + err, true);
    setBusy(btn, false);
  });
}

function sendNotice() {
  const btn = document.getElementById("noticeBtn");
  const text = document.getElementById("noticeText").value;
  if (!text.trim()) {
    setStatus("Please enter a message", true);
    return;
  }
  setBusy(btn, true);
  setStatus("Sending...", false);
  fetch("/send_message", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({text: text})
  })
  .then(r => r.json())
  .then(data => {
    setStatus(data.message, data.status !== "ok");
    setBusy(btn, false);
    if (data.status === "ok") document.getElementById("noticeText").value = "";
  })
  .catch(err => {
    setStatus("Connection error: " + err, true);
    setBusy(btn, false);
  });
}
</script>

</body>
</html>
"""


# =====================================================
#                  ROUTES
# =====================================================
@app.route("/")
def index():
    return render_template_string(INDEX_HTML, animations=ANIMATIONS, port=SERIAL_PORT)


@app.route("/set_animation", methods=["POST"])
def set_animation():
    data = request.get_json()
    anim_id = data.get("anim_id")
    ok, msg = send_command(f"ANIM,{anim_id}")
    if ok:
        return jsonify({"status": "ok", "message": f"Animation {anim_id} applied"})
    return jsonify({"status": "error", "message": msg}), 500


@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"status": "error", "message": "Message cannot be empty"}), 400
    ok, msg = send_command(f"NOTICE,{text}")
    if ok:
        return jsonify({"status": "ok", "message": "Notice sent"})
    return jsonify({"status": "error", "message": msg}), 500


if __name__ == "__main__":
    open_serial()   # connect once, at real startup
    # use_reloader=False is CRITICAL — the default reloader runs this file
    # twice (two processes), which fights over COM5 and causes exactly the
    # random "sometimes works, sometimes doesn't" behavior you saw.
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000)