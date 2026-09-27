"""
Builds the kid-friendly circuit cards in docs/ from data.py.

    python tools/circuit_cards/build.py          # write docs/
    python tools/circuit_cards/build.py --check  # exit 1 if docs/ is out of date (used by CI)

Output:
    docs/index.html            all cards + the wiring rules
    docs/cards/<slug>.html     one card per project
    docs/cards.css, cards.js   shared style and checklist script
"""
import html, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from data import PROJECTS, LEARNING, PYTHON  # noqa: E402

REPO = "https://github.com/narendrakumarachari/hana-projects"
E = html.escape

# ------------------------------------------------------------------ colours
RED, BLACK = "#e53935", "#263238"
SIGNAL = ["#f9a825", "#2e9e4f", "#1e88e5", "#f57c00", "#8e24aa", "#6d4c41", "#d81b60", "#00acc1",
          "#7cb342", "#5c6bc0", "#ef6c00", "#00897b", "#c0ca33", "#546e7a", "#ad1457", "#3949ab"]
DARK_TEXT = {"#f9a825", "#00acc1", "#7cb342", "#c0ca33"}
RAIL_PLUS, RAIL_MINUS = "#e53935", "#1e63c6"
POWER = {"5V", "3V3", "VIN"}

# ------------------------------------------------------------------ parts
PART_PINS = {
    "led": ["+", "−"], "rgb": ["R", "G", "B", "−"], "buzzer_p": ["+", "−"], "buzzer_a": ["+", "−"],
    "button": ["leg 1", "leg 2"], "sound": ["AO", "GND", "VCC", "DO"], "hcsr04": ["VCC", "TRIG", "ECHO", "GND"],
    "ldr": ["VCC", "OUT", "GND"], "pir": ["VCC", "OUT", "GND"], "dht11": ["VCC", "DATA", "GND"],
    "servo": ["GND", "5V", "SIG"], "lcd": ["GND", "VCC", "SDA", "SCL"], "ir": ["OUT", "GND", "VCC"],
    "rc522": ["SDA", "SCK", "MOSI", "MISO", "IRQ", "GND", "RST", "3.3V"], "max7219": ["VCC", "GND", "DIN", "CS", "CLK"],
    "joystick": ["GND", "+5V", "VRx", "VRy", "SW"], "mpu6050": ["VCC", "GND", "SCL", "SDA"],
    "st7789": ["GND", "VCC", "SCL", "SDA", "RES", "DC", "CS", "BLK"],
}
PART_INFO = {  # glossary: name, what it does
    "led": ("LED", "A tiny light. The long leg is +. Always use a 220Ω resistor so it doesn't burn out."),
    "rgb": ("RGB LED", "Three lights (red, green, blue) in one. The longest leg is ground (−)."),
    "ledrow": ("LED row", "10 LEDs in a line on the breadboard, each with its own 220Ω resistor."),
    "buzzer_p": ("Passive buzzer", "Can play music notes with tone(). Long leg is +."),
    "buzzer_a": ("Active buzzer", "Beeps one sound by itself when switched on. Long leg is +. Often has a sticker on top."),
    "button": ("Push button", "Connects its legs while you press it. Use two legs on opposite corners."),
    "buttons": ("Buttons", "Several push buttons. One leg of each goes to a pin, the other legs all go to ground."),
    "sound": ("Sound sensor", "Hears sound. DO says loud / quiet, AO gives a loudness number. Blue screw = sensitivity."),
    "hcsr04": ("Distance sensor", "Sends a sound you can't hear and times the echo, like a bat."),
    "ldr": ("Light sensor (LDR)", "Changes with light. Paired with a 10kΩ resistor so the Uno can read a number."),
    "pir": ("Motion sensor (PIR)", "Notices warm bodies moving. Needs about 1 minute to wake up."),
    "dht11": ("Temperature sensor", "Measures temperature and humidity."),
    "servo": ("Servo motor", "Turns to an exact angle, 0° to 180°. Wires: brown = GND, red = 5V, orange = signal."),
    "lcd": ("LCD screen (I2C)", "Shows 2 lines of 16 letters, using just 2 data wires (SDA, SCL)."),
    "ir": ("IR receiver", "Sees the invisible light from a TV remote."),
    "rc522": ("RFID reader", "Reads ID cards and key tags. Uses 3.3V only!"),
    "max7219": ("LED matrix", "64 red dots in an 8×8 grid for letters and pictures."),
    "joystick": ("Joystick", "Two sliders (X and Y) that give numbers, plus a click button."),
    "mpu6050": ("Tilt sensor", "Feels which way it is tilted."),
    "st7789": ("Colour screen", "A small 240×240 full-colour screen. 3.3V only."),
}


def part_pins(p):
    if p["type"] == "ledrow":
        return [str(i) for i in range(1, 11)] + ["GND"]
    if p["type"] == "buttons":
        return [str(i) for i in range(1, p["n"] + 1)] + ["GND"]
    return PART_PINS[p["type"]]


