# birds.py - ChirpQuest (Realistic photos via iNaturalist + 3D SVG + debug logging)

import os
import random
import re
import time
import logging
import requests
from flask import Flask, jsonify, render_template_string, request

# Load GEMINI_API_KEY from the .env file next to this script (never uploaded).
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass  # pip install python-dotenv, or set GEMINI_API_KEY in the terminal

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("chirpquest")

app = Flask(__name__)

# ==========================================
# 0. GEMINI CONFIG (rotate keys/models here)
# ==========================================
# Put your REAL key in the .env file as GEMINI_API_KEY=... (see .env.example).
GEMINI_API_KEYS = [
    os.environ.get("GEMINI_API_KEY", ""),  # real key lives in .env
    # "SECOND_KEY_HERE",  # optional backup for rotation
]
GEMINI_MODEL = "gemini-flash-latest"
GEMINI_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

_key_index = 0
def get_current_gemini_key():
    return GEMINI_API_KEYS[_key_index % len(GEMINI_API_KEYS)]
def rotate_gemini_key():
    global _key_index
    _key_index = (_key_index + 1) % len(GEMINI_API_KEYS)
    return get_current_gemini_key()

PIP_SYSTEM_PROMPT = (
    "You are Pip, a friendly cockatiel mascot for the ChirpQuest birding app. "
    "Answer questions about North Texas birds (and birds in general) like a warm, patient expert talking to a curious kid under 10. "
    "Always give a complete, natural 2-4 sentence answer — never trail off or stop mid-thought. "
    "If you don't know something, say you're still learning instead of guessing. "
    "Add one or two bird emojis naturally, not on every sentence."
)

def call_gemini(user_message, retries=None, transient_retries=2):
    if retries is None:
        retries = len(GEMINI_API_KEYS)
    key = get_current_gemini_key()
    if key in ("DUMMY_TEST_KEY_REPLACE_ME", "PUT_YOUR_KEY_HERE", ""):
        log.warning("Gemini key is a placeholder — set GEMINI_API_KEY env var. Using fallback reply.")
        return generate_bot_reply_fallback(user_message)

    url = GEMINI_URL_TEMPLATE.format(model=GEMINI_MODEL)
    payload = {
        "contents": [{"parts": [{"text": user_message}]}],
        "systemInstruction": {"parts": [{"text": PIP_SYSTEM_PROMPT}]},
        "generationConfig": {
            "maxOutputTokens": 2048,
            "temperature": 0.8,
        },
    }
    headers = {"Content-Type": "application/json", "X-goog-api-key": key}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        log.info("Gemini HTTP %s", resp.status_code)
        # ---- DEBUG: print the raw response so you can see exactly what's wrong ----
        try:
            log.info("Gemini raw response: %s", resp.text[:1500])
        except Exception:
            pass

        if resp.status_code in (400, 401, 403, 429) and retries > 0:
            log.warning("Gemini error %s — rotating key and retrying.", resp.status_code)
            rotate_gemini_key()
            return call_gemini(user_message, retries=retries - 1, transient_retries=transient_retries)

        if resp.status_code in (500, 502, 503, 504) and transient_retries > 0:
            log.warning(
                "Gemini transient error %s — retrying (%d attempt(s) left).",
                resp.status_code, transient_retries,
            )
            time.sleep(1.5)
            return call_gemini(user_message, retries=retries, transient_retries=transient_retries - 1)

        resp.raise_for_status()
        data = resp.json()

        # Handle safety blocks / empty candidates explicitly
        if not data.get("candidates"):
            reason = data.get("promptFeedback", {}).get("blockReason")
            log.warning("No candidates returned. blockReason=%s", reason)
            return "Chirp! I couldn't chirp that one out. Try asking me another bird question!"

        candidate = data["candidates"][0]
        finish_reason = candidate.get("finishReason")
        parts = candidate.get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts).strip()

        if finish_reason == "MAX_TOKENS":
            log.warning(
                "Gemini hit MAX_TOKENS — reply was cut off. Consider raising maxOutputTokens further. Partial text: %r",
                text,
            )
            if not text:
                return "Chirp! I had a lot to say and lost my train of thought — ask me again?"

        if text:
            return text
        log.warning("Candidate had no text. Full candidate: %s", candidate)
        return "Chirp! My brain got a little ruffled there — ask me again?"

    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        if transient_retries > 0:
            log.warning("Gemini network error (%s) — retrying (%d attempt(s) left).", e, transient_retries)
            return call_gemini(user_message, retries=retries, transient_retries=transient_retries - 1)
        log.error("Gemini request failed after retries: %s", e)
        return generate_bot_reply_fallback(user_message)
    except requests.exceptions.RequestException as e:
        log.error("Gemini request failed: %s", e)
        return generate_bot_reply_fallback(user_message)
    except Exception as e:
        log.error("Unexpected Gemini error: %s", e)
        return generate_bot_reply_fallback(user_message)

def _has_word(msg, *words):
    return any(re.search(r"\b" + re.escape(w) + r"\b", msg) for w in words)

def generate_bot_reply_fallback(user_msg):
    msg = user_msg.lower().strip()
    if _has_word(msg, "hi", "hello", "hey"):
        return "Chirp chirp! I'm Pip! What bird questions do you have today?"
    elif _has_word(msg, "cardinal"):
        return "Northern Cardinals are famous for their vivid red crests and black masks around their beaks!"
    elif _has_word(msg, "owl"):
        return "Barred Owls live in Texas woodlands and have big, beautiful dark brown eyes."
    elif _has_word(msg, "bluejay") or "blue jay" in msg:
        return "Blue Jays are bright blue with a crest, and they can even mimic hawk calls!"
    elif _has_word(msg, "hummingbird"):
        return "Ruby-throated Hummingbirds flap their wings up to 80 times a second!"
    return "That's awesome! Check the Bird Book tab to see all our North Texas species!"

# ==========================================
# 1. MASCOT (Pip) — shaded 3D-style cockatiel
# ==========================================
COCKATIEL_MASCOT = {
    "name": "Pip the Cockatiel",
    "role": "ChirpQuest Guide",
    "svg": """<svg viewBox="0 0 120 140" class="mascot-svg">
        <defs>
            <radialGradient id="pipBody" cx="40%" cy="35%" r="75%">
                <stop offset="0%" stop-color="#e2e8f0"/><stop offset="70%" stop-color="#94a3b8"/><stop offset="100%" stop-color="#64748b"/>
            </radialGradient>
            <radialGradient id="pipCheek" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#fb923c"/><stop offset="100%" stop-color="#ea580c"/>
            </radialGradient>
            <linearGradient id="pipCrest" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#fde047"/><stop offset="100%" stop-color="#f59e0b"/>
            </linearGradient>
        </defs>
        <ellipse cx="52" cy="126" rx="26" ry="5" fill="#0f172a" opacity="0.12"/>
        <path d="M 25,115 L 45,90 L 20,130 Z" fill="#64748b"/>
        <path d="M 45,90 Q 30,65 50,40 Q 68,20 82,30 Q 95,50 82,75 Q 68,100 45,90 Z" fill="url(#pipBody)"/>
        <path class="mascot-wing" d="M 52,65 Q 66,80 74,64 Q 60,72 52,65 Z" fill="#cbd5e1"/>
        <path d="M 58,26 Q 50,4 38,2 Q 52,14 62,20 Z" fill="url(#pipCrest)"/>
        <path d="M 64,24 Q 58,6 48,4 Q 58,16 68,22 Z" fill="#fde047"/>
        <path d="M 58,22 Q 80,18 88,36 Q 85,55 65,52 Z" fill="#fef08a"/>
        <circle cx="75" cy="43" r="8" fill="url(#pipCheek)"/>
        <path d="M 84,34 L 96,39 L 83,44 Z" fill="#475569"/>
        <g class="mascot-eye">
            <circle cx="72" cy="32" r="4.2" fill="#0f172a"/>
            <circle cx="73.6" cy="30.4" r="1.6" fill="#ffffff"/>
        </g>
    </svg>"""
}