def icon(t, cx, cy, p=None):
    """Small recognizable drawing of a part, about 150x62, centred at cx, cy."""
    s = []
    a = s.append
    if t == "led":
        a(f'<rect x="{cx-40}" y="{cy-3}" width="26" height="8" rx="3" fill="#d9c7a3"/>')
        for i, c in enumerate(["#8d6e63", "#000", "#6d4c41"]):
            a(f'<rect x="{cx-36+i*7}" y="{cy-3}" width="3" height="8" fill="{c}"/>')
        a(f'<path d="M{cx+2} {cy+14} v-20 a14 14 0 0 1 28 0 v20 z" fill="#ef5350" stroke="#b71c1c" stroke-width="2"/>')
        a(f'<ellipse cx="{cx+11}" cy="{cy-10}" rx="4" ry="6" fill="#fff" opacity=".5"/>')
    elif t == "rgb":
        a(f'<path d="M{cx-14} {cy+16} v-22 a14 14 0 0 1 28 0 v22 z" fill="#eceff1" stroke="#90a4ae" stroke-width="2"/>')
        for i, c in enumerate(["#e53935", "#43a047", "#1e88e5"]):
            a(f'<circle cx="{cx-7+i*7}" cy="{cy-4}" r="3.5" fill="{c}"/>')
    elif t == "ledrow":
        for i in range(10):
            x = cx - 68 + i * 15
            a(f'<path d="M{x-5} {cy+10} v-12 a5 5 0 0 1 10 0 v12 z" fill="#ef5350" stroke="#b71c1c" stroke-width="1"/>')
            a(f'<rect x="{x-2}" y="{cy+12}" width="4" height="10" fill="#d9c7a3"/>')
    elif t in ("buzzer_p", "buzzer_a"):
        a(f'<circle cx="{cx}" cy="{cy}" r="26" fill="#1c1c1c"/><circle cx="{cx}" cy="{cy}" r="5" fill="#555"/>')
        if t == "buzzer_a":
            a(f'<rect x="{cx-14}" y="{cy-8}" width="28" height="16" rx="3" fill="#fafafa" opacity=".9"/>')
            a(f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="9" font-family="Atkinson Hyperlegible, sans-serif" fill="#333">ACTIVE</text>')
        a(f'<text x="{cx+18}" y="{cy-14}" font-size="16" font-weight="800" font-family="Baloo 2, sans-serif" fill="#fff">+</text>')
    elif t == "button":
        a(f'<rect x="{cx-20}" y="{cy-20}" width="40" height="40" rx="4" fill="#37474f"/><circle cx="{cx}" cy="{cy}" r="12" fill="#e53935"/>')
    elif t == "buttons":
        n = p["n"] if p else 5
        for i in range(n):
            x = cx - (n - 1) * 17 + i * 34
            a(f'<rect x="{x-14}" y="{cy-14}" width="28" height="28" rx="3" fill="#37474f"/><circle cx="{x}" cy="{cy}" r="8" fill="#e53935"/>')
            a(f'<text x="{x}" y="{cy+28}" text-anchor="middle" font-size="10" font-family="JetBrains Mono, monospace" fill="#455a64">{i+1}</text>')
    elif t == "sound":
        a(f'<rect x="{cx-50}" y="{cy-18}" width="100" height="36" rx="4" fill="#1f5fae"/>')
        a(f'<circle cx="{cx-28}" cy="{cy}" r="13" fill="#b0bec5"/><circle cx="{cx-28}" cy="{cy}" r="8" fill="#546e7a"/>')
        a(f'<rect x="{cx+6}" y="{cy-10}" width="18" height="18" fill="#1565c0" stroke="#90caf9"/><circle cx="{cx+15}" cy="{cy-1}" r="4" fill="#e3f2fd"/>')
    elif t == "hcsr04":
        a(f'<rect x="{cx-62}" y="{cy-26}" width="124" height="52" rx="5" fill="#1f5fae"/>')
        for dx in (-32, 32):
            a(f'<circle cx="{cx+dx}" cy="{cy}" r="22" fill="#c7cdd2"/><circle cx="{cx+dx}" cy="{cy}" r="15" fill="#8e979e"/><circle cx="{cx+dx}" cy="{cy}" r="8" fill="#5e676e"/>')
    elif t == "ldr":
        a(f'<circle cx="{cx-22}" cy="{cy}" r="16" fill="#ffcc80" stroke="#e65100" stroke-width="2"/>')
        a(f'<path d="M{cx-32} {cy-6} h8 v6 h-8 v6 h20 v-6 h-8 v-6 h8" fill="none" stroke="#bf360c" stroke-width="2"/>')
        a(f'<rect x="{cx+6}" y="{cy-4}" width="36" height="9" rx="3" fill="#d9c7a3"/>')
        for i, c in enumerate(["#6d4c41", "#000", "#f57c00"]):
            a(f'<rect x="{cx+12+i*8}" y="{cy-4}" width="3" height="9" fill="{c}"/>')
        a(f'<text x="{cx+24}" y="{cy+22}" text-anchor="middle" font-size="9" font-family="JetBrains Mono, monospace" fill="#455a64">10kΩ</text>')
    elif t == "pir":
        a(f'<rect x="{cx-36}" y="{cy+2}" width="72" height="18" rx="3" fill="#2e7d32"/><path d="M{cx-26} {cy+4} a26 26 0 0 1 52 0 z" fill="#fafafa" stroke="#bdbdbd"/>')
    elif t == "dht11":
        a(f'<rect x="{cx-20}" y="{cy-24}" width="40" height="48" rx="3" fill="#29b6f6"/>')
        for yy in range(-18, 20, 8):
            a(f'<rect x="{cx-14}" y="{cy+yy}" width="28" height="4" fill="#0277bd"/>')
    elif t == "servo":
        a(f'<rect x="{cx-36}" y="{cy-16}" width="72" height="34" rx="4" fill="#1e5aa8"/><circle cx="{cx+18}" cy="{cy-16}" r="9" fill="#fafafa"/>')
        a(f'<rect x="{cx+14}" y="{cy-36}" width="8" height="30" rx="4" fill="#fafafa"/>')
    elif t == "lcd":
        a(f'<rect x="{cx-66}" y="{cy-24}" width="132" height="48" rx="4" fill="#2e7d32"/><rect x="{cx-58}" y="{cy-16}" width="116" height="32" fill="#9ccc65"/>')
        a(f'<text x="{cx-52}" y="{cy-2}" font-size="11" font-family="JetBrains Mono, monospace" fill="#1b3d0f">Hello!</text>')
        a(f'<text x="{cx-52}" y="{cy+12}" font-size="11" font-family="JetBrains Mono, monospace" fill="#1b3d0f">16x2 I2C</text>')
    elif t == "ir":
        a(f'<rect x="{cx-26}" y="{cy-6}" width="52" height="24" rx="3" fill="#37474f"/><path d="M{cx-12} {cy+2} v-12 a12 12 0 0 1 24 0 v12 z" fill="#111"/>')
    elif t == "rc522":
        a(f'<rect x="{cx-50}" y="{cy-26}" width="100" height="52" rx="4" fill="#1f5fae"/>')
        a(f'<rect x="{cx-38}" y="{cy-18}" width="76" height="36" rx="6" fill="none" stroke="#ffd54f" stroke-width="2"/>')
        a(f'<rect x="{cx+30}" y="{cy-30}" width="36" height="24" rx="3" fill="#fafafa" stroke="#90a4ae" transform="rotate(12 {cx+48} {cy-18})"/>')
    elif t == "max7219":
        a(f'<rect x="{cx-30}" y="{cy-30}" width="60" height="60" rx="3" fill="#212121"/>')
        for i in range(8):
            for j in range(8):
                on = (i, j) in {(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (2, 3), (2, 4), (3, 2), (3, 5), (4, 1), (4, 6), (5, 0), (5, 7)}
                a(f'<circle cx="{cx-24.5+i*7}" cy="{cy-24.5+j*7}" r="2.4" fill="{"#ff5252" if on else "#4e342e"}"/>')
    elif t == "joystick":
        a(f'<rect x="{cx-26}" y="{cy-26}" width="52" height="52" rx="4" fill="#212121"/><circle cx="{cx}" cy="{cy}" r="16" fill="#424242"/><circle cx="{cx}" cy="{cy}" r="10" fill="#616161"/>')
    elif t == "mpu6050":
        a(f'<rect x="{cx-26}" y="{cy-20}" width="52" height="40" rx="3" fill="#1f5fae"/><rect x="{cx-8}" y="{cy-8}" width="16" height="16" fill="#111"/>')
    elif t == "st7789":
        a(f'<rect x="{cx-34}" y="{cy-32}" width="68" height="64" rx="6" fill="#111"/><rect x="{cx-28}" y="{cy-26}" width="56" height="52" fill="#4fc3f7"/>')
        a(f'<rect x="{cx-28}" y="{cy+8}" width="56" height="18" fill="#66bb6a"/><circle cx="{cx+14}" cy="{cy-14}" r="6" fill="#ffd54f"/>')
    return "".join(s)


# ------------------------------------------------------------------ boards
def uno_pins():
    top = ["AREF", "GND", "D13", "D12", "D11", "D10", "D9", "D8"]
    top2 = ["D7", "D6", "D5", "D4", "D3", "D2", "D1", "D0"]
    pins = {}
    for i, n in enumerate(top):
        pins[("T", i)] = (n, 130 + i * 22)
    for i, n in enumerate(top2):
        pins[("T", 8 + i)] = (n, 320 + i * 22)
    bot = ["IOREF", "RESET", "3V3", "5V", "GND", "GND", "VIN"]
    for i, n in enumerate(bot):
        pins[("B", i)] = (n, 170 + i * 22)
    for i in range(6):
        pins[("B", 7 + i)] = (f"A{i}", 340 + i * 22)
    return pins


ESP_TOP = ["VIN", "GND", "D13", "D12", "D14", "D27", "D26", "D25", "D33", "D32", "D35", "D34", "VN", "VP", "EN"]
ESP_BOT = ["3V3", "GND", "D15", "D2", "D4", "RX2", "TX2", "D5", "D18", "D19", "D21", "RX0", "TX0", "D22", "D23"]


def esp_pins():
    pins = {}
    for i, n in enumerate(ESP_TOP):
        pins[("T", i)] = (n, 55 + i * 30)
    for i, n in enumerate(ESP_BOT):
        pins[("B", i)] = (n, 55 + i * 30)
    return pins


BOARDS = {
    "uno": dict(w=520, h=330, pins=uno_pins, name="Arduino Uno"),
    "esp32": dict(w=530, h=220, pins=esp_pins, name="ESP32 DevKit"),
}
PWM = {"D3", "D5", "D6", "D9", "D10", "D11"}


def label_of(board, n):
    if board == "uno":
        if n.startswith("D"):
            num = n[1:]
            return ("~" if n in PWM else "") + num
        return {"3V3": "3.3V"}.get(n, n)
    return {"3V3": "3V3"}.get(n, n)


def draw_board(board, bx, by, used, builtin=None):
    b = BOARDS[board]
    w, h = b["w"], b["h"]
    pins = b["pins"]()
    s = []
    a = s.append
    if board == "uno":
        a(f'<rect x="{bx}" y="{by}" width="{w}" height="{h}" rx="18" fill="#0e7c86" stroke="#0a5c63" stroke-width="3"/>')
        a(f'<rect x="{bx-30}" y="{by+35}" width="70" height="62" rx="6" fill="#b8c2c8" stroke="#8a969d" stroke-width="2"/>')
        a(f'<text x="{bx+5}" y="{by+72}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="13" font-weight="700" fill="#44525a">USB</text>')
        a(f'<rect x="{bx-26}" y="{by+230}" width="60" height="56" rx="8" fill="#232323"/>')
        a(f'<rect x="{bx+240}" y="{by+150}" width="210" height="46" rx="4" fill="#1c1c1c"/>')
        a(f'<text x="{bx+110}" y="{by+180}" font-family="Baloo 2, sans-serif" font-weight="800" font-size="40" fill="#fff">UNO</text>')
        a(f'<text x="{bx+112}" y="{by+204}" font-family="Atkinson Hyperlegible, sans-serif" font-size="14" fill="#bfe6e8">Arduino</text>')
        a(f'<rect x="{bx+118}" y="{by+14}" width="178" height="22" rx="3" fill="#1c1c1c"/><rect x="{bx+308}" y="{by+14}" width="178" height="22" rx="3" fill="#1c1c1c"/>')
        a(f'<rect x="{bx+158}" y="{by+h-36}" width="156" height="22" rx="3" fill="#1c1c1c"/><rect x="{bx+328}" y="{by+h-36}" width="134" height="22" rx="3" fill="#1c1c1c"/>')
        a(f'<text x="{bx+300}" y="{by+72}" text-anchor="middle" font-family="Atkinson Hyperlegible, sans-serif" font-weight="700" font-size="12" fill="#bfe6e8" letter-spacing="1.5">DIGITAL PINS</text>')
        a(f'<text x="{bx+236}" y="{by+h-86}" text-anchor="middle" font-family="Atkinson Hyperlegible, sans-serif" font-weight="700" font-size="12" fill="#bfe6e8" letter-spacing="1.5">POWER</text>')
        a(f'<text x="{bx+395}" y="{by+h-74}" text-anchor="middle" font-family="Atkinson Hyperlegible, sans-serif" font-weight="700" font-size="12" fill="#bfe6e8" letter-spacing="1.5">ANALOG IN</text>')
        a(f'<text x="{bx+439}" y="{by+h-6}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="9" fill="#bfe6e8">SDA SCL</text>')
        a(f'<g><circle cx="{bx+470}" cy="{by+100}" r="5" fill="#ffb300"/><text x="{bx+482}" y="{by+104}" font-family="JetBrains Mono, monospace" font-size="10" fill="#d8f1f2">L (13)</text></g>')
    else:
        a(f'<rect x="{bx}" y="{by}" width="{w}" height="{h}" rx="12" fill="#1f2a30" stroke="#0f1519" stroke-width="3"/>')
        a(f'<rect x="{bx-26}" y="{by+85}" width="44" height="50" rx="5" fill="#b8c2c8" stroke="#8a969d" stroke-width="2"/>')
        a(f'<text x="{bx-4}" y="{by+114}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="11" font-weight="700" fill="#44525a">USB</text>')
        a(f'<rect x="{bx+250}" y="{by+50}" width="200" height="120" rx="6" fill="#aab4ba" stroke="#7d878d" stroke-width="2"/>')
        a(f'<text x="{bx+350}" y="{by+108}" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="30" fill="#2b3439">ESP32</text>')
        a(f'<text x="{bx+350}" y="{by+130}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="11" fill="#2b3439">WROOM-32</text>')
        a(f'<path d="M{bx+460} {by+70} h20 v16 h-14 v16 h14 v16 h-14 v16 h14 v14" fill="none" stroke="#c9a227" stroke-width="3"/>')
        a(f'<text x="{bx+140}" y="{by+104}" text-anchor="middle" font-family="Atkinson Hyperlegible, sans-serif" font-weight="700" font-size="12" fill="#9fb2bb" letter-spacing="1">3.3 VOLT BOARD</text>')
        a(f'<rect x="{bx+60}" y="{by+130}" width="20" height="12" rx="2" fill="#555"/><text x="{bx+70}" y="{by+156}" text-anchor="middle" font-size="9" font-family="JetBrains Mono, monospace" fill="#9fb2bb">EN</text>')
        a(f'<rect x="{bx+190}" y="{by+130}" width="20" height="12" rx="2" fill="#555"/><text x="{bx+200}" y="{by+156}" text-anchor="middle" font-size="9" font-family="JetBrains Mono, monospace" fill="#9fb2bb">BOOT</text>')
        glow = builtin is not None
        ring = ' stroke="#fff" stroke-width="3"' if glow else ""
        a(f'<circle cx="{bx+120}" cy="{by+140}" r="{8 if glow else 5}" fill="#29b6f6"{ring}/>')
        a(f'<text x="{bx+120}" y="{by+165}" text-anchor="middle" font-size="9" font-family="JetBrains Mono, monospace" fill="#9fb2bb">LED (pin 2)</text>')
        a(f'<rect x="{bx+40}" y="{by+12}" width="{w-80}" height="22" rx="3" fill="#111"/><rect x="{bx+40}" y="{by+h-34}" width="{w-80}" height="22" rx="3" fill="#111"/>')
    # pins + labels
    for (row, i), (name, ox) in pins.items():
        x = bx + ox
        if board == "uno":
            py = by + 20 if row == "T" else by + h - 30
        else:
            py = by + 18 if row == "T" else by + h - 28
        a(f'<rect x="{x-5}" y="{py}" width="10" height="10" fill="#4a4a4a"/>')
        lab = E(label_of(board, name))
        if row == "T":
            ly = by + 50 if board == "uno" else by + 48
        else:
            if board == "uno":
                ly = by + h - 44 - (12 if i % 2 else 0)
            else:
                ly = by + h - 40
        col = "#d8f1f2" if board == "uno" else "#e0e6ea"
        weight = ' font-weight="700"' if (row, i) in used else ""
        a(f'<text x="{x}" y="{ly}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="{10 if board == "uno" else 11}"{weight} fill="{col}">{lab}</text>')
    for key, color in used.items():
        name, ox = pins[key]
        x = bx + ox
        py = (by + 16 if key[0] == "T" else by + h - 34) if board == "uno" else (by + 14 if key[0] == "T" else by + h - 32)
        a(f'<rect x="{x-8}" y="{py}" width="16" height="18" rx="3" fill="none" stroke="{color}" stroke-width="3"/>')
    return "".join(s)


def board_pin_xy(board, bx, by, key):
    b = BOARDS[board]
    name, ox = b["pins"]()[key]
    if key[0] == "T":
        return (bx + ox, by + (16 if board == "uno" else 14)), (0, -1)
    return (bx + ox, by + b["h"] - (16 if board == "uno" else 14)), (0, 1)


# ------------------------------------------------------------------ layout
PW, PH = 240, 150


def plan(proj):
    """Decide pin assignment, rails, part slots. Returns a layout dict."""
    board = proj["board"]
    pins = BOARDS[board]["pins"]()
    by_name = {}
    for k, (n, _) in pins.items():
        by_name.setdefault(n, []).append(k)
    vcc = "3V3" if board == "esp32" else "5V"
    wires = proj["wires"]
    n_vcc = sum(1 for w in wires if w[2] == vcc)
    n_gnd = sum(1 for w in wires if w[2] == "GND")
    rails = n_vcc > 1 or n_gnd > len(by_name["GND"])
    parts = proj["parts"]
    # slot: by signal pin rows
    slot = {}
    counts = {"top": 0, "bottom": 0, "right": 0, "left": 0}
    cap = {"top": 4, "bottom": 4, "right": 2, "left": 1}
    for p in parts:
        rows = [by_name[w[2]][0][0] for w in wires if w[0] == p["id"] and w[2] not in POWER and w[2] != "GND" and w[2] in by_name]
        pref = "bottom" if rows and rows.count("B") > rows.count("T") else "top"
        if p.get("slot"):
            pref = p["slot"]
        order = [pref, "bottom" if pref == "top" else "top", "right", "left"]
        for s_ in order:
            if counts[s_] < cap[s_]:
                slot[p["id"]] = s_
                counts[s_] += 1
                break
    return dict(rails=rails, vcc=vcc, slot=slot, counts=counts, by_name=by_name)


def bez(p0, n0, p3, n3):
    d = math.hypot(p3[0] - p0[0], p3[1] - p0[1])
    k = max(40, min(170, d / 2.4))
    c1 = (p0[0] + n0[0] * k, p0[1] + n0[1] * k)
    c2 = (p3[0] + n3[0] * k, p3[1] + n3[1] * k)
    return p0, c1, c2, p3


def bez_pt(b, t):
    p0, c1, c2, p3 = b
    u = 1 - t
    return (u**3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t**3 * p3[1])


def diagram(proj):
    """Returns (svg, checklist rows)."""
    board = proj["board"]
    L = plan(proj)
    b = BOARDS[board]
    W = 1180
    bw, bh = b["w"], b["h"]
    slot, counts, rails, vcc = L["slot"], L["counts"], L["rails"], L["vcc"]
    parts = {p["id"]: p for p in proj["parts"]}
    top_parts = [p for p in proj["parts"] if slot.get(p["id"]) == "top"]
    bot_parts = [p for p in proj["parts"] if slot.get(p["id"]) == "bottom"]
    side_parts = [p for p in proj["parts"] if slot.get(p["id"]) in ("right", "left")]
    needs_top_rail = rails and any(slot[w[0]] in ("top", "right", "left") for w in proj["wires"] if w[2] in (vcc, "GND"))
    y = 24
    top_y = y
    if top_parts:
        y += PH + 70
    rail_top_y = None
    if needs_top_rail:
        rail_top_y = y
        y += 26 + 70
    by = y
    y += bh + 70
    rail_bot_y = None
    if rails:
        rail_bot_y = y
        y += 26 + 70
    bot_y = y
    if bot_parts:
        y += PH + 30
    H = max(y, by + bh + 40)
    bx = (W - bw) // 2
    rail_x0, rail_x1 = bx - 150, bx + bw + 150

    # --- part boxes & pin coordinates
    part_svg = []
    pin_xy = {}

    def place_row(plist, py, edge):
        n = len(plist)
        total = n * PW + (n - 1) * 24
        x0 = (W - total) // 2
        for i, p in enumerate(plist):
            px = x0 + i * (PW + 24)
            draw_part(p, px, py, edge)

    def draw_part(p, px, py, edge):
        names = part_pins(p)
        n = len(names)
        h = PH if edge in ("bottom", "top") else max(PH, 50 + n * 26)
        g = []
        g.append(f'<rect x="{px}" y="{py}" width="{PW}" height="{h}" rx="14" fill="#ffffff" stroke="#b9c7cc" stroke-width="2"/>')
        if edge == "bottom":        # part above the board: pins on its bottom edge
            g.append(icon(p["type"], px + PW / 2, py + 64, p))
            g.append(f'<text x="{px+PW/2}" y="{py+22}" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="16" fill="#16242c">{E(p["label"])}</text>')
            sp = min(46, (PW - 24) / max(n, 1))
            x0 = px + PW / 2 - sp * (n - 1) / 2
            fs = 11 if n <= 8 else 9.5
            for i, nm in enumerate(names):
                x = x0 + i * sp
                g.append(f'<rect x="{x-4}" y="{py+h}" width="8" height="14" fill="#d9b44a"/>')
                g.append(f'<text x="{x}" y="{py+h-10}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-weight="700" font-size="{fs}" fill="#1f5fae">{E(nm)}</text>')
                pin_xy[(p["id"], nm)] = ((x, py + h + 14), (0, 1))
        elif edge == "top":         # part below the board: pins on its top edge
            g.append(icon(p["type"], px + PW / 2, py + 84, p))
            g.append(f'<text x="{px+PW/2}" y="{py+h-12}" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="16" fill="#16242c">{E(p["label"])}</text>')
            sp = min(46, (PW - 24) / max(n, 1))
            x0 = px + PW / 2 - sp * (n - 1) / 2
            fs = 11 if n <= 8 else 9.5
            for i, nm in enumerate(names):
                x = x0 + i * sp
                g.append(f'<rect x="{x-4}" y="{py-14}" width="8" height="14" fill="#d9b44a"/>')
                g.append(f'<text x="{x}" y="{py+18}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-weight="700" font-size="{fs}" fill="#1f5fae">{E(nm)}</text>')
                pin_xy[(p["id"], nm)] = ((x, py - 14), (0, -1))
        else:                       # side part: pins on the edge facing the board
            left_edge = edge == "left"
            ex = px if left_edge else px + PW
            dirx = -1 if left_edge else 1
            g.append(icon(p["type"], px + (PW * 0.64 if left_edge else PW * 0.36), py + h / 2 - 8, p))
            g.append(f'<text x="{px+(PW*0.64 if left_edge else PW*0.36)}" y="{py+h-14}" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="15" fill="#16242c">{E(p["label"])}</text>')
            y0 = py + h / 2 - 13 * (n - 1)
            for i, nm in enumerate(names):
                yy = y0 + i * 26
                sx = ex - 14 if left_edge else ex
                g.append(f'<rect x="{sx}" y="{yy-4}" width="14" height="8" fill="#d9b44a"/>')
                tx = ex + 10 if left_edge else ex - 10
                g.append(f'<text x="{tx}" y="{yy+4}" text-anchor="{"start" if left_edge else "end"}" font-family="JetBrains Mono, monospace" font-weight="700" font-size="11" fill="#1f5fae">{E(nm)}</text>')
                pin_xy[(p["id"], nm)] = ((ex + 14 * dirx, yy), (dirx, 0))
        part_svg.append("".join(g))

    if top_parts:
        place_row(top_parts, top_y, "bottom")
    if bot_parts:
        place_row(bot_parts, bot_y, "top")
    ry = by
    ly = by
    for p in side_parts:
        n = len(part_pins(p))
        h = max(PH, 50 + n * 26)
        if slot[p["id"]] == "right":
            draw_part(p, W - PW - 16, ry, "left")   # pins on its left edge
            ry += h + 20
        else:
            draw_part(p, 16, ly, "right")
            ly += h + 20
    H = max(H, ry, ly)

    # --- wires
    pins_by_name = L["by_name"]
    used_board = {}
    free = {k: list(v) for k, v in pins_by_name.items()}
    rows = []       # checklist rows
    paths = []
    tags = []
    color_i = [0]

    def next_color():
        c = SIGNAL[color_i[0] % len(SIGNAL)]
        color_i[0] += 1
        return c

    def take(name, prefer_row):
        cands = free.get(name, [])
        if not cands:
            return pins_by_name[name][0]
        cands.sort(key=lambda k: 0 if k[0] == prefer_row else 1)
        k = cands.pop(0)
        return k

    def add_wire(p0, n0, p3, n3, color, num):
        bz = bez(p0, n0, p3, n3)
        d = f'M{bz[0][0]:.1f} {bz[0][1]:.1f} C {bz[1][0]:.1f} {bz[1][1]:.1f}, {bz[2][0]:.1f} {bz[2][1]:.1f}, {bz[3][0]:.1f} {bz[3][1]:.1f}'
        paths.append(f'<path d="{d}" stroke="#ffffff" stroke-width="11"/><path d="{d}" stroke="{color}" stroke-width="6.5"/>')
        best, bestd = None, -1
        for t in (0.5, 0.4, 0.6, 0.3, 0.7, 0.22, 0.78):
            pt = bez_pt(bz, t)
            md = min([math.hypot(pt[0] - q[0], pt[1] - q[1]) for q in tags] + [999])
            if md > 34:
                best = pt
                break
            if md > bestd:
                best, bestd = pt, md
        tags.append((best[0], best[1], color, num))

    num = 0
    if rails:
        vk = take(vcc, "B")
        gk = take("GND", "B")
        for key, color, rail_y, label in ((vk, RED, rail_bot_y, f"{label_of(board, vcc)}"), (gk, BLACK, rail_bot_y + 26, "GND")):
            num += 1
            used_board[key] = color
            p3, n3 = board_pin_xy(board, bx, by, key)
            add_wire(p3, n3, (p3[0], rail_y), (0, -1), color, num)
            rows.append(dict(n=num, color=color, frm=f'{"Uno" if board == "uno" else "ESP32"} <span class="pin">{E(label_of(board, pins_by_name[vcc][0] and pins_by_name["GND"] and (vcc if color == RED else "GND")))}</span>',
                             to=f'breadboard <span class="pin rail {"plus" if color == RED else "minus"}">{"+ strip" if color == RED else "− strip"}</span>',
                             why="power for everything" if color == RED else "ground for everything"))
        if needs_top_rail:
            for color, y1, y2, x, lab in ((RED, rail_bot_y, rail_top_y, rail_x0 + 12, "+"), (BLACK, rail_bot_y + 26, rail_top_y + 26, rail_x0 + 30, "−")):
                num += 1
                paths.append(f'<path d="M{x} {y1} L {x} {y2}" stroke="#ffffff" stroke-width="11"/><path d="M{x} {y1} L {x} {y2}" stroke="{color}" stroke-width="6.5"/>')
                tags.append((x - 22 if lab == "+" else x + 22, (y1 + y2) / 2, color, num))
                rows.append(dict(n=num, color=color, frm=f'bottom <span class="pin rail {"plus" if lab == "+" else "minus"}">{lab} strip</span>',
                                 to=f'top <span class="pin rail {"plus" if lab == "+" else "minus"}">{lab} strip</span>', why="connects the two power strips"))

    for (pid, ppin, bpin, why) in proj["wires"]:
        p = parts[pid]
        num += 1
        start, n0 = pin_xy[(pid, ppin)]
        is_power = bpin in (vcc, "GND") and rails
        if bpin == "GND":
            color = BLACK
        elif bpin in POWER:
            color = RED
        else:
            color = next_color()
        if is_power:
            s_ = slot[pid]
            if s_ == "bottom":
                ry_ = rail_bot_y + (26 if bpin == "GND" else 0)
                end, n3 = (min(max(start[0], rail_x0 + 50), rail_x1 - 10), ry_), (0, 1)
            else:
                ry_ = rail_top_y + (26 if bpin == "GND" else 0)
                end, n3 = (min(max(start[0], rail_x0 + 50), rail_x1 - 10), ry_), (0, -1)
            add_wire(start, n0, end, n3, color, num)
            to = f'breadboard <span class="pin rail {"minus" if bpin == "GND" else "plus"}">{"− strip" if bpin == "GND" else "+ strip"}</span>'
        else:
            prefer = "T" if slot[pid] == "top" else "B"
            key = take(bpin, prefer)
            used_board[key] = color
            end, n3 = board_pin_xy(board, bx, by, key)
            add_wire(start, n0, end, n3, color, num)
            nice = label_of(board, bpin)
            where = ""
            if bpin == "GND":
                where = " <small>(top row)</small>" if key[0] == "T" else " <small>(bottom row)</small>"
            if board == "uno" and bpin in ("A4", "A5"):
                where = " <small>(" + ("SDA" if bpin == "A4" else "SCL") + ")</small>"
            pretty = f'pin <span class="pin">{E(nice)}</span>' if bpin.startswith(("D", "A")) else f'<span class="pin">{E(nice)}</span>'
            to = f'{"Uno" if board == "uno" else "ESP32"} {pretty}{where}'
        rows.append(dict(n=num, color=color, frm=f'{E(p["label"])} <span class="pin part-pin">{E(ppin)}</span>', to=to, why=E(why)))

    # --- assemble svg
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Wiring picture for {E(proj["title"])}: {len(rows)} wires, listed in the checklist below.">']
    s.append('<defs><pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.4" fill="#d5ddd4"/></pattern></defs>')
    s.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#dots)"/>')
    for ry_ in [r for r in (rail_top_y, rail_bot_y) if r is not None]:
        s.append(f'<rect x="{rail_x0}" y="{ry_-12}" width="{rail_x1-rail_x0}" height="50" rx="8" fill="#fbfbf8" stroke="#d0d6cf" stroke-width="2"/>')
        s.append(f'<line x1="{rail_x0+44}" y1="{ry_}" x2="{rail_x1-10}" y2="{ry_}" stroke="{RAIL_PLUS}" stroke-width="3"/>')
        s.append(f'<line x1="{rail_x0+44}" y1="{ry_+26}" x2="{rail_x1-10}" y2="{ry_+26}" stroke="{RAIL_MINUS}" stroke-width="3"/>')
        for xx in range(rail_x0 + 56, rail_x1 - 10, 18):
            s.append(f'<rect x="{xx-2}" y="{ry_-2}" width="4" height="4" fill="#bfc6be"/><rect x="{xx-2}" y="{ry_+24}" width="4" height="4" fill="#bfc6be"/>')
        s.append(f'<text x="{rail_x0+22}" y="{ry_+5}" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="16" fill="{RAIL_PLUS}">+</text>')
        s.append(f'<text x="{rail_x0+22}" y="{ry_+31}" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="16" fill="{RAIL_MINUS}">−</text>')
        s.append(f'<text x="{rail_x0-8}" y="{ry_+5}" text-anchor="end" font-family="JetBrains Mono, monospace" font-weight="700" font-size="13" fill="{RAIL_PLUS}">+{label_of(board, vcc)}</text>')
        s.append(f'<text x="{rail_x0-8}" y="{ry_+31}" text-anchor="end" font-family="JetBrains Mono, monospace" font-weight="700" font-size="13" fill="{RAIL_MINUS}">GND</text>')
    s.append(draw_board(board, bx, by, used_board, proj.get("builtin_led")))
    if proj.get("builtin_led"):
        s.append(f'<text x="{bx+120}" y="{by+bh+34}" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="18" fill="#0277bd">↑ this tiny blue LED is on pin 2: no wires needed!</text>')
    if not proj["parts"] and not proj.get("builtin_led"):
        s.append(f'<text x="{W/2}" y="{by+bh+40}" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="20" fill="#00838c">No wires: just plug in the USB cable!</text>')
        H2 = by + bh + 60
        s[0] = s[0].replace(f'viewBox="0 0 {W} {H}"', f'viewBox="0 0 {W} {H2}"')
    s.extend(part_svg)
    s.append('<g fill="none" stroke-linecap="round" stroke-linejoin="round">' + "".join(paths) + "</g>")
    s.append('<g font-family="Baloo 2, sans-serif" font-weight="800" font-size="15" text-anchor="middle">')
    for (x, y_, c, n) in tags:
        tc = "#3b2a00" if c in DARK_TEXT else "#ffffff"
        s.append(f'<circle cx="{x:.1f}" cy="{y_:.1f}" r="14" fill="{c}" stroke="#ffffff" stroke-width="3"/><text x="{x:.1f}" y="{y_+5:.1f}" fill="{tc}">{n}</text>')
    s.append("</g></svg>")
    return "".join(s), rows, rails


# ------------------------------------------------------------------ pages
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Atkinson+Hyperlegible:wght@400;700&family=JetBrains+Mono:wght@500;700&display=swap">')


def page(title, body, css_href, js_href, standalone=True):
    head = f'<title>{E(title)}</title>{FONTS}<link rel="stylesheet" href="{css_href}">'
    tail = f'<script src="{js_href}"></script>'
    if standalone:
        return (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
                f'{head}</head><body>{body}{tail}</body></html>\n')
    return f"{head}\n{body}{tail}\n"


def level(n):
    return ("★☆☆ Easy", 1) if n <= 1 else (("★★☆ Medium", 2) if n <= 3 else ("★★★ Big build", 3))


def lib_rows(libs):
    info = {
        "Servo": "Servo by Michael Margolis, Arduino", "MFRC522": "MFRC522 by GithubCommunity",
        "IRremote": "IRremote by shirriff, z3t0, ArminJo (version 4.x)", "LiquidCrystal I2C": "LiquidCrystal I2C by Frank de Brabander",
        "LedControl": "LedControl by Eberhard Fahle", "DHT sensor library": "DHT sensor library by Adafruit (click Install All)",
        "Adafruit ST7735 and ST7789": "Adafruit ST7735 and ST7789 Library (click Install All)", "Adafruit GFX": "Adafruit GFX Library (comes with the one above)",
    }
    return "".join(f"<li>{E(info.get(l, l))}</li>" for l in libs)


def arduino_card(p, all_by_slug):
    svg, rows, rails = ("", [], False) if p.get("wip") else diagram(p)
    n_parts = len(p["parts"])
    lv, _ = level(n_parts)
    board_name = BOARDS[p["board"]]["name"]
    ino = p["folder"].split("/")[-1] + ".ino"
    path_win = "HanaProjects\\" + p["folder"].replace("/", "\\") + "\\" + ino
    chips = [f'<span class="chip level">{lv}</span>', f'<span class="chip">{n_parts} part{"s" if n_parts != 1 else ""}</span>',
             f'<span class="chip">{len(rows)} wire{"s" if len(rows) != 1 else ""}</span>', f'<span class="chip board-{p["board"]}">Board: {board_name}</span>']
    if rails:
        chips.append('<span class="chip">Uses a breadboard</span>')
    out = [f'<main class="page"><nav class="crumbs"><a href="../index.html">← All circuit cards</a></nav>']
    out.append(f'<header class="hero"><div class="eyebrow">Hana\'s Circuit Cards · {E(p["group"])}</div><h1>{E(p["title"])}</h1>'
               f'<p class="lead">{p["what"]}</p><div class="chips">{"".join(chips)}</div></header>')
    if p.get("showcase"):
        out.append(SHOWCASE_BANNER)
    if p["board"] == "esp32":
        out.append('<div class="banner esp">⚡ <b>ESP32 = 3.3 volts.</b> Never connect 5V to an ESP32 pin. Everything on this card uses the <b>3V3</b> pin.</div>')
    if p.get("wip"):
        out.append('<section><div class="tip warn"><h3>Not started yet</h3><p>This project has no code yet, so there is nothing to wire. When it has code, add it to <code>tools/circuit_cards/data.py</code> and rebuild the cards.</p></div></section>')
    else:
        step = 1
        # parts
        items = "".join(f'<div class="part"><svg viewBox="0 0 150 84" role="img" aria-label="{E(q["label"])}">{icon(q["type"], 75, 42, q)}</svg><b>{E(q["label"])}</b><span>{E(PART_INFO[q["type"]][1])}</span></div>' for q in p["parts"])
        extras = '<div class="part"><svg viewBox="0 0 150 84" role="img" aria-label="USB cable"><path d="M20 60 C 60 80, 90 10, 128 30" stroke="#6b7a83" stroke-width="7" fill="none" stroke-linecap="round"/><rect x="8" y="50" width="22" height="18" rx="3" fill="#b8c2c8"/><rect x="120" y="22" width="24" height="16" rx="3" fill="#b8c2c8"/></svg><b>USB cable</b><span>connects the board to the computer</span></div>'
        if rows:
            extras += f'<div class="part"><svg viewBox="0 0 150 84" role="img" aria-label="Jumper wires"><g stroke-width="6" stroke-linecap="round" fill="none"><path d="M14 70 C 30 10, 50 10, 60 70" stroke="{RED}"/><path d="M34 70 C 50 20, 66 20, 76 70" stroke="{BLACK}"/><path d="M54 70 C 70 16, 86 16, 96 70" stroke="#f9a825"/><path d="M74 70 C 90 22, 106 22, 116 70" stroke="#2e9e4f"/><path d="M94 70 C 110 16, 126 16, 136 70" stroke="#1e88e5"/></g></svg><b>{len(rows)} jumper wires</b><span>any colours work; matching the picture helps</span></div>'
        if rails:
            extras += '<div class="part"><svg viewBox="0 0 150 84" role="img" aria-label="Breadboard"><rect x="8" y="14" width="134" height="56" rx="6" fill="#f5f5f0" stroke="#cfd3cc" stroke-width="2"/><line x1="16" y1="24" x2="134" y2="24" stroke="#e53935" stroke-width="2"/><line x1="16" y1="60" x2="134" y2="60" stroke="#1e63c6" stroke-width="2"/><g fill="#c3c8c0"><rect x="20" y="32" width="110" height="3"/><rect x="20" y="40" width="110" height="3"/><rect x="20" y="48" width="110" height="3"/></g></svg><b>Breadboard</b><span>its + and − strips share power with every part</span></div>'
        board_icon = ('<rect x="10" y="8" width="130" height="70" rx="8" fill="#0e7c86"/><text x="80" y="50" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="20" fill="#fff">UNO</text>'
                      if p["board"] == "uno" else '<rect x="10" y="20" width="130" height="46" rx="6" fill="#1f2a30"/><rect x="70" y="26" width="52" height="34" rx="3" fill="#aab4ba"/><text x="96" y="48" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="13" fill="#2b3439">ESP32</text>')
        items = f'<div class="part"><svg viewBox="0 0 150 84" role="img" aria-label="{board_name}">{board_icon}</svg><b>{board_name}</b><span>the brain</span></div>' + items + extras
        out.append(f'<section><div class="step-title"><span class="step-num">{step}</span><h2>Get your parts</h2></div><div class="parts">{items}</div></section>')
        step += 1
        # picture
        cap = "Every wire has a <b>colour</b> and a <b>number</b>. Find the same number in the checklist."
        if rails:
            cap += f" Parts get power from the breadboard's <b>+</b> strip ({label_of(p['board'], 'VCC' if False else ('3V3' if p['board']=='esp32' else '5V'))}) and <b>−</b> strip (GND)."
        out.append(f'<section><div class="step-title"><span class="step-num">{step}</span><h2>Look at the picture</h2></div><p class="hint">{cap}</p>'
                   f'<figure><div class="mat">{svg}</div><figcaption>Wire colours: <b style="color:{RED}">red = power</b>, <b>black = ground (GND)</b>, other colours = signals. Wires can cross over each other; that\'s normal.</figcaption></figure></section>')
        step += 1
        if rows:
            wl = []
            for r in rows:
                tc = "#3b2a00" if r["color"] in DARK_TEXT else "#fff"
                wl.append(f'<label class="wire" for="w{r["n"]}"><input type="checkbox" id="w{r["n"]}"><span class="swatch" style="background:{r["color"]}"></span>'
                          f'<span class="route"><span class="tag" style="background:{r["color"]};color:{tc}">{r["n"]}</span><span class="from">{r["frm"]}</span>'
                          f'<span class="arrow">→</span><span class="to">{r["to"]}</span><span class="why">{r["why"]}</span></span></label>')
            out.append(f'<section><div class="step-title"><span class="step-num">{step}</span><h2>Connect the wires, one at a time</h2></div>'
                       f'<p class="hint"><b>Unplug the USB cable first.</b> Tick each wire when it\'s in. <span class="progress" data-total="{len(rows)}" aria-live="polite"></span></p>'
                       f'<div class="wires" data-key="card-{p["slug"]}">{"".join(wl)}</div></section>')
            step += 1
        # program
        libs = p.get("libs", [])
        secret = ""
        if p.get("secrets"):
            secret = ('<li>First time only: in the project folder, copy <code>arduino_secrets.example.h</code> to <code>arduino_secrets.h</code> and type your Wi-Fi name and password in it. '
                      '<b>This file never goes to GitHub.</b></li>')
        board_step = ('<kbd>Tools</kbd> → <kbd>Board</kbd> → <b>Arduino Uno</b>' if p["board"] == "uno"
                      else '<kbd>Tools</kbd> → <kbd>Board</kbd> → <b>esp32</b> → <b>ESP32 Dev Module</b> (install "esp32 by Espressif" in Boards Manager the first time)')
        lib_html = (f'<div class="libs"><b>Libraries needed</b> (<kbd>Tools</kbd> → <kbd>Manage Libraries…</kbd>, search, click Install). Already inside <code>arduino/libraries</code> if the sketchbook is set to <code>HanaProjects\\arduino</code>:<ul>{lib_rows(libs)}</ul></div>'
                    if libs else '<p class="hint">No extra libraries needed.</p>')
        serial = p.get("serial")
        serial_li = (f'<li>Open <kbd>Tools</kbd> → <kbd>Serial Monitor</kbd> and set it to <b>{serial} baud</b> to see messages.</li>' if serial else "")
        out.append(f'<section><div class="step-title"><span class="step-num">{step}</span><h2>Upload the program</h2></div><div class="program">'
                   f'<div class="file"><span>Open this file:</span><code class="path">{E(path_win)}</code><button class="copy" type="button">Copy</button></div>'
                   f'<ol class="do">{secret}<li>Plug the board into the computer with the USB cable.</li><li>In the Arduino IDE: <kbd>File</kbd> → <kbd>Open…</kbd> → the file above.</li>'
                   f'<li>{board_step}.</li><li><kbd>Tools</kbd> → <kbd>Port</kbd> → the <b>COM</b> port that appears.</li>'
                   f'<li>Click <b>Upload</b> (the round <kbd>→</kbd> button) and wait for <b>"Done uploading"</b>.</li>{serial_li}</ol>{lib_html}</div></section>')
        step += 1
        # try
        tries = "".join(f"<li>{t}</li>" for t in p.get("try_", []))
        extra = ""
        if p.get("python"):
            q = p["python"]
            extra = f'<p class="hint">This project has a Python partner: <a href="{q}.html">{E(next(x["title"] for x in PYTHON if x["slug"] == q))}</a>.</p>'
        out.append(f'<section><div class="step-title"><span class="step-num">{step}</span><h2>Try it!</h2></div><ol class="do">{tries}</ol>{extra}</section>')
        step += 1
        # tips
        tips = list(p.get("tips", []))
        types = {q["type"] for q in p["parts"]}
        auto = []
        if types & {"led", "rgb", "ledrow"}:
            auto.append(("LED stays dark", "Turn the LED around: the <b>long leg</b> goes toward the pin (through the resistor), the short leg to GND.", False))
        if types & {"buzzer_p", "buzzer_a"}:
            auto.append(("No sound", "Check the buzzer's <b>long leg (+)</b> goes to the pin. A passive buzzer needs tone(); an active one beeps by itself.", False))
        if "hcsr04" in types:
            auto.append(("Distance always 0", "TRIG and ECHO may be swapped. Check them against the checklist.", False))
        if "lcd" in types:
            auto.append(("Screen lights up but no words", "Turn the small blue screw on the back of the screen. Still nothing? Run the <b>I2C Scanner</b> card: the address may be 0x3F.", False))
        if "servo" in types:
            auto.append(("Servo shakes or resets the board", "It needs more power: make sure it uses the 5V pin or strip, and all GNDs are connected.", False))
        if "sound" in types:
            auto.append(("Sensor always ON or always OFF", "Turn the blue screw on the sensor until its little LED is just off when it's quiet.", False))
        if types & {"button", "buttons"}:
            auto.append(("Button does nothing", "Buttons have 4 legs. Use two legs on <b>opposite corners</b>.", False))
        if "pir" in types:
            auto.append(("Motion always ON", "A PIR needs about 1 minute to settle after power-up.", False))
        if "rc522" in types or "st7789" in types or p["board"] == "esp32":
            auto.append(("3.3V only!", "The ESP32, the RFID reader and the colour screen are damaged by 5V.", True))
        auto.append(("Upload fails", "Close the Serial Monitor, check <kbd>Tools</kbd> → <kbd>Port</kbd>, unplug and replug the USB cable, try again.", False))
        tips.extend(auto)
        tip_html = "".join(f'<div class="tip{" warn" if w else ""}"><h3>{t}</h3><p>{d}</p></div>' for t, d, w in tips[:6])
        out.append(f'<section><div class="step-title"><span class="step-num">{step}</span><h2>If it doesn\'t work</h2></div><div class="tips">{tip_html}</div></section>')
    learn = ", ".join(p.get("learn", []))
    out.append(f'<footer><span><b>Program folder:</b> <a href="{REPO}/tree/main/{p["folder"]}"><code>{E(p["folder"])}</code></a> (old name <code>{E(p["old"])}</code>)</span>'
               + (f"<span><b>You'll learn:</b> {E(learn)}</span>" if learn else "")
               + '<span>Pins on this card are checked against the program code. To change a card, edit <code>tools/circuit_cards/data.py</code> and run <code>python tools/circuit_cards/build.py</code>.</span></footer></main>')
    return "".join(out)


def flow_svg(q):
    """Computer <-> board picture for Python companions."""
    s = ['<svg viewBox="0 0 900 250" role="img" aria-label="How the Python program connects to the board">']
    s.append('<rect x="0" y="0" width="900" height="250" fill="#f4f7f1"/>')
    # computer
    s.append('<rect x="40" y="40" width="240" height="150" rx="12" fill="#263238"/><rect x="54" y="54" width="212" height="112" rx="4" fill="#e3f2fd"/>')
    s.append('<rect x="20" y="190" width="280" height="16" rx="6" fill="#455a64"/>')
    s.append('<text x="160" y="96" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="20" fill="#0d47a1">Computer</text>')
    s.append(f'<text x="160" y="124" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="12" fill="#0d47a1">{E(q["file"].split("/")[-1])}</text>')
    if q["kind"] == "none":
        s.append('<text x="600" y="120" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="26" fill="#00838c">No wires needed!</text>')
        s.append('<text x="600" y="150" text-anchor="middle" font-family="Atkinson Hyperlegible, sans-serif" font-size="15" fill="#4a5d68">This program runs only on the computer.</text>')
    else:
        esp = q["kind"] == "wifi"
        bx = 620
        if esp:
            s.append(f'<rect x="{bx}" y="70" width="240" height="90" rx="10" fill="#1f2a30"/><rect x="{bx+120}" y="84" width="96" height="62" rx="5" fill="#aab4ba"/><text x="{bx+168}" y="122" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="18" fill="#2b3439">ESP32</text>')
        else:
            s.append(f'<rect x="{bx}" y="55" width="240" height="130" rx="14" fill="#0e7c86"/><text x="{bx+120}" y="128" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="30" fill="#fff">UNO</text>')
        sk = q.get("sketch") or "board program (not saved yet)"
        s.append(f'<text x="{bx+120}" y="214" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="12" fill="#16242c">{E(sk)}</text>')
        if esp:
            s.append('<path d="M300 120 C 400 60, 520 60, 610 115" fill="none" stroke="#1e88e5" stroke-width="4" stroke-dasharray="10 8"/>')
            s.append('<text x="455" y="58" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="18" fill="#1565c0">Wi-Fi (same network)</text>')
            s.append('<text x="455" y="150" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="12" fill="#4a5d68">http://ESP32-IP/on  /off</text>')
        else:
            s.append('<path d="M300 150 C 400 190, 520 190, 620 140" fill="none" stroke="#6b7a83" stroke-width="9" stroke-linecap="round"/>')
            s.append('<text x="460" y="128" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="18" fill="#37474f">USB cable</text>')
            s.append(f'<text x="460" y="224" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="12" fill="#4a5d68">COM5 · {q.get("baud", 9600)} baud</text>')
    s.append("</svg>")
    return "".join(s)


def python_card(q):
    out = ['<main class="page"><nav class="crumbs"><a href="../index.html">← All circuit cards</a></nav>']
    kind = {"usb": "Talks to an Arduino over USB", "wifi": "Talks to an ESP32 over Wi-Fi", "none": "No wires needed"}[q["kind"]]
    chips = [f'<span class="chip">Python</span>', f'<span class="chip">{kind}</span>']
    out.append(f'<header class="hero"><div class="eyebrow">Hana\'s Circuit Cards · Python</div><h1>{E(q["title"])}</h1><p class="lead">{q["what"]}</p><div class="chips">{"".join(chips)}</div></header>')
    if q.get("showcase"):
        out.append(SHOWCASE_BANNER)
    elif q.get("ngrok"):
        out.append('<a class="feature" href="../share-with-ngrok.html"><span class="feature-kicker">Share it with friends</span>'
                   '<b>Put this website online with ngrok</b><span>One command, <code>ngrok http 5000</code>, gives you a link friends can open from anywhere. See the step-by-step guide →</span></a>')
    out.append(f'<section><div class="step-title"><span class="step-num">1</span><h2>How it connects</h2></div><figure><div class="mat">{flow_svg(q)}</div></figure>')
    if q.get("board_card"):
        out.append(f'<p class="hint">Wire and upload the board first: <a href="{q["board_card"]}.html">open its circuit card</a>.</p>')
    if q.get("led_pin"):
        out.append('<p class="hint">Board side: an LED on <span class="pin">~11</span> through a 220Ω resistor, short leg to <span class="pin">GND</span>.</p>')
    out.append("</section>")
    run_dir = q.get("run_in", "python")
    fname = q["file"]
    if q.get("lessons"):
        cmd = "python 01_Python_Basics\\01_hello_print.py"
    elif q.get("run_in"):
        cmd = "python " + fname.split("/")[-1]
    else:
        cmd = "python " + fname[len("python/"):].replace("/", "\\")
    run_win = run_dir.replace("/", "\\")
    usb_li = "<li><b>Close the Arduino Serial Monitor first</b>: only one program can use the USB port.</li>" if q["kind"] == "usb" else ""
    key_li = ("<li>For AI answers: copy <code>04_ChirpQuest\\.env.example</code> to <code>.env</code> and paste the Gemini key.</li>"
              if "ChirpQuest" in fname else "")
    out.append('<section><div class="step-title"><span class="step-num">2</span><h2>Run the program</h2></div><div class="program">'
               f'<div class="file"><span>Type in a terminal:</span><code class="path">cd HanaProjects\\{E(run_win)} &amp;&amp; {E(cmd)}</code><button class="copy" type="button">Copy</button></div>'
               '<ol class="do"><li>First time only: <code>cd HanaProjects\\python</code>, then <code>python -m venv venv</code> and <code>venv\\Scripts\\activate</code> and <code>pip install -r requirements.txt</code>.</li>'
               '<li>Every time: <code>venv\\Scripts\\activate</code> (you\'ll see <code>(venv)</code> at the start of the line).</li>'
               f'<li>Run the command above.</li>{usb_li}{key_li}'
               '<li>Stop it with <kbd>Ctrl</kbd> + <kbd>C</kbd>.</li></ol></div></section>')
    if q.get("lessons"):
        lessons = ["01_hello_print", "02_variables", "03_input_greeting", "04_if_elif_else", "05_calculator", "06_string_indexing", "07_friendly_chat",
                   "08_compare_numbers", "09_string_slicing", "10_loops", "11_functions_pet_agents", "12_data_types", "13_try_except"]
        out.append('<section><div class="step-title"><span class="step-num">3</span><h2>The 13 lessons</h2></div><div class="lessons">'
                   + "".join(f'<code>{l}.py</code>' for l in lessons) + '</div></section>')
    tries = "".join(f"<li>{t}</li>" for t in q.get("try_", []))
    out.append(f'<section><div class="step-title"><span class="step-num">{4 if q.get("lessons") else 3}</span><h2>Try it!</h2></div><ol class="do">{tries}</ol></section>')
    tips = q.get("tips", [])
    if tips:
        out.append('<section><div class="step-title"><span class="step-num">!</span><h2>If it doesn\'t work</h2></div><div class="tips">'
                   + "".join(f'<div class="tip{" warn" if w else ""}"><h3>{t}</h3><p>{d}</p></div>' for t, d, w in tips) + "</div></section>")
    out.append(f'<footer><span><b>Program:</b> <a href="{REPO}/tree/main/{q["file"]}"><code>{E(q["file"])}</code></a> (old name <code>{E(q["old"])}</code>)</span></footer></main>')
    return "".join(out)


SHOWCASE_BANNER = ('<div class="feature-row"><a class="feature" href="../led-from-anywhere.html"><span class="feature-kicker">★ Featured project</span>'
                   '<b>Control this LED from anywhere in the world</b><span>The full step-by-step mission with ngrok, a QR code for your class, and a 5-minute school demo script →</span></a>'
                   '<a class="feature alt" href="../share-with-ngrok.html"><span class="feature-kicker">ngrok guide</span><b>Share any project with a link</b>'
                   '<span>How to install ngrok, connect it, and open a tunnel, explained for kids →</span></a></div>')


def index_page():
    groups = {}
    for p in PROJECTS + LEARNING:
        groups.setdefault(p["group"], []).append(p)
    order = ["Basics & LEDs", "Music & Sound", "Sensors & Security", "Doors", "IR Remote & Displays", "Games", "Smart House", "ESP32 & Tools", "Learning Steps"]
    out = ['<main class="page">']
    out.append('<header class="hero"><div class="eyebrow">Hana\'s Circuit Cards</div><h1>Build it, wire it, run it</h1>'
               '<p class="lead">One card for every project: which parts you need, which pin each wire goes to, which program to upload, and how to test it.</p>'
               f'<div class="chips"><span class="chip">{len(PROJECTS)} Arduino &amp; ESP32 projects</span><span class="chip">{len(LEARNING)} learning steps</span><span class="chip">{len(PYTHON)} Python programs</span></div></header>')
    out.append('<a class="hero-feature" href="led-from-anywhere.html">'
               '<svg viewBox="0 0 520 120" role="img" aria-label="A phone taps ON, the signal crosses the world, and an LED lights up">'
               '<rect x="10" y="22" width="44" height="76" rx="8" fill="#1d3552" stroke="#43d3ff" stroke-width="3"/><rect x="18" y="46" width="28" height="16" rx="4" fill="#39d98a"/>'
               '<text x="32" y="58" text-anchor="middle" font-family="Baloo 2, sans-serif" font-weight="800" font-size="10" fill="#0b1626">ON</text>'
               '<path d="M66 60 H 440" stroke="#ffd23f" stroke-width="4" stroke-dasharray="3 10" stroke-linecap="round"/>'
               '<circle cx="250" cy="60" r="30" fill="#123a5c" stroke="#43d3ff" stroke-width="3"/><ellipse cx="250" cy="60" rx="12" ry="30" fill="none" stroke="#43d3ff" stroke-width="2"/><line x1="220" y1="60" x2="280" y2="60" stroke="#43d3ff" stroke-width="2"/>'
               '<circle cx="480" cy="56" r="34" fill="#ffd23f" opacity=".25"/><path d="M466 80 V52 a14 14 0 0 1 28 0 V80 Z" fill="#ffd23f"/><rect x="470" y="80" width="4" height="18" fill="#b0bec5"/><rect x="486" y="80" width="4" height="24" fill="#b0bec5"/>'
               '</svg><span class="hf-text"><span class="feature-kicker">★ Featured project · school demo</span><b>Turn on an LED from anywhere in the world</b>'
               '<span>Friends tap ON from their phones, and a light switches on at home. ESP32 + Python + ngrok, step by step.</span>'
               '<span class="hf-links"><span class="hf-btn">Start the mission →</span></span></span></a>')
    out.append('<a class="feature alt wide" href="share-with-ngrok.html"><span class="feature-kicker">ngrok guide</span><b>Share any of Hana\'s web projects with a link</b>'
               '<span>ESP32 LED remote, LED slider, ChirpQuest, TFT noticeboard: install ngrok, connect it, and open a tunnel in 7 kid-sized steps →</span></a>')
    out.append('<section><h2>The rules on every card</h2><div class="rules">'
               f'<div class="rule"><span class="swatch" style="background:{RED}"></span><div><b>Red wire = power</b><p>5V on an Uno, 3.3V on an ESP32.</p></div></div>'
               f'<div class="rule"><span class="swatch" style="background:{BLACK}"></span><div><b>Black wire = ground (GND)</b><p>Every part needs a ground wire back to the board.</p></div></div>'
               '<div class="rule"><span class="swatch" style="background:linear-gradient(90deg,#f9a825,#2e9e4f,#1e88e5)"></span><div><b>Other colours = signals</b><p>Each has a number that matches the checklist.</p></div></div>'
               '<div class="rule"><span class="swatch" style="background:linear-gradient(180deg,#e53935 0 45%,#fff 45% 55%,#1e63c6 55%)"></span><div><b>Breadboard strips</b><p>When many parts need power, they share the + and − strips.</p></div></div>'
               '<div class="rule"><span class="big">🔌</span><div><b>Unplug first</b><p>Always unplug the USB cable before moving wires.</p></div></div>'
               '<div class="rule"><span class="big">⚡</span><div><b>ESP32 = 3.3V only</b><p>5V can damage an ESP32, an RFID reader or a colour screen.</p></div></div>'
               '</div></section>')
    for g in order:
        items = groups.get(g, [])
        if not items:
            continue
        cards = []
        for p in items:
            lv, _ = level(len(p["parts"]))
            star = '<span class="star">★ Favourite</span>' if p.get("star") else ""
            cards.append(f'<a class="tile" href="cards/{p["slug"]}.html"><span class="tile-top"><span class="chip board-{p["board"]}">{"Uno" if p["board"] == "uno" else "ESP32"}</span>{star}</span>'
                         f'<b>{E(p["title"])}</b><span class="tile-sub">{"Not started" if p.get("wip") else lv + " · " + str(len(p["parts"])) + " parts"}</span></a>')
        out.append(f'<section><h2>{E(g)}</h2><div class="tiles">{"".join(cards)}</div></section>')
    pc = []
    for q in PYTHON:
        k = {"usb": "USB to Arduino", "wifi": "Wi-Fi to ESP32", "none": "No wires"}[q["kind"]]
        star = '<span class="star">★ Favourite</span>' if q.get("star") else ""
        pc.append(f'<a class="tile" href="cards/{q["slug"]}.html"><span class="tile-top"><span class="chip">Python</span>{star}</span><b>{E(q["title"])}</b><span class="tile-sub">{k}</span></a>')
    out.append(f'<section><h2>Python programs</h2><div class="tiles">{"".join(pc)}</div></section>')
    gl = "".join(f'<div class="part"><svg viewBox="0 0 150 84" role="img" aria-label="{E(n)}">{icon(t, 75, 42, {"n": 3})}</svg><b>{E(n)}</b><span>{E(d)}</span></div>'
                 for t, (n, d) in PART_INFO.items())
    out.append(f'<section><h2>Parts guide</h2><div class="parts">{gl}</div></section>')
    out.append(f'<footer><span>Source: <a href="{REPO}">{REPO}</a>. Cards are built from <code>tools/circuit_cards/data.py</code>.</span></footer></main>')
    return "".join(out)


CSS = r""":root{--bg:#eef3f4;--surface:#fff;--ink:#16242c;--ink-soft:#4a5d68;--line:#d3dee2;--accent:#00838c;--accent-soft:#d7eff0;--sun:#ffc93c;--sun-ink:#5a4300;--warn:#c2410c;--warn-soft:#fff1e6;
--display:"Baloo 2","Trebuchet MS",system-ui,sans-serif;--body:"Atkinson Hyperlegible","Segoe UI",system-ui,sans-serif;--mono:"JetBrains Mono",Consolas,"Courier New",monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#0f171b;--surface:#17232a;--ink:#e7eef1;--ink-soft:#9fb2bb;--line:#2a3a43;--accent:#3fc3cb;--accent-soft:#123338;--sun:#ffd35c;--sun-ink:#2b2100;--warn:#ff9a5c;--warn-soft:#2d1b10}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#0f171b;--surface:#17232a;--ink:#e7eef1;--ink-soft:#9fb2bb;--line:#2a3a43;--accent:#3fc3cb;--accent-soft:#123338;--sun:#ffd35c;--sun-ink:#2b2100;--warn:#ff9a5c;--warn-soft:#2d1b10}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.55;padding-inline:16px;padding-block:24px 48px}
a{color:var(--accent)}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid var(--sun);outline-offset:2px}
.page{max-width:1000px;margin:0 auto;display:grid;gap:28px}
h1,h2,h3{font-family:var(--display);line-height:1.1;text-wrap:balance;margin:0}h1{font-size:clamp(2.1rem,6vw,3.3rem);font-weight:800}h2{font-size:1.65rem;font-weight:700}h3{font-size:1.15rem;font-weight:700}
p{margin:0}code,.pin{font-family:var(--mono)}code{font-size:.92em}
.crumbs a{font-weight:700;text-decoration:none}
.hero{display:grid;gap:12px}.eyebrow{font-family:var(--mono);font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);font-weight:700}
.lead{font-size:1.18rem;max-width:62ch}
.chips{display:flex;flex-wrap:wrap;gap:8px}.chip{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:999px;background:var(--accent-soft);color:var(--ink);font-size:.88rem;font-weight:700}
.chip.level{background:var(--sun);color:var(--sun-ink)}.chip.board-esp32{background:#263238;color:#e0e6ea}.chip.board-uno{background:#0e7c86;color:#fff}
.banner{border-radius:14px;padding:12px 16px;font-size:1.02rem}.banner.esp{background:var(--warn-soft);border:2px solid var(--warn)}
section{display:grid;gap:14px}.step-title{display:flex;align-items:center;gap:12px}
.step-num{flex:none;width:40px;height:40px;border-radius:50%;display:grid;place-items:center;background:var(--accent);color:var(--surface);font-family:var(--display);font-weight:800;font-size:1.3rem}
.hint{color:var(--ink-soft)}
.parts{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:12px}
.part{background:var(--surface);border:2px solid var(--line);border-radius:16px;padding:12px;display:grid;gap:6px;justify-items:center;text-align:center;align-content:start}
.part svg{width:100%;max-width:150px;height:84px}.part b{font-size:1rem}.part span{font-size:.84rem;color:var(--ink-soft)}
figure{margin:0;display:grid;gap:10px}.mat{background:#f4f7f1;border-radius:20px;border:3px solid #cfd9cf;padding:8px;overflow-x:auto}
.mat svg{display:block;width:100%;min-width:760px;height:auto}figcaption{color:var(--ink-soft);font-size:.95rem}
.wires{display:grid;gap:10px}
.wire{display:grid;grid-template-columns:auto auto 1fr;align-items:center;gap:14px;background:var(--surface);border:2px solid var(--line);border-radius:14px;padding:12px 14px;cursor:pointer}
.wire:has(input:checked){border-color:var(--accent);background:var(--accent-soft)}.wire input{width:26px;height:26px;accent-color:var(--accent);cursor:pointer}
.swatch{display:inline-block;width:46px;height:14px;border-radius:7px;border:2px solid rgba(0,0,0,.25)}
.tag{display:inline-grid;place-items:center;width:26px;height:26px;border-radius:50%;font-family:var(--display);font-weight:800;font-size:.95rem;border:2px solid #fff;box-shadow:0 0 0 1px rgba(0,0,0,.25)}
.route{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px}.arrow{color:var(--ink-soft);font-weight:700}
.pin{display:inline-block;padding:1px 8px;border-radius:6px;background:#0e6f78;color:#fff;font-size:.9rem;font-weight:700}.pin.part-pin{background:#1f5fae}
.pin.rail.plus{background:#e53935}.pin.rail.minus{background:#1e63c6}
.why{font-size:.85rem;color:var(--ink-soft);flex-basis:100%}.progress{font-weight:700;color:var(--accent)}
.program{background:var(--surface);border:2px solid var(--line);border-radius:18px;padding:18px;display:grid;gap:14px}
.file{display:flex;flex-wrap:wrap;align-items:center;gap:10px;background:var(--bg);border-radius:12px;padding:10px 12px}.file code{word-break:break-all}
.copy{font:inherit;font-size:.85rem;font-weight:700;border:2px solid var(--accent);color:var(--accent);background:transparent;border-radius:10px;padding:4px 12px;cursor:pointer}
ol.do{margin:0;padding-left:1.4em;display:grid;gap:8px}ol.do li::marker{font-family:var(--display);font-weight:800;color:var(--accent)}
.libs ul{margin:6px 0 0;padding-left:1.2em}
kbd{font-family:var(--mono);font-size:.85em;background:var(--bg);border:1px solid var(--line);border-bottom-width:3px;border-radius:6px;padding:0 6px}
.tips{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.tip{background:var(--surface);border:2px solid var(--line);border-radius:14px;padding:14px;display:grid;gap:6px;align-content:start}.tip.warn{background:var(--warn-soft);border-color:var(--warn)}.tip.warn h3{color:var(--warn)}
.rules{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.rule{display:flex;gap:12px;align-items:flex-start;background:var(--surface);border:2px solid var(--line);border-radius:14px;padding:14px}.rule p{color:var(--ink-soft);font-size:.92rem}
.rule .swatch{flex:none;margin-top:6px}.rule .big{font-size:1.6rem;line-height:1;flex:none;width:46px;text-align:center}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px}
.tile{display:grid;gap:6px;align-content:start;background:var(--surface);border:2px solid var(--line);border-radius:16px;padding:14px;text-decoration:none;color:var(--ink)}
.tile:hover{border-color:var(--accent)}.tile b{font-family:var(--display);font-size:1.15rem;line-height:1.15}.tile-sub{color:var(--ink-soft);font-size:.88rem}
.tile-top{display:flex;justify-content:space-between;align-items:center;gap:6px}.star{font-size:.8rem;font-weight:700;color:var(--sun-ink);background:var(--sun);border-radius:999px;padding:2px 8px}
.lessons{display:flex;flex-wrap:wrap;gap:8px}.lessons code{background:var(--surface);border:2px solid var(--line);border-radius:10px;padding:4px 10px}
footer{color:var(--ink-soft);font-size:.85rem;border-top:2px solid var(--line);padding-top:14px;display:grid;gap:4px}
.feature-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}
.feature{display:grid;gap:6px;text-decoration:none;color:#eef5fb;background:linear-gradient(135deg,#0b1626 0%,#15293f 60%,#3a1d34 100%);border:3px solid #ffd23f;border-radius:20px;padding:18px 20px;box-shadow:0 8px 24px rgba(11,22,38,.25)}
.feature:hover{transform:translateY(-2px)}.feature b{font-family:var(--display);font-size:1.35rem;line-height:1.15;color:#ffd23f}.feature span{color:#c9d8e6}
.feature code{background:#050b12;color:#ffd23f;border-radius:6px;padding:0 5px}
.feature.alt{border-color:#43d3ff}.feature.alt b{color:#43d3ff}
.feature-kicker{font-family:var(--mono);font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;font-weight:700;color:#ff9fb7!important}
.hero-feature{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:18px;align-items:center;text-decoration:none;color:#eef5fb;background:radial-gradient(circle at 85% 30%,rgba(255,210,63,.25),transparent 45%),linear-gradient(135deg,#0b1626,#15293f);border:3px solid #ffd23f;border-radius:24px;padding:22px}
.hero-feature svg{width:100%;height:auto}.hf-text{display:grid;gap:8px}.hf-text b{font-family:var(--display);font-size:clamp(1.5rem,4vw,2.1rem);line-height:1.1;color:#ffd23f}.hf-text span{color:#c9d8e6}
.hf-btn{display:inline-block;background:#ffd23f;color:#2b2100!important;font-weight:800;font-family:var(--display);border-radius:999px;padding:6px 18px;font-size:1.05rem}
@media (max-width:700px){.hero-feature{grid-template-columns:1fr}}
@media (prefers-reduced-motion:no-preference){.feature,.hero-feature{transition:transform .15s}.hero-feature:hover{transform:translateY(-2px)}}
@media (max-width:520px){.wire{grid-template-columns:auto 1fr}.wire .swatch{display:none}}
"""

JS = r"""(function(){
var box=document.querySelector('.wires');
if(box){var key=box.getAttribute('data-key');var cbs=[].slice.call(box.querySelectorAll('input[type=checkbox]'));var pr=document.querySelector('.progress');
function load(){try{return JSON.parse(localStorage.getItem(key)||'[]')}catch(e){return[]}}
function save(){try{localStorage.setItem(key,JSON.stringify(cbs.filter(function(b){return b.checked}).map(function(b){return b.id})))}catch(e){}}
function upd(){var n=cbs.filter(function(b){return b.checked}).length;if(pr)pr.textContent=n===cbs.length?('All '+n+' done! Now upload the program.'):(n+' of '+cbs.length+' done')}
var s=load();cbs.forEach(function(b){b.checked=s.indexOf(b.id)!==-1;b.addEventListener('change',function(){save();upd()})});upd();}
[].slice.call(document.querySelectorAll('.copy')).forEach(function(btn){btn.addEventListener('click',function(){var el=btn.parentNode.querySelector('.path');var t=el.textContent;
function sel(){var r=document.createRange();r.selectNodeContents(el);var s=window.getSelection();s.removeAllRanges();s.addRange(r);btn.textContent='Selected: press Ctrl+C'}
if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(function(){btn.textContent='Copied!'},sel)}else{sel()}
setTimeout(function(){btn.textContent='Copy'},2500)})});
})();
"""


def build(out_dir, standalone=True):
    files = {}
    by_slug = {p["slug"]: p for p in PROJECTS + LEARNING}
    for p in PROJECTS + LEARNING:
        files[f"cards/{p['slug']}.html"] = page(f"{p['title']} Circuit Card", arduino_card(p, by_slug), "../cards.css", "../cards.js")
    for q in PYTHON:
        files[f"cards/{q['slug']}.html"] = page(f"{q['title']} Card", python_card(q), "../cards.css", "../cards.js")
    files["index.html"] = page("Hana's Circuit Cards", index_page(), "cards.css", "cards.js", standalone)
    files["cards.css"] = CSS
    files["cards.js"] = JS
    files[".nojekyll"] = ""
    show = os.path.join(HERE, "showcase")          # hand-written showcase pages, copied as-is
    for name in sorted(os.listdir(show)):
        with open(os.path.join(show, name), encoding="utf-8") as f:
            files[name] = f.read()
    return files


def main():
    check = "--check" in sys.argv
    out = os.path.join(ROOT, "docs")
    files = build(out)
    stale = []
    for rel, content in files.items():
        path = os.path.join(out, rel.replace("/", os.sep))
        old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if old != content:
            stale.append(rel)
            if not check:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(content)
    if "--artifact" in sys.argv:          # index variant without <html>/<head> for the Claude artifact viewer
        a = os.path.join(sys.argv[sys.argv.index("--artifact") + 1])
        with open(a, "w", encoding="utf-8", newline="\n") as f:
            f.write(page("Hana's Circuit Cards", index_page(), "cards.css", "cards.js", standalone=False))
    if check:
        if stale:
            print("docs/ is out of date. Run: python tools/circuit_cards/build.py\n  " + "\n  ".join(stale))
            sys.exit(1)
        print(f"docs/ is up to date ({len(files)} files).")
    else:
        print(f"wrote {len(stale)} changed file(s); {len(files)} files total in docs/")


if __name__ == "__main__":
    main()