# ==========================================
# 2. TEXAS BIRDS — 3D-shaded SVGs + iNaturalist photo lookup name
# ==========================================
# "inat" = the search term used to pull a REAL Creative-Commons photo at runtime.
TEXAS_BIRDS = [
    {"id": "cardinal", "name": "Northern Cardinal", "emoji": "🐦", "inat": "Cardinalis cardinalis",
     "marks": ["Vivid red body & tall crest", "Distinct black mask around orange beak"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <radialGradient id="g_card" cx="38%" cy="30%" r="80%"><stop offset="0%" stop-color="#f87171"/><stop offset="65%" stop-color="#ef4444"/><stop offset="100%" stop-color="#b91c1c"/></radialGradient></defs>
        <ellipse cx="52" cy="92" rx="24" ry="4" fill="#0f172a" opacity="0.12"/>
        <path class="wing-flap" d="M 35,75 Q 20,55 40,35 Q 60,15 75,30 Q 90,50 75,70 Q 55,90 35,75 Z" fill="url(#g_card)"/>
        <path d="M 55,18 L 72,2 L 68,28 Z" fill="#dc2626"/>
        <path d="M 40,58 Q 55,66 68,58" stroke="#b91c1c" stroke-width="2" fill="none" opacity="0.5"/>
        <path d="M 70,35 L 88,40 L 72,50 Z" fill="#f97316"/>
        <path d="M 62,30 Q 75,32 72,46 Q 60,50 58,38 Z" fill="#1e293b"/>
        <g class="bird-blink"><circle cx="65" cy="34" r="3.6" fill="#fff"/><circle cx="65" cy="34" r="1.6" fill="#0f172a"/><circle cx="63.8" cy="32.8" r="0.9" fill="#fff"/></g></svg>"""},
    {"id": "bluejay", "name": "Blue Jay", "emoji": "🐦", "inat": "Cyanocitta cristata",
     "marks": ["Bright blue crest & back", "Black necklace pattern & white chest"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <radialGradient id="g_jay" cx="38%" cy="30%" r="80%"><stop offset="0%" stop-color="#60a5fa"/><stop offset="65%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#1d4ed8"/></radialGradient></defs>
        <ellipse cx="52" cy="92" rx="24" ry="4" fill="#0f172a" opacity="0.12"/>
        <path class="wing-flap" d="M 35,75 Q 20,55 40,35 Q 60,15 75,30 Q 90,50 75,70 Q 55,90 35,75 Z" fill="url(#g_jay)"/>
        <path d="M 38,55 Q 55,75 72,55 Q 55,88 38,55 Z" fill="#f8fafc"/>
        <path d="M 55,18 L 74,4 L 66,28 Z" fill="#2563eb"/>
        <path d="M 70,35 L 88,40 L 72,50 Z" fill="#1e293b"/>
        <path d="M 58,42 Q 68,55 72,40" stroke="#1e293b" stroke-width="3.5" fill="none"/>
        <g class="bird-blink"><circle cx="65" cy="34" r="3.6" fill="#fff"/><circle cx="65" cy="34" r="1.6" fill="#0f172a"/><circle cx="63.8" cy="32.8" r="0.9" fill="#fff"/></g></svg>"""},
    {"id": "mockingbird", "name": "Northern Mockingbird", "emoji": "🐦", "inat": "Mimus polyglottos",
     "marks": ["Texas State Bird", "Sleek gray coat with white wing bars"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <radialGradient id="g_mock" cx="38%" cy="30%" r="80%"><stop offset="0%" stop-color="#cbd5e1"/><stop offset="70%" stop-color="#94a3b8"/><stop offset="100%" stop-color="#64748b"/></radialGradient></defs>
        <ellipse cx="52" cy="92" rx="24" ry="4" fill="#0f172a" opacity="0.12"/>
        <path class="wing-flap" d="M 35,75 Q 20,55 40,35 Q 60,15 75,30 Q 90,50 75,70 Q 55,90 35,75 Z" fill="url(#g_mock)"/>
        <path d="M 38,55 Q 55,75 72,55 Q 55,88 38,55 Z" fill="#f1f5f9"/>
        <path d="M 70,35 L 88,40 L 72,48 Z" fill="#475569"/>
        <g class="bird-blink"><circle cx="65" cy="34" r="3.6" fill="#fff"/><circle cx="65" cy="34" r="1.6" fill="#0f172a"/></g></svg>"""},
    {"id": "flycatcher", "name": "Scissor-tailed Flycatcher", "emoji": "🐦", "inat": "Tyrannus forficatus",
     "marks": ["Long scissor-like tail feathers", "Delicate salmon-pink sides"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <radialGradient id="g_fly" cx="38%" cy="30%" r="80%"><stop offset="0%" stop-color="#e2e8f0"/><stop offset="70%" stop-color="#cbd5e1"/><stop offset="100%" stop-color="#94a3b8"/></radialGradient></defs>
        <ellipse cx="52" cy="94" rx="24" ry="4" fill="#0f172a" opacity="0.1"/>
        <path d="M 8,92 L 32,62 L 4,98 Z" fill="#64748b"/>
        <path class="wing-flap" d="M 35,75 Q 20,55 40,35 Q 60,15 75,30 Q 90,50 75,70 Q 55,90 35,75 Z" fill="url(#g_fly)"/>
        <path d="M 40,55 Q 52,68 62,55" fill="#fda4af"/>
        <path d="M 70,35 L 88,40 L 72,48 Z" fill="#334155"/>
        <g class="bird-blink"><circle cx="65" cy="34" r="3.6" fill="#fff"/><circle cx="65" cy="34" r="1.6" fill="#0f172a"/></g></svg>"""},
    {"id": "dove", "name": "Mourning Dove", "emoji": "🕊️", "inat": "Zenaida macroura",
     "marks": ["Soft tan-gray teardrop body", "Tiny black spots on wings"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <radialGradient id="g_dove" cx="38%" cy="30%" r="80%"><stop offset="0%" stop-color="#e2e8f0"/><stop offset="70%" stop-color="#cbd5e1"/><stop offset="100%" stop-color="#94a3b8"/></radialGradient></defs>
        <ellipse cx="52" cy="92" rx="24" ry="4" fill="#0f172a" opacity="0.1"/>
        <path class="wing-flap" d="M 35,75 Q 20,55 40,35 Q 60,15 75,30 Q 90,50 75,70 Q 55,90 35,75 Z" fill="url(#g_dove)"/>
        <path d="M 70,35 L 86,40 L 72,48 Z" fill="#64748b"/>
        <circle cx="48" cy="52" r="2" fill="#334155"/><circle cx="55" cy="58" r="2" fill="#334155"/>
        <g class="bird-blink"><circle cx="65" cy="34" r="3.6" fill="#fff"/><circle cx="65" cy="34" r="1.6" fill="#0f172a"/></g></svg>"""},
    {"id": "chickadee", "name": "Carolina Chickadee", "emoji": "🐦", "inat": "Poecile carolinensis",
     "marks": ["Distinct black cap and bib", "Bright white cheek patches"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <radialGradient id="g_chick" cx="38%" cy="30%" r="80%"><stop offset="0%" stop-color="#cbd5e1"/><stop offset="70%" stop-color="#94a3b8"/><stop offset="100%" stop-color="#64748b"/></radialGradient></defs>
        <ellipse cx="52" cy="92" rx="24" ry="4" fill="#0f172a" opacity="0.12"/>
        <path class="wing-flap" d="M 35,75 Q 20,55 40,35 Q 60,15 75,30 Q 90,50 75,70 Q 55,90 35,75 Z" fill="url(#g_chick)"/>
        <path d="M 45,20 Q 65,10 75,30 Q 62,38 52,32 Z" fill="#0f172a"/>
        <path d="M 52,34 Q 68,34 60,52 Z" fill="#fff"/>
        <path d="M 58,46 Q 72,46 66,58 Z" fill="#0f172a"/>
        <path d="M 70,33 L 86,37 L 72,42 Z" fill="#0f172a"/>
        <g class="bird-blink"><circle cx="65" cy="30" r="3.6" fill="#fff"/><circle cx="65" cy="30" r="1.6" fill="#0f172a"/></g></svg>"""},
    {"id": "bluebird", "name": "Eastern Bluebird", "emoji": "🐦", "inat": "Sialia sialis",
     "marks": ["Vibrant royal blue back", "Warm rusty-red chest"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <radialGradient id="g_blue" cx="38%" cy="30%" r="80%"><stop offset="0%" stop-color="#3b82f6"/><stop offset="70%" stop-color="#2563eb"/><stop offset="100%" stop-color="#1e40af"/></radialGradient></defs>
        <ellipse cx="52" cy="92" rx="24" ry="4" fill="#0f172a" opacity="0.12"/>
        <path class="wing-flap" d="M 35,75 Q 20,55 40,35 Q 60,15 75,30 Q 90,50 75,70 Q 55,90 35,75 Z" fill="url(#g_blue)"/>
        <path d="M 45,45 Q 65,52 70,70 Q 55,85 40,70 Z" fill="#c2410c"/>
        <path d="M 70,35 L 88,40 L 72,46 Z" fill="#eab308"/>
        <g class="bird-blink"><circle cx="65" cy="34" r="3.6" fill="#fff"/><circle cx="65" cy="34" r="1.6" fill="#0f172a"/></g></svg>"""},
    {"id": "roadrunner", "name": "Greater Roadrunner", "emoji": "🐦", "inat": "Geococcyx californianus",
     "marks": ["Streaked brown plumage", "Long agile tail & swift stance"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <radialGradient id="g_road" cx="38%" cy="30%" r="80%"><stop offset="0%" stop-color="#f59e0b"/><stop offset="65%" stop-color="#d97706"/><stop offset="100%" stop-color="#92400e"/></radialGradient></defs>
        <ellipse cx="52" cy="90" rx="26" ry="4" fill="#0f172a" opacity="0.12"/>
        <path d="M 6,68 L 28,58 L 10,80 Z" fill="#78350f"/>
        <path class="wing-flap" d="M 28,62 Q 22,45 45,35 Q 68,20 82,32 Q 92,48 78,62 Q 58,82 28,62 Z" fill="url(#g_road)"/>
        <path d="M 62,25 L 78,12 L 72,32 Z" fill="#78350f"/>
        <path d="M 78,36 L 96,40 L 80,46 Z" fill="#eab308"/>
        <g class="bird-blink"><circle cx="70" cy="35" r="3.6" fill="#fff"/><circle cx="70" cy="35" r="1.6" fill="#0f172a"/></g></svg>"""},
    {"id": "hawk", "name": "Red-tailed Hawk", "emoji": "🦅", "inat": "Buteo jamaicensis",
     "marks": ["Broad powerful wings & sharp gaze", "Rich rust-orange tail"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <radialGradient id="g_hawk" cx="38%" cy="30%" r="80%"><stop offset="0%" stop-color="#b45309"/><stop offset="65%" stop-color="#92400e"/><stop offset="100%" stop-color="#78350f"/></radialGradient></defs>
        <ellipse cx="50" cy="90" rx="26" ry="4" fill="#0f172a" opacity="0.12"/>
        <path d="M 15,78 Q 10,60 28,55 Z" fill="#ea580c"/>
        <path class="wing-flap" d="M 28,68 Q 18,45 40,25 Q 62,10 78,22 Q 92,38 78,60 Q 58,85 28,68 Z" fill="url(#g_hawk)"/>
        <path d="M 38,48 Q 58,65 72,48 Q 58,80 38,48 Z" fill="#f8fafc"/>
        <path d="M 74,32 L 92,40 L 74,45 Z" fill="#eab308"/>
        <g class="bird-blink"><circle cx="65" cy="30" r="3.6" fill="#fff"/><circle cx="65" cy="30" r="1.6" fill="#0f172a"/></g></svg>"""},
    {"id": "woodpecker", "name": "Red-bellied Woodpecker", "emoji": "🐦", "inat": "Melanerpes carolinus",
     "marks": ["Bright red cap stripe", "Zebra-striped black & white back"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <radialGradient id="g_wood" cx="38%" cy="30%" r="80%"><stop offset="0%" stop-color="#f1f5f9"/><stop offset="70%" stop-color="#e2e8f0"/><stop offset="100%" stop-color="#cbd5e1"/></radialGradient></defs>
        <ellipse cx="52" cy="92" rx="24" ry="4" fill="#0f172a" opacity="0.1"/>
        <path class="wing-flap" d="M 35,75 Q 20,55 40,35 Q 60,15 75,30 Q 90,50 75,70 Q 55,90 35,75 Z" fill="url(#g_wood)"/>
        <path d="M 40,22 Q 62,8 72,20 Z" stroke="#ef4444" stroke-width="7" fill="none"/>
        <line x1="32" y1="46" x2="55" y2="46" stroke="#0f172a" stroke-width="3.5"/>
        <line x1="30" y1="55" x2="53" y2="55" stroke="#0f172a" stroke-width="3.5"/>
        <line x1="28" y1="64" x2="51" y2="64" stroke="#0f172a" stroke-width="3.5"/>
        <path d="M 72,32 L 94,36 L 74,42 Z" fill="#475569"/>
        <g class="bird-blink"><circle cx="65" cy="32" r="3.6" fill="#fff"/><circle cx="65" cy="32" r="1.6" fill="#0f172a"/></g></svg>"""},
    {"id": "heron", "name": "Great Blue Heron", "emoji": "🐦", "inat": "Ardea herodias",
     "marks": ["Tall blue-gray body & curved S-neck", "Long dagger-like yellow beak"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <linearGradient id="g_heron" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#64748b"/><stop offset="100%" stop-color="#334155"/></linearGradient></defs>
        <ellipse cx="52" cy="94" rx="22" ry="4" fill="#0f172a" opacity="0.1"/>
        <path class="wing-flap" d="M 38,82 Q 28,65 44,55 Q 48,32 58,28 Q 68,18 76,24 Q 84,35 72,46 Q 58,52 52,68 Z" fill="url(#g_heron)"/>
        <path d="M 72,26 L 96,28 L 74,35 Z" fill="#eab308"/>
        <g class="bird-blink"><circle cx="68" cy="28" r="3.6" fill="#fff"/><circle cx="68" cy="28" r="1.6" fill="#0f172a"/></g></svg>"""},
    {"id": "grackle", "name": "Great-tailed Grackle", "emoji": "🐦‍⬛", "inat": "Quiscalus mexicanus",
     "marks": ["Iridescent black feathers", "Bright yellow inquiring eyes"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <radialGradient id="g_grac" cx="38%" cy="30%" r="80%"><stop offset="0%" stop-color="#334155"/><stop offset="60%" stop-color="#1e293b"/><stop offset="100%" stop-color="#0f172a"/></radialGradient></defs>
        <ellipse cx="52" cy="92" rx="24" ry="4" fill="#0f172a" opacity="0.12"/>
        <path d="M 10,88 L 32,65 L 16,98 Z" fill="#0f172a"/>
        <path class="wing-flap" d="M 35,75 Q 20,55 40,35 Q 60,15 75,30 Q 90,50 75,70 Q 55,90 35,75 Z" fill="url(#g_grac)"/>
        <path d="M 42,50 Q 55,56 66,50" stroke="#4c1d95" stroke-width="2" fill="none" opacity="0.4"/>
        <path d="M 70,35 L 92,38 L 72,46 Z" fill="#0f172a"/>
        <g class="bird-blink"><circle cx="65" cy="34" r="4.5" fill="#facc15"/><circle cx="65" cy="34" r="1.8" fill="#0f172a"/></g></svg>"""},
    {"id": "robin", "name": "American Robin", "emoji": "🐦", "inat": "Turdus migratorius",
     "marks": ["Warm brick-red breast", "Dark gray back & white eye arc"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <radialGradient id="g_rob" cx="38%" cy="30%" r="80%"><stop offset="0%" stop-color="#64748b"/><stop offset="70%" stop-color="#475569"/><stop offset="100%" stop-color="#334155"/></radialGradient></defs>
        <ellipse cx="52" cy="92" rx="24" ry="4" fill="#0f172a" opacity="0.12"/>
        <path class="wing-flap" d="M 35,75 Q 20,55 40,35 Q 60,15 75,30 Q 90,50 75,70 Q 55,90 35,75 Z" fill="url(#g_rob)"/>
        <path d="M 45,42 Q 65,48 74,62 Q 58,82 40,65 Z" fill="#c2410c"/>
        <path d="M 70,35 L 88,40 L 72,46 Z" fill="#eab308"/>
        <g class="bird-blink"><circle cx="65" cy="34" r="3.6" fill="#fff"/><circle cx="65" cy="34" r="1.6" fill="#0f172a"/></g></svg>"""},
    {"id": "titmouse", "name": "Tufted Titmouse", "emoji": "🐦", "inat": "Baeolophus bicolor",
     "marks": ["Cute gray crest & button eyes", "Subtle rusty-orange sides"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <radialGradient id="g_tit" cx="38%" cy="30%" r="80%"><stop offset="0%" stop-color="#94a3b8"/><stop offset="70%" stop-color="#64748b"/><stop offset="100%" stop-color="#475569"/></radialGradient></defs>
        <ellipse cx="52" cy="92" rx="24" ry="4" fill="#0f172a" opacity="0.12"/>
        <path class="wing-flap" d="M 35,75 Q 20,55 40,35 Q 60,15 75,30 Q 90,50 75,70 Q 55,90 35,75 Z" fill="url(#g_tit)"/>
        <path d="M 52,22 L 68,8 L 64,30 Z" fill="#475569"/>
        <path d="M 40,58 Q 50,68 58,58" fill="#ea580c"/>
        <path d="M 70,35 L 86,38 L 72,44 Z" fill="#1e293b"/>
        <g class="bird-blink"><circle cx="65" cy="32" r="3.6" fill="#fff"/><circle cx="65" cy="32" r="1.6" fill="#0f172a"/></g></svg>"""},
    {"id": "hummingbird", "name": "Ruby-throated Hummingbird", "emoji": "🐦", "inat": "Archilochus colubris",
     "marks": ["Metallic emerald back", "Ruby red glowing throat patch"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <radialGradient id="g_hum" cx="38%" cy="30%" r="80%"><stop offset="0%" stop-color="#34d399"/><stop offset="65%" stop-color="#10b981"/><stop offset="100%" stop-color="#047857"/></radialGradient></defs>
        <ellipse cx="52" cy="92" rx="20" ry="3.5" fill="#0f172a" opacity="0.1"/>
        <path class="wing-flap-fast" d="M 35,75 Q 20,55 40,35 Q 60,15 75,30 Q 90,50 75,70 Q 55,90 35,75 Z" fill="url(#g_hum)"/>
        <path d="M 60,36 Q 72,40 66,52 Z" fill="#ef4444"/>
        <path d="M 70,33 L 98,36 L 72,40 Z" fill="#0f172a"/>
        <g class="bird-blink"><circle cx="64" cy="32" r="3" fill="#fff"/><circle cx="64" cy="32" r="1.2" fill="#0f172a"/></g></svg>"""},
    {"id": "owl", "name": "Barred Owl", "emoji": "🦉", "inat": "Strix varia",
     "marks": ["Horizontal throat bars & round face", "Large soulful dark brown eyes"],
     "svg": """<svg viewBox="0 0 100 100" class="bird-svg"><defs>
        <radialGradient id="g_owl" cx="38%" cy="30%" r="80%"><stop offset="0%" stop-color="#a16207"/><stop offset="65%" stop-color="#78350f"/><stop offset="100%" stop-color="#451a03"/></radialGradient></defs>
        <ellipse cx="52" cy="92" rx="24" ry="4" fill="#0f172a" opacity="0.12"/>
        <path class="owl-sway" d="M 35,75 Q 20,55 40,35 Q 60,15 75,30 Q 90,50 75,70 Q 55,90 35,75 Z" fill="url(#g_owl)"/>
        <path d="M 40,48 Q 58,62 72,48 Q 58,82 40,62 Z" fill="#fef3c7"/>
        <line x1="44" y1="55" x2="68" y2="55" stroke="#78350f" stroke-width="2.5"/>
        <line x1="46" y1="62" x2="66" y2="62" stroke="#78350f" stroke-width="2.5"/>
        <path d="M 62,38 L 70,44 L 60,44 Z" fill="#eab308"/>
        <g class="bird-blink"><circle cx="58" cy="34" r="4" fill="#0f172a"/><circle cx="56.8" cy="32.8" r="1" fill="#fff"/></g>
        <g class="bird-blink"><circle cx="70" cy="34" r="4" fill="#0f172a"/><circle cx="68.8" cy="32.8" r="1" fill="#fff"/></g></svg>"""},
]

# ==========================================
# 3. FACTS / VIDEOS / BADGES
# ==========================================
BIRD_FACTS = [
    "Birds have hollow bones which make their bodies super light for flying!",
    "Northern Mockingbirds can mimic over 30 different bird songs and animal sounds.",
    "A hummingbird's wings can flap up to 80 times every single second!",
    "Barred Owls make a distinct hooting call that sounds like: 'Who cooks for you?'",
    "Blue Jays gather and bury acorns, helping new oak trees grow across Texas.",
    "Greater Roadrunners can run up to 20 miles per hour across the land!",
    "Northern Cardinals get their vivid red color from pigments in the seeds they eat.",
    "Birds use their beaks like hands to weave nests out of twigs, grass, and moss.",
    "Great Blue Herons stand completely still in water waiting for fish to swim by.",
    "Feathers help keep birds dry in the rain and warm during cold winter nights.",
    "Chickadees can remember thousands of hiding places where they stored seeds!",
    "Red-tailed Hawks have keen eyesight that is 8 times sharper than human vision.",
]

SHOWTIME_VIDEOS = [
    {"title": "Learn About Baby Birds - Nat Geo Kids", "video_id": "JF4pBKXUAFc", "emoji": "🐣"},
    {"title": "Merlin Bird ID Demo - Cornell Lab", "video_id": "xmSUOLxyatY", "emoji": "🔍"},
    {"title": "Blue Jay - Cornell Lab / Macaulay Library", "video_id": "QbWIrZUlX3Q", "emoji": "🐦"},
    {"title": "50 Birds, 50 States - Nat Geo Kids", "video_id": "Av_-_8B_ePQ", "emoji": "🗺️"},
]

PRIZE_BADGES = [
    {"id": "hatchling", "name": "Hatchling Spotter", "goal": 1, "emoji": "🥚", "color": "#94a3b8"},
    {"id": "fledgling", "name": "Fledgling Birder", "goal": 4, "emoji": "🐤", "color": "#22c55e"},
    {"id": "flock_leader", "name": "Flock Leader", "goal": 8, "emoji": "🐦", "color": "#0ea5e9"},
    {"id": "master_birder", "name": "Master Birder", "goal": 12, "emoji": "🦅", "color": "#f59e0b"},
    {"id": "chirp_legend", "name": "ChirpQuest Legend", "goal": 16, "emoji": "🏆", "color": "#a855f7"},
]

# ==========================================
# 4. REAL BIRD PHOTOS via iNaturalist (open, CC-licensed)
# ==========================================
_photo_cache = {}

def fetch_inat_photo(scientific_name):
    """Return a real CC-licensed photo URL for a species, or None. Cached in memory."""
    if scientific_name in _photo_cache:
        return _photo_cache[scientific_name]
    try:
        r = requests.get(
            "https://api.inaturalist.org/v1/taxa",
            params={"q": scientific_name, "rank": "species", "per_page": 1},
            timeout=8,
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        url = None
        if results and results[0].get("default_photo"):
            # medium-sized square-ish photo
            url = results[0]["default_photo"].get("medium_url")
        _photo_cache[scientific_name] = url
        return url
    except Exception as e:
        log.warning("iNat photo fetch failed for %s: %s", scientific_name, e)
        _photo_cache[scientific_name] = None
        return None

# ==========================================
# 5. FRONTEND
# ==========================================
WEB_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ChirpQuest</title>
<style>
:root { --teal-primary:#0f766e; --card-bg:#ffffff; --text-main:#1e293b; }
body { font-family:'Comic Sans MS',cursive,sans-serif; background:linear-gradient(135deg,#f0fdf4 0%,#e0f2fe 100%); margin:0; color:var(--text-main); min-height:100vh; display:flex; flex-direction:column; overflow-x:hidden; position:relative; }

/* ANIMATIONS */
@keyframes wingFlap { 0%,100%{transform:translateY(0) rotate(0deg);} 50%{transform:translateY(-2px) rotate(-5deg);} }
@keyframes wingFlapFast { 0%,100%{transform:translateY(0) scaleY(1);} 50%{transform:translateY(-1px) scaleY(0.85);} }
@keyframes blink { 0%,92%,100%{transform:scaleY(1);} 96%{transform:scaleY(0.1);} }
@keyframes owlSway { 0%,100%{transform:rotate(0deg);} 50%{transform:rotate(2.5deg);} }
@keyframes floatUpDown { 0%,100%{transform:translateY(0);} 50%{transform:translateY(-10px);} }
@keyframes float3d { 0%,100%{transform:translateY(0) rotateY(0deg) rotateX(0deg);} 25%{transform:translateY(-8px) rotateY(8deg) rotateX(3deg);} 75%{transform:translateY(-4px) rotateY(-8deg) rotateX(-2deg);} }
@keyframes gentleBob { 0%,100%{transform:translateY(0) rotate(0deg);} 50%{transform:translateY(-6px) rotate(-1.5deg);} }
@keyframes popIn { 0%{transform:scale(0.7);opacity:0;} 60%{transform:scale(1.08);opacity:1;} 100%{transform:scale(1);} }
@keyframes shine { 0%{background-position:-150% 0;} 100%{background-position:250% 0;} }
@keyframes badgeGlow { 0%,100%{box-shadow:0 0 0 rgba(245,158,11,0);} 50%{box-shadow:0 0 24px rgba(245,158,11,0.55);} }
@keyframes confettiFall { 0%{transform:translateY(-20px) rotate(0deg);opacity:1;} 100%{transform:translateY(220px) rotate(360deg);opacity:0;} }

.mascot-svg { animation:gentleBob 3s ease-in-out infinite; transform-origin:center bottom; }
.mascot-wing { transform-origin:52px 66px; animation:wingFlap 1.3s ease-in-out infinite; }
.mascot-eye, .bird-blink { transform-box: fill-box; transform-origin: center; animation:blink 4s infinite; }

.bird-svg { animation:float3d 5s ease-in-out infinite; transform-origin:center bottom; transform-style:preserve-3d; }
.wing-flap { transform-origin:55px 55px; animation:wingFlap 1.5s ease-in-out infinite; }
.wing-flap-fast { transform-origin:55px 55px; animation:wingFlapFast 0.3s ease-in-out infinite; }
.owl-sway { transform-origin:55px 90px; animation:owlSway 3s ease-in-out infinite; }
.bird-page:hover .bird-svg { animation-duration:2.5s; }

.emoji-icon { display:inline-block; animation:floatUpDown 2.6s ease-in-out infinite; }
.bg-emoji { position:fixed; font-size:28px; opacity:0.12; pointer-events:none; animation:floatUpDown 6s ease-in-out infinite; z-index:0; }

/* LAYOUT */
.app-layout { display:flex; flex:1; min-height:0; position:relative; z-index:1; }
.sidebar { width:260px; background:#0f766e; color:#fff; display:flex; flex-direction:column; box-shadow:4px 0 15px rgba(0,0,0,0.05); z-index:10; }
.logo-area { padding:25px 20px; display:flex; align-items:center; gap:12px; border-bottom:1px solid rgba(255,255,255,0.1); }
.logo-badge { width:44px; height:44px; background:rgba(255,255,255,0.15); border-radius:14px; display:flex; align-items:center; justify-content:center; border:2px solid rgba(255,255,255,0.3); flex-shrink:0; }
.logo-text-wrap h1 { font-size:1.4em; margin:0; letter-spacing:0.5px; color:#fff; }
.logo-text-wrap p { font-size:0.75em; margin:0; color:#99f6e4; }
.nav-links { padding:20px 15px; display:flex; flex-direction:column; gap:8px; flex:1; }
.nav-btn { background:transparent; border:none; color:#ccfbf1; padding:12px 18px; border-radius:12px; text-align:left; font-size:1em; font-weight:bold; cursor:pointer; transition:all 0.2s; display:flex; align-items:center; gap:12px; }
.nav-btn:hover { background:rgba(255,255,255,0.1); color:#fff; transform:translateX(4px); }
.nav-btn.active { background:#14b8a6; color:#fff; box-shadow:0 4px 12px rgba(20,184,166,0.3); }

.main-content { flex:1; padding:30px; overflow-y:auto; display:flex; justify-content:center; align-items:flex-start; }
.content-container { width:100%; max-width:1000px; }
.tab-content { display:none; }
.tab-content.active { display:block; animation:popIn 0.35s ease-out; }
.box { background:var(--card-bg); padding:30px; border-radius:28px; box-shadow:0 10px 25px rgba(15,118,110,0.08); border:3px solid #ccfbf1; box-sizing:border-box; }

.mascot-banner { display:flex; align-items:center; background:linear-gradient(135deg,#f0fdf4 0%,#ccfbf1 100%); border:3px solid #99f6e4; border-radius:22px; padding:20px 25px; margin-bottom:25px; gap:20px; }
.mascot-display { width:90px; height:100px; flex-shrink:0; }

.feature-cards { display:flex; gap:15px; margin-top:25px; flex-wrap:wrap; }
.card { background:#f8fafc; padding:20px; border-radius:20px; flex:1; border:2px solid #e2e8f0; min-width:240px; transition:transform 0.25s; }
.card:hover { transform:translateY(-4px); }
.card h2 { margin-top:0; color:#0f766e; font-size:1.2em; }

.book-container { display:flex; flex-wrap:wrap; gap:20px; justify-content:center; margin-top:20px; max-height:640px; overflow-y:auto; padding:10px; }
.bird-page { background:#fff; border:3px solid #e2e8f0; border-radius:22px; padding:16px; width:230px; text-align:center; box-shadow:0 6px 12px rgba(0,0,0,0.03); transition:transform 0.2s,border-color 0.2s; perspective:600px; }
.bird-page:hover { transform:translateY(-6px) scale(1.02); border-color:#14b8a6; }
.bird-stage { height:150px; background:linear-gradient(180deg,#dbeafe 0%,#f0fdf4 60%,#dcfce7 100%); border-radius:16px; border:2px solid #ccfbf1; position:relative; display:flex; justify-content:center; align-items:center; overflow:hidden; }
.bird-photo { width:100%; height:100%; object-fit:cover; border-radius:14px; display:none; }
.bird-photo.loaded { display:block; animation:popIn 0.4s ease-out; }
.photo-tag { position:absolute; bottom:4px; right:6px; font-size:0.6em; color:#fff; background:rgba(0,0,0,0.4); padding:1px 5px; border-radius:6px; }
.bird-sprite-container { width:110px; height:110px; display:inline-block; }
.bird-name-row { display:flex; align-items:center; justify-content:center; gap:6px; }
.field-marks { text-align:left; background:#f8fafc; padding:10px; border-radius:12px; border:1px solid #e2e8f0; margin-top:12px; font-size:0.82em; }
.field-marks ul { margin:4px 0 0 0; padding-left:16px; color:#475569; }
.photo-toggle { margin-top:8px; font-size:0.72em; color:#0f766e; background:#f0fdfa; border:1px solid #99f6e4; border-radius:8px; padding:4px 8px; cursor:pointer; }

.checklist-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:12px; margin-top:20px; max-height:550px; overflow-y:auto; padding:5px; }
.check-item { background:#f8fafc; border:2px solid #e2e8f0; padding:14px 16px; border-radius:14px; display:flex; align-items:center; gap:12px; font-weight:bold; cursor:pointer; transition:all 0.2s; color:#334155; }
.check-item:hover { background:#f0fdf4; border-color:#14b8a6; color:#0f766e; }
.check-item input { width:20px; height:20px; accent-color:#0f766e; cursor:pointer; }
.check-item.checked { background:#dcfce7; border-color:#22c55e; }

.chat-box { display:flex; flex-direction:column; height:380px; border:3px solid #e2e8f0; border-radius:20px; background:#f8fafc; padding:20px; overflow-y:auto; gap:12px; }
.chat-msg { padding:12px 18px; border-radius:16px; max-width:75%; font-weight:bold; font-size:0.95em; animation:popIn 0.25s ease-out; white-space:pre-wrap; }
.bot-msg { background:#e0f2fe; color:#0369a1; border:2px solid #bae6fd; align-self:flex-start; }
.user-msg { background:#dcfce7; color:#15803d; border:2px solid #bbf7d0; align-self:flex-end; }
.typing-msg { background:#e0f2fe; color:#0369a1; border:2px solid #bae6fd; align-self:flex-start; padding:12px 18px; border-radius:16px; }
.typing-dot { display:inline-block; width:6px; height:6px; background:#0369a1; border-radius:50%; margin-right:3px; animation:floatUpDown 0.8s infinite; }
.typing-dot:nth-child(2){animation-delay:0.15s;} .typing-dot:nth-child(3){animation-delay:0.3s;}
.chat-controls { display:flex; gap:10px; margin-top:15px; }
.chat-input { flex:1; padding:14px 18px; border-radius:14px; border:3px solid #14b8a6; font-size:1em; font-family:inherit; outline:none; background:#fff; }
.chat-input:focus { box-shadow:0 0 0 3px rgba(20,184,166,0.2); }
.chat-send-btn { background:#0f766e; color:#fff; border:none; padding:14px 28px; border-radius:14px; font-weight:bold; font-size:1em; cursor:pointer; transition:background 0.2s,transform 0.1s; }
.chat-send-btn:hover { background:#115e59; transform:scale(1.05); }
.chat-send-btn:disabled { opacity:0.5; cursor:not-allowed; }

.sound-btn { background:#0ea5e9; color:#fff; border:none; padding:10px 18px; border-radius:12px; font-weight:bold; cursor:pointer; margin-top:10px; transition:background 0.2s,transform 0.1s; }
.sound-btn:hover { background:#0284c7; transform:scale(1.05); }

.video-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:20px; margin-top:20px; }
.video-card { background:#f8fafc; border:3px solid #e2e8f0; border-radius:20px; padding:14px; transition:transform 0.2s,border-color 0.2s; }
.video-card:hover { transform:translateY(-4px); border-color:#14b8a6; }
.video-frame-wrap { position:relative; width:100%; padding-top:56.25%; border-radius:14px; overflow:hidden; background:#000; }
.video-frame-wrap iframe { position:absolute; top:0; left:0; width:100%; height:100%; border:0; }
.video-title { margin:10px 0 0 0; color:#0f766e; font-weight:bold; font-size:0.95em; display:flex; align-items:center; gap:6px; }

.badge-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:18px; margin-top:20px; }
.badge-card { background:#f8fafc; border:3px solid #e2e8f0; border-radius:20px; padding:20px 14px; text-align:center; transition:transform 0.25s; position:relative; }
.badge-card.unlocked { border-color:var(--badge-color,#f59e0b); animation:badgeGlow 2.4s ease-in-out infinite; }
.badge-card.unlocked:hover { transform:translateY(-6px) scale(1.03); }
.badge-emoji { font-size:2.6em; display:block; margin-bottom:8px; filter:grayscale(1); opacity:0.4; }
.badge-card.unlocked .badge-emoji { filter:none; opacity:1; animation:popIn 0.5s ease-out; }
.badge-name { font-weight:bold; color:#334155; }
.badge-card.unlocked .badge-name { color:#0f766e; }
.badge-progress { font-size:0.8em; color:#64748b; margin-top:6px; }
.progress-bar-outer { background:#e2e8f0; border-radius:10px; height:14px; margin-top:20px; overflow:hidden; }
.progress-bar-inner { background:linear-gradient(90deg,#14b8a6,#22c55e,#14b8a6); background-size:200% 100%; height:100%; border-radius:10px; animation:shine 2.5s linear infinite; transition:width 0.6s ease; }
.confetti-piece { position:absolute; width:8px; height:8px; top:0; animation:confettiFall 1.4s ease-in forwards; border-radius:2px; }

@media (max-width:768px){ .app-layout{flex-direction:column;} .sidebar{width:100%;height:auto;} .nav-links{flex-direction:row;flex-wrap:wrap;justify-content:center;} }
</style>
</head>
<body>
<div class="bg-emoji" style="top:8%;left:4%;">🍃</div>
<div class="bg-emoji" style="top:70%;left:90%;animation-delay:1.2s;">🍃</div>
<div class="bg-emoji" style="top:40%;left:96%;animation-delay:2.4s;">☁️</div>

<div class="app-layout">
    <aside class="sidebar">
        <div class="logo-area">
            <div class="logo-badge">
                <svg viewBox="0 0 100 100" style="width:32px;height:32px;">
                    <path d="M 20,80 Q 50,85 80,50 Q 90,30 75,20 Q 55,25 35,45 Q 20,60 20,80 Z" fill="url(#rainbowGrad)"/>
                    <path d="M 32,70 Q 50,75 70,45 Q 60,35 45,50 Z" fill="#fff" opacity="0.3"/>
                    <defs><linearGradient id="rainbowGrad" x1="0%" y1="100%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#ef4444"/><stop offset="20%" stop-color="#f97316"/>
                        <stop offset="40%" stop-color="#eab308"/><stop offset="60%" stop-color="#10b981"/>
                        <stop offset="80%" stop-color="#06b6d4"/><stop offset="100%" stop-color="#8b5cf6"/>
                    </linearGradient></defs>
                </svg>
            </div>
            <div class="logo-text-wrap"><h1>ChirpQuest</h1><p>North Texas Bird Guide</p></div>
        </div>
        <div class="nav-links">
            <button class="nav-btn active" onclick="openTab(event,'welcome')"><span class="emoji-icon">🏠</span> Welcome</button>
            <button class="nav-btn" onclick="openTab(event,'chat')"><span class="emoji-icon">💬</span> Ask Pip</button>
            <button class="nav-btn" onclick="openTab(event,'book')"><span class="emoji-icon">📖</span> Bird Book</button>
            <button class="nav-btn" onclick="openTab(event,'checklist')"><span class="emoji-icon">✅</span> Checklist</button>
            <button class="nav-btn" onclick="openTab(event,'showtime')"><span class="emoji-icon">📺</span> Showtime</button>
            <button class="nav-btn" onclick="openTab(event,'prizes')"><span class="emoji-icon">🏆</span> Prizes</button>
        </div>
    </aside>

    <main class="main-content">
        <div class="content-container">
            <section id="tab-welcome" class="tab-content active">
                <div class="box">
                    <div class="mascot-banner">
                        <div class="mascot-display" id="mascot-container"></div>
                        <div>
                            <h2 style="margin:0 0 5px 0;color:#0f766e;">Meet Pip the Cockatiel!</h2>
                            <p style="margin:0;color:#334155;font-size:0.95em;">Your official ChirpQuest guide. Ask Pip any question in the Ask Pip tab!</p>
                        </div>
                    </div>
                    <h1 style="color:#0f766e;margin-top:0;">Welcome to ChirpQuest! 🐦</h1>
                    <p style="color:#475569;">Explore local North Texas wildlife with real photos, field guides, and interactive features.</p>
                    <div class="feature-cards">
                        <div class="card"><h2>📸 Bird Facts</h2>
                            <ul id="facts-list" style="text-align:left;font-size:0.88em;padding-left:18px;margin:0;color:#475569;"><li>Loading facts...</li></ul></div>
                        <div class="card"><h2>🔊 Bird Sounds</h2>
                            <p id="sound-bird-name" style="font-weight:bold;margin-bottom:5px;color:#0f766e;">Press to play call!</p>
                            <button class="sound-btn" onclick="playRandomBirdCall()">Play Bird Sound 🎵</button></div>
                        <div class="card"><h2>🐦 Bird of the Day</h2>
                            <p id="daily-bird" style="font-weight:bold;font-size:1.1em;color:#0f766e;margin-top:10px;">Loading...</p></div>
                    </div>
                </div>
            </section>

            <section id="tab-chat" class="tab-content">
                <div class="box">
                    <h2 style="color:#0f766e;margin-top:0;">💬 Chat with Pip</h2>
                    <div class="chat-box" id="chat-container">
                        <div class="chat-msg bot-msg">Chirp chirp! I'm Pip the Cockatiel! Ask me anything about North Texas birds!</div>
                    </div>
                    <div class="chat-controls">
                        <input type="text" id="user-input" class="chat-input" placeholder="Type your bird question here..." onkeydown="if(event.key==='Enter') sendChatMessage()">
                        <button class="chat-send-btn" id="send-btn" type="button" onclick="sendChatMessage()">Send</button>
                    </div>
                </div>
            </section>

            <section id="tab-book" class="tab-content">
                <div class="box">
                    <h2 style="color:#0f766e;margin-top:0;">📖 North Texas Field Guide (16 Species)</h2>
                    <p style="color:#475569;">Real Creative-Commons photos load automatically, with 3D illustrated fallbacks. Tap a card to flip between photo and art.</p>
                    <div class="book-container" id="bird-grid"></div>
                </div>
            </section>

            <section id="tab-checklist" class="tab-content">
                <div class="box">
                    <h2 style="color:#0f766e;margin-top:0;">✅ North Texas Bird Log & Checklist</h2>
                    <p style="color:#475569;">Check off every bird as you spot them outdoors across Texas!</p>
                    <div class="progress-bar-outer"><div class="progress-bar-inner" id="checklist-progress-bar" style="width:0%;"></div></div>
                    <div class="checklist-grid" id="checklist-container"></div>
                </div>
            </section>

            <section id="tab-showtime" class="tab-content">
                <div class="box">
                    <h2 style="color:#0f766e;margin-top:0;">📺 Showtime: Bird Videos</h2>
                    <p style="color:#475569;">Watch real bird videos from Cornell Lab and Nat Geo Kids!</p>
                    <div class="video-grid" id="video-grid"></div>
                </div>
            </section>

            <section id="tab-prizes" class="tab-content">
                <div class="box">
                    <h2 style="color:#0f766e;margin-top:0;">🏆 Prizes & Badges</h2>
                    <p style="color:#475569;">Unlock badges as you check off birds on your checklist!</p>
                    <div class="badge-grid" id="badge-grid"></div>
                </div>
            </section>
        </div>
    </main>
</div>

<script>
let allBirds = [];
let checkedSet = new Set(JSON.parse(localStorage.getItem("chirpquest_checked") || "[]"));

function openTab(evt, tabName){
    document.querySelectorAll('.tab-content').forEach(c=>c.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));
    document.getElementById('tab-'+tabName).classList.add('active');
    if(evt&&evt.currentTarget) evt.currentTarget.classList.add('active');
    if(tabName==='chat') setTimeout(()=>{const i=document.getElementById("user-input"); if(i)i.focus();},100);
    if(tabName==='prizes') renderBadges();
}

function playRandomBirdCall(){
    if(allBirds.length===0) return;
    const b = allBirds[Math.floor(Math.random()*allBirds.length)];
    document.getElementById('sound-bird-name').innerText = `${b.emoji||"🐦"} ${b.name}`;
    const ctx = new (window.AudioContext||window.webkitAudioContext)();
    const osc = ctx.createOscillator(); const gain = ctx.createGain();
    osc.type='sine'; const now=ctx.currentTime;
    osc.frequency.setValueAtTime(1200,now);
    osc.frequency.exponentialRampToValueAtTime(2800,now+0.1);
    osc.frequency.exponentialRampToValueAtTime(1500,now+0.2);
    osc.frequency.exponentialRampToValueAtTime(3200,now+0.35);
    gain.gain.setValueAtTime(0.3,now);
    gain.gain.exponentialRampToValueAtTime(0.01,now+0.4);
    osc.connect(gain); gain.connect(ctx.destination);
    osc.start(now); osc.stop(now+0.4);
}

async function sendChatMessage(){
    const input=document.getElementById("user-input");
    const btn=document.getElementById("send-btn");
    const text=input.value.trim(); if(!text) return;
    const c=document.getElementById("chat-container");
    c.innerHTML += `<div class="chat-msg user-msg">${text}</div>`;
    input.value=""; c.scrollTop=c.scrollHeight;
    btn.disabled=true;
    const tid="typing-"+Date.now();
    c.innerHTML += `<div class="typing-msg" id="${tid}"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></div>`;
    c.scrollTop=c.scrollHeight;
    try{
        const r=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:text})});
        const data=await r.json();
        document.getElementById(tid)?.remove();
        c.innerHTML += `<div class="chat-msg bot-msg">${data.reply}</div>`;
        c.scrollTop=c.scrollHeight;
    }catch(e){
        document.getElementById(tid)?.remove();
        c.innerHTML += `<div class="chat-msg bot-msg">Chirp! Something ruffled my feathers. Try again?</div>`;
    }finally{
        btn.disabled=false;
        input.focus();
    }
}

function fireConfetti(container){
    const colors=["#ef4444","#f97316","#eab308","#22c55e","#0ea5e9","#a855f7"];
    for(let i=0;i<18;i++){
        const p=document.createElement("div"); p.className="confetti-piece";
        p.style.left=Math.random()*100+"%";
        p.style.background=colors[Math.floor(Math.random()*colors.length)];
        p.style.animationDelay=(Math.random()*0.3)+"s";
        container.appendChild(p); setTimeout(()=>p.remove(),1600);
    }
}

async function renderBadges(){
    let badges=[];
    try{ badges=await (await fetch("/api/prizes")).json(); }catch(e){ return; }
    const count=checkedSet.size;
    const grid=document.getElementById("badge-grid"); grid.innerHTML="";
    badges.forEach(b=>{
        const unlocked=count>=b.goal;
        const card=document.createElement("div");
        card.className="badge-card"+(unlocked?" unlocked":"");
        card.style.setProperty("--badge-color",b.color);
        card.innerHTML=`<span class="badge-emoji">${b.emoji}</span><div class="badge-name">${b.name}</div><div class="badge-progress">${Math.min(count,b.goal)} / ${b.goal} birds spotted</div>`;
        grid.appendChild(card);
        if(unlocked&&!sessionStorage.getItem("celebrated-"+b.id)){
            sessionStorage.setItem("celebrated-"+b.id,"1");
            setTimeout(()=>fireConfetti(card),150);
        }
    });
}

// Load a real photo into a card; keep the SVG as fallback
function loadBirdPhoto(bird){
    if(!bird.inat) return;
    fetch("/api/photo?name="+encodeURIComponent(bird.inat))
        .then(r=>r.json())
        .then(d=>{
            if(d && d.url){
                const img=document.getElementById("photo-"+bird.id);
                if(img){
                    img.onload=()=>{ img.classList.add("loaded"); const s=document.getElementById("sprite-"+bird.id); if(s)s.style.display="none"; };
                    img.src=d.url;
                }
            }
        }).catch(()=>{});
}

function toggleView(id){
    const img=document.getElementById("photo-"+id);
    const sprite=document.getElementById("sprite-"+id);
    if(!img||!img.src){ return; }
    if(img.style.display==="none"){ img.style.display="block"; sprite.style.display="none"; }
    else { img.style.display="none"; sprite.style.display="inline-block"; }
}

document.addEventListener("DOMContentLoaded", async ()=>{
    try{ const m=await (await fetch("/api/mascot")).json(); document.getElementById("mascot-container").innerHTML=m.svg; }catch(e){}
    try{ const f=await (await fetch("/api/facts")).json(); document.getElementById("facts-list").innerHTML=f.map(x=>`<li style="margin-bottom:6px;">${x}</li>`).join(""); }catch(e){}
    try{
        const v=await (await fetch("/api/videos")).json();
        document.getElementById("video-grid").innerHTML=v.map(x=>`
            <div class="video-card">
                <div class="video-frame-wrap"><iframe src="https://www.youtube.com/embed/${x.video_id}" title="${x.title}" allowfullscreen loading="lazy"></iframe></div>
                <p class="video-title">${x.emoji} ${x.title}</p>
            </div>`).join("");
    }catch(e){}

    try{
        allBirds=await (await fetch("/api/birds")).json();
        const today=allBirds[Math.floor(Math.random()*allBirds.length)];
        document.getElementById("daily-bird").innerText=`${today.emoji||"🐦"} ${today.name}`;

        const grid=document.getElementById("bird-grid"); grid.innerHTML="";
        allBirds.forEach(bird=>{
            const marks=bird.marks.map(m=>`<li>${m}</li>`).join("");
            grid.innerHTML+=`
                <div class="bird-page">
                    <h3 class="bird-name-row" style="margin:5px 0 10px 0;color:#0f766e;font-size:1.05em;">
                        <span class="emoji-icon">${bird.emoji||"🐦"}</span> ${bird.name}
                    </h3>
                    <div class="bird-stage">
                        <div class="bird-sprite-container" id="sprite-${bird.id}">${bird.svg}</div>
                        <img class="bird-photo" id="photo-${bird.id}" alt="${bird.name}">
                        <span class="photo-tag">real photo</span>
                    </div>
                    <div class="field-marks"><strong style="color:#0f766e;">Key Marks:</strong><ul>${marks}</ul></div>
                    <div class="photo-toggle" onclick="toggleView('${bird.id}')">🔄 Photo / Art</div>
                </div>`;
        });
        // fetch real photos after cards exist
        allBirds.forEach(b=>loadBirdPhoto(b));

        const cl=document.getElementById("checklist-container"); cl.innerHTML="";
        allBirds.forEach(bird=>{
            const on=checkedSet.has(bird.id);
            cl.innerHTML+=`
                <label class="check-item ${on?'checked':''}" id="label-${bird.id}">
                    <input type="checkbox" id="check-${bird.id}" ${on?'checked':''} onchange="toggleBird('${bird.id}')">
                    <span>${bird.emoji||"🐦"} ${bird.name}</span>
                </label>`;
        });
        updateChecklistProgress();
    }catch(e){ console.error("Error loading birds:",e); }
});

function toggleBird(id){
    const cb=document.getElementById("check-"+id);
    const label=document.getElementById("label-"+id);
    if(cb.checked){ checkedSet.add(id); label.classList.add("checked"); }
    else { checkedSet.delete(id); label.classList.remove("checked"); }
    localStorage.setItem("chirpquest_checked",JSON.stringify([...checkedSet]));
    updateChecklistProgress();
}

function updateChecklistProgress(){
    const total=allBirds.length||1;
    const pct=Math.round((checkedSet.size/total)*100);
    const bar=document.getElementById("checklist-progress-bar");
    if(bar) bar.style.width=pct+"%";
}
</script>
</body>
</html>
"""

# ==========================================
# 6. ROUTES
# ==========================================
@app.route("/")
def home():
    return render_template_string(WEB_PAGE)

@app.route("/api/mascot")
def get_mascot():
    return jsonify(COCKATIEL_MASCOT)

@app.route("/api/birds")
def get_texas_birds():
    return jsonify(TEXAS_BIRDS)

@app.route("/api/facts")
def get_random_facts():
    return jsonify(random.sample(BIRD_FACTS, 5))

@app.route("/api/videos")
def get_videos():
    return jsonify(SHOWTIME_VIDEOS)

@app.route("/api/prizes")
def get_prizes():
    return jsonify(PRIZE_BADGES)

@app.route("/api/photo")
def get_photo():
    name = request.args.get("name", "")
    url = fetch_inat_photo(name) if name else None
    return jsonify({"url": url})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "")
    log.info("Chat request: %r", user_message)
    reply = call_gemini(user_message)
    log.info("Chat reply: %r", reply)
    return jsonify({"reply": reply})

# ==========================================
# 7. RUNNER
# ==========================================
if __name__ == "__main__":
    log.info("Starting ChirpQuest on http://127.0.0.1:5000")
    key = get_current_gemini_key()
    if key in ("DUMMY_TEST_KEY_REPLACE_ME", "PUT_YOUR_KEY_HERE", ""):
        log.warning("No real Gemini key set. Set it with:  export GEMINI_API_KEY='your_key'")
    app.run(debug=True, host="127.0.0.1", port=5000, load_dotenv=False)