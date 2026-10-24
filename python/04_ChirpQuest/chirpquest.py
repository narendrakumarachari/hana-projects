# chirpquest.py - ChirpQuest: North Texas bird guide for kids
# (cartoon birds, live iNaturalist sightings map, Wikipedia facts, Gemini chat + Photo ID, quiz, videos)

import base64
import datetime
import json
import os
import random
import re
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor
import requests
from flask import Flask, Response, jsonify, request

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
# Tried in order. If one is busy (503) or gone (404), Pip moves to the next one.
# Fastest free model first (timed Oct 24, 2026); gemini-flash-latest kept timing out.
GEMINI_MODELS = [
    "gemini-3.1-flash-lite",     # ~1 s
    "gemini-3.5-flash-lite",     # newer, ~5 s
    "gemini-flash-lite-latest",  # Google's alias for the current lite model
]
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

def call_gemini(user_message, retries=None, transient_retries=2, model_index=0):
    if retries is None:
        retries = len(GEMINI_API_KEYS)
    key = get_current_gemini_key()
    if key in ("DUMMY_TEST_KEY_REPLACE_ME", "PUT_YOUR_KEY_HERE", ""):
        log.warning("Gemini key is a placeholder — set GEMINI_API_KEY env var. Using fallback reply.")
        return generate_bot_reply_fallback(user_message)

    model = GEMINI_MODELS[model_index]
    has_next_model = model_index + 1 < len(GEMINI_MODELS)
    url = GEMINI_URL_TEMPLATE.format(model=model)
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
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        log.info("Gemini HTTP %s (%s)", resp.status_code, model)
        # ---- DEBUG: print the raw response so you can see exactly what's wrong ----
        try:
            log.debug("Gemini raw response: %s", resp.text[:1500])
        except Exception:
            pass

        if resp.status_code in (400, 401, 403, 429) and retries > 0:
            log.warning("Gemini error %s — rotating key and retrying.", resp.status_code)
            rotate_gemini_key()
            return call_gemini(user_message, retries=retries - 1, transient_retries=transient_retries,
                               model_index=model_index)

        if resp.status_code in (404, 500, 502, 503, 504) and has_next_model:
            log.warning("Gemini model %s returned %s — trying the next model.", model, resp.status_code)
            return call_gemini(user_message, retries=retries, transient_retries=transient_retries,
                               model_index=model_index + 1)

        if resp.status_code in (500, 502, 503, 504) and transient_retries > 0:
            log.warning(
                "Gemini transient error %s — retrying (%d attempt(s) left).",
                resp.status_code, transient_retries,
            )
            time.sleep(1.5)
            return call_gemini(user_message, retries=retries, transient_retries=transient_retries - 1,
                               model_index=model_index)

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
        if isinstance(e, requests.exceptions.Timeout) and has_next_model:
            log.warning("Gemini model %s timed out — trying the next model.", model)
            return call_gemini(user_message, retries=retries, transient_retries=transient_retries,
                               model_index=model_index + 1)
        if transient_retries > 0:
            log.warning("Gemini network error (%s) — retrying (%d attempt(s) left).", e, transient_retries)
            return call_gemini(user_message, retries=retries, transient_retries=transient_retries - 1,
                               model_index=model_index)
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
# 1. MASCOT (Pip) — cartoon cockatiel, same style as the Bird Book cartoons
# ==========================================
COCKATIEL_MASCOT = {
    "name": "Pip the Cockatiel",
    "role": "ChirpQuest Guide",
    "svg": """<svg viewBox="0 -8 120 148" class="mascot-svg" role="img" aria-label="Pip the Cockatiel">
        <defs><clipPath id="pipHead"><circle cx="70" cy="54" r="24"/></clipPath>
              <clipPath id="pipBodyClip"><ellipse cx="56" cy="96" rx="27" ry="30"/></clipPath></defs>
        <ellipse cx="58" cy="133" rx="28" ry="5" fill="#0f172a" opacity="0.12"/>
        <path d="M40,104 L12,132 L24,137 L50,112 Z" fill="#6b7280" stroke="#1e293b" stroke-width="2.5" stroke-linejoin="round"/>
        <path d="M50,120 L50,129 M45,129 L55,129 M62,120 L62,129 M57,129 L67,129" stroke="#d8a7a7" stroke-width="3.2" stroke-linecap="round"/>
        <ellipse cx="56" cy="96" rx="27" ry="30" fill="#9ca3af"/>
        <g clip-path="url(#pipBodyClip)"><ellipse cx="66" cy="106" rx="19" ry="22" fill="#d1d5db"/></g>
        <ellipse cx="56" cy="96" rx="27" ry="30" fill="none" stroke="#1e293b" stroke-width="2.5"/>
        <g class="mascot-wing">
            <path d="M40,82 Q58,74 68,92 Q60,118 34,112 Q28,94 40,82 Z" fill="#6b7280"/>
            <path d="M44,86 Q56,82 62,92 Q54,98 42,96 Z" fill="#f8fafc"/>
            <path d="M40,82 Q58,74 68,92 Q60,118 34,112 Q28,94 40,82 Z" fill="none" stroke="#1e293b" stroke-width="2.2" stroke-linejoin="round"/>
        </g>
        <g class="mascot-crest" stroke-linejoin="round" stroke-linecap="round">
            <path d="M58,40 Q52,38 47,33 L53,31 Q47,27 44,21 L50,19 Q45,14 43,6 L80,34 Z"
                  fill="#facc15" stroke="#1e293b" stroke-width="2.4"/>
            <path d="M50,15 L76,34 L64,36 Z" fill="#fde68a"/>
            <path d="M48,12 L71,30" stroke="#fef9c3" stroke-width="1.6" fill="none"/>
        </g>
        <circle cx="70" cy="54" r="24" fill="#fde68a"/>
        <g clip-path="url(#pipHead)"><ellipse cx="50" cy="62" rx="16" ry="24" fill="#9ca3af"/></g>
        <circle cx="70" cy="54" r="24" fill="none" stroke="#1e293b" stroke-width="2.5"/>
        <circle cx="78" cy="64" r="7.5" fill="#fb923c"/>
        <g class="mascot-eye">
            <circle cx="78" cy="48" r="7.5" fill="#ffffff" stroke="#1e293b" stroke-width="2"/>
            <circle cx="79.5" cy="48.8" r="4.4" fill="#0f172a"/>
            <circle cx="81.2" cy="46.4" r="1.8" fill="#ffffff"/>
        </g>
        <path d="M91,50 Q102,50 100,61 L96,57 L91,61 Z" fill="#a8a29e" stroke="#1e293b" stroke-width="2" stroke-linejoin="round"/>
    </svg>"""
}

# ==========================================
# 2. NORTH TEXAS BIRDS
# ==========================================
# "inat"    = scientific name, used to pull REAL photos, sightings and seasons from iNaturalist.
# "habitat" = backyard / water / open (fields & sky) / night — the Bird Book filter chips.
# "art"     = recipe for the cartoon drawing (see cartoon_bird_svg below).
# "call"    = recipe for a made-up synthesized call (played in the browser with Web Audio).
#             notes are [start Hz, end Hz, seconds, pause]. They are just for fun, NOT real recordings.
TEXAS_BIRDS = [
    {"id": "cardinal", "name": "Northern Cardinal", "emoji": "❤️", "inat": "Cardinalis cardinalis", "habitat": "backyard",
     "marks": ["Vivid red body & tall crest", "Black mask around a thick orange beak"],
     "art": {"body": "#dc2626", "belly": "#ef4444", "head": "#dc2626", "wing": "#b91c1c", "tail_color": "#b91c1c",
             "crest": "#dc2626", "mask": "#1f1416", "beak": "#fb923c", "beak_type": "cone", "tail": "long"},
     "call": {"notes": [[4000, 2000, .16, .05]] * 3 + [[2200, 3600, .09, .03]] * 3}},
    {"id": "bluejay", "name": "Blue Jay", "emoji": "💙", "inat": "Cyanocitta cristata", "habitat": "backyard",
     "marks": ["Bright blue crest & back", "Black necklace across a white chest"],
     "art": {"body": "#3b82f6", "belly": "#f1f5f9", "head": "#3b82f6", "wing": "#2563eb", "tail_color": "#2563eb",
             "crest": "#3b82f6", "cheek": "#f8fafc", "necklace": "#0f172a", "wing_bars": "#0f172a", "wing_tips": "#ffffff",
             "beak": "#1e293b", "beak_type": "small", "tail": "long"},
     "call": {"wave": "sawtooth", "vol": .35, "buzz": 2200, "notes": [[2600, 1900, .18, .12]] * 3}},
    {"id": "mockingbird", "name": "Northern Mockingbird", "emoji": "🎶", "inat": "Mimus polyglottos", "habitat": "backyard",
     "marks": ["Texas State Bird!", "Gray coat with flashy white wing patches"],
     "art": {"body": "#9ca3af", "belly": "#f3f4f6", "head": "#9ca3af", "wing": "#4b5563", "tail_color": "#4b5563",
             "wing_patch": "#ffffff", "beak": "#1f2937", "beak_type": "thin", "tail": "long"},
     "call": {"wave": "triangle", "mimic": True, "notes": []}},
    {"id": "flycatcher", "name": "Scissor-tailed Flycatcher", "emoji": "✂️", "inat": "Tyrannus forficatus", "habitat": "open",
     "marks": ["Super-long scissor tail", "Salmon-pink sides under the wings"],
     "art": {"body": "#e5e7eb", "belly": "#fecdd3", "flanks": "#fb7185", "head": "#e5e7eb", "wing": "#374151",
             "tail_color": "#1f2937", "beak": "#111827", "beak_type": "thin", "tail": "scissor"},
     "call": {"wave": "square", "vol": .22, "notes": [[2600, 3200, .035, .06]] * 5 + [[1800, 3400, .25, 0]]}},
    {"id": "dove", "name": "Mourning Dove", "emoji": "🕊️", "inat": "Zenaida macroura", "habitat": "backyard",
     "marks": ["Soft tan teardrop body & small head", "Black spots on the wings"],
     "art": {"shape": "small-head", "body": "#d4b896", "belly": "#e9d8c0", "head": "#cdb497", "wing": "#b89b7a",
             "tail_color": "#a8896a", "spots": "#1f2937", "eye_ring": "#93c5fd", "beak": "#1f2937", "beak_type": "small",
             "legs": "#f472b6", "tail": "long"},
     "call": {"vol": .9, "notes": [[520, 640, .3, .05], [640, 560, .45, .25], [480, 470, .4, .12], [470, 460, .4, .12], [460, 450, .4, 0]]}},
    {"id": "chickadee", "name": "Carolina Chickadee", "emoji": "🖤", "inat": "Poecile carolinensis", "habitat": "backyard",
     "marks": ["Black cap and black bib", "Bright white cheeks"],
     "art": {"body": "#9ca3af", "belly": "#f5f5f4", "flanks": "#e7d7c1", "head": "#f8fafc", "cap": "#111827", "bib": "#111827",
             "wing": "#6b7280", "tail_color": "#6b7280", "beak": "#111827", "beak_type": "small", "tail": "short"},
     "call": {"notes": [[4200, 4100, .28, .08], [3300, 3250, .28, .12], [3900, 3850, .28, .08], [3000, 2950, .32, 0]]}},
    {"id": "bluebird", "name": "Eastern Bluebird", "emoji": "🔵", "inat": "Sialia sialis", "habitat": "open",
     "marks": ["Royal blue back & wings", "Warm rusty-orange chest"],
     "art": {"body": "#2563eb", "belly": "#ea580c", "vent": "#f8fafc", "head": "#2563eb", "wing": "#1d4ed8",
             "tail_color": "#1d4ed8", "beak": "#1f2937", "beak_type": "thin", "tail": "short"},
     "call": {"wave": "triangle", "vib": 18, "vibDepth": 150, "notes": [[2200, 2600, .2, .05], [2600, 2300, .25, .05], [2400, 2800, .2, 0]]}},
    {"id": "roadrunner", "name": "Greater Roadrunner", "emoji": "💨", "inat": "Geococcyx californianus", "habitat": "open",
     "marks": ["Streaky brown feathers & shaggy crest", "Long tail — runs up to 20 mph!"],
     "art": {"shape": "roadrunner", "body": "#a16207", "belly": "#fef3c7", "head": "#854d0e", "crest": "#422006",
             "wing": "#713f12", "spots": "#fef3c7", "streaks": "#422006", "eye_patch": True, "tail_color": "#422006",
             "beak": "#1f2937", "beak_type": "long", "legs": "#64748b", "leg_len": 16, "tail": "up"},
     "call": {"notes": [[700, 640, .3, .12], [660, 600, .3, .12], [620, 560, .3, .12], [580, 520, .3, .12], [540, 480, .35, 0]]}},
    {"id": "hawk", "name": "Red-tailed Hawk", "emoji": "🦅", "inat": "Buteo jamaicensis", "habitat": "open",
     "marks": ["Big broad wings & sharp gaze", "Rusty-orange tail"],
     "art": {"body": "#92400e", "belly": "#fefce8", "streaks": "#78350f", "head": "#78350f", "wing": "#7c2d12",
             "tail_color": "#ea580c", "beak": "#374151", "beak_type": "hook", "brow": True, "legs": "#facc15", "tail": "fan"},
     "call": {"wave": "sawtooth", "vol": .3, "vib": 30, "vibDepth": 120, "buzz": 2500, "notes": [[3200, 1500, 1.1, 0]]}},
    {"id": "woodpecker", "name": "Red-bellied Woodpecker", "emoji": "🪵", "inat": "Melanerpes carolinus", "habitat": "backyard",
     "marks": ["Bright red cap from beak to neck", "Zebra-striped black & white back"],
     "art": {"body": "#e7e5e4", "belly": "#fde2e4", "head": "#e7e5e4", "cap": "#ef4444", "cap_h": .7, "wing": "#111827",
             "zebra": "#ffffff", "tail_color": "#1f2937", "beak": "#1f2937", "beak_type": "chisel", "tail": "stiff"},
     "call": {"noise": True, "q": 3, "notes": [[1500, 0, .02, .04]] * 18}},
    {"id": "heron", "name": "Great Blue Heron", "emoji": "🐟", "inat": "Ardea herodias", "habitat": "water",
     "marks": ["Tall blue-gray body & S-shaped neck", "Long dagger-like yellow beak"],
     "art": {"shape": "heron", "body": "#7c8ea8", "neck": "#a8b5c7", "head": "#f8fafc", "wing": "#64748b",
             "plume": "#111827", "beak": "#facc15", "legs": "#78716c"},
     "call": {"wave": "sawtooth", "vol": .35, "buzz": 400, "notes": [[320, 180, .5, .15], [300, 170, .35, 0]]}},
    {"id": "grackle", "name": "Great-tailed Grackle", "emoji": "🖤", "inat": "Quiscalus mexicanus", "habitat": "backyard",
     "marks": ["Shiny purple-black feathers", "Bright yellow eyes & a huge tail"],
     "art": {"body": "#1e1b4b", "belly": "#312e81", "head": "#1e1b4b", "wing": "#0f172a", "tail_color": "#0f172a",
             "shimmer": "#7c3aed", "iris": "#facc15", "beak": "#0f172a", "beak_type": "thin", "tail": "keel"},
     "call": {"wave": "square", "vol": .2, "notes": [[900, 5000, .25, .05], [5000, 5200, .04, .04], [5000, 5200, .04, .04], [1200, 600, .15, .1], [700, 4500, .3, 0]]}},
    {"id": "robin", "name": "American Robin", "emoji": "🧡", "inat": "Turdus migratorius", "habitat": "backyard",
     "marks": ["Brick-orange chest", "Dark head with white eye arcs"],
     "art": {"body": "#4b5563", "belly": "#ea580c", "vent": "#f8fafc", "head": "#1f2937", "wing": "#374151",
             "tail_color": "#1f2937", "eye_ring": "#ffffff", "beak": "#facc15", "beak_type": "thin", "tail": "short"},
     "call": {"notes": [[2200, 2800, .15, .06], [2800, 2300, .15, .06], [2400, 3000, .15, .14], [2600, 2100, .18, .06], [2300, 2900, .15, 0]]}},
    {"id": "titmouse", "name": "Tufted Titmouse", "emoji": "🩶", "inat": "Baeolophus bicolor", "habitat": "backyard",
     "marks": ["Gray crest & big button eyes", "Peachy-orange sides"],
     "art": {"body": "#9ca3af", "belly": "#f5f5f4", "flanks": "#fb923c", "head": "#9ca3af", "crest": "#9ca3af",
             "forehead": "#111827", "eye_scale": 1.15, "wing": "#6b7280", "tail_color": "#6b7280", "beak": "#1f2937",
             "beak_type": "small", "tail": "short"},
     "call": {"repeat": 4, "rest": .02, "notes": [[3000, 2200, .14, .04], [2200, 2150, .1, .1]]}},
    {"id": "hummingbird", "name": "Ruby-throated Hummingbird", "emoji": "💎", "inat": "Archilochus colubris", "habitat": "backyard",
     "marks": ["Shiny emerald-green back", "Glowing ruby-red throat"],
     "art": {"shape": "hummingbird", "body": "#10b981", "belly": "#f8fafc", "head": "#059669", "throat": "#e11d48",
             "wing": "#a7f3d0", "tail_color": "#065f46", "beak": "#1f2937", "beak_type": "needle", "tail": "tiny", "leg_len": 6},
     "call": {"buzz": 180, "notes": [[6500, 7200, .03, .05]] * 8}},
    {"id": "owl", "name": "Barred Owl", "emoji": "🦉", "inat": "Strix varia", "habitat": "night",
     "marks": ["Round face with no ear tufts", "Big dark eyes & striped belly"],
     "art": {"shape": "owl", "body": "#8b5e34", "belly": "#f5e6c8", "face": "#e7dccb", "streaks": "#6b4423",
             "wing": "#6b4423", "iris": "#2b1a0e", "beak": "#facc15"},
     "call": {"vib": 6, "vibDepth": 8, "vol": 1, "notes": [[380, 420, .22, .08], [420, 400, .22, .08], [400, 380, .22, .3],
                                                          [380, 420, .22, .08], [420, 400, .22, .08], [400, 380, .22, .08], [380, 320, .6, 0]]}},
    # ---- 16 more North Texas birds ----
    {"id": "bunting", "name": "Painted Bunting", "emoji": "🌈", "inat": "Passerina ciris", "habitat": "open",
     "marks": ["Rainbow colors: blue head, red belly", "Lime-green back"],
     "art": {"body": "#65a30d", "belly": "#ef4444", "head": "#2563eb", "eye_ring": "#ef4444", "wing": "#4d7c0f",
             "tail_color": "#9f1239", "beak": "#94a3b8", "beak_type": "cone", "tail": "short"},
     "call": {"notes": [[3200, 3600, .08, .02], [3600, 3000, .08, .02], [3400, 4000, .1, .02], [3800, 3200, .1, .02], [3000, 3500, .12, 0]]}},
    {"id": "goldfinch", "name": "American Goldfinch", "emoji": "💛", "inat": "Spinus tristis", "habitat": "backyard",
     "marks": ["Lemon-yellow body (dull in winter)", "Black wings with white bars"],
     "art": {"body": "#facc15", "belly": "#fde047", "head": "#facc15", "cap": "#111827", "cap_h": .45, "wing": "#111827",
             "wing_bars": "#ffffff", "tail_color": "#111827", "beak": "#fb923c", "beak_type": "cone", "tail": "fork"},
     "call": {"repeat": 2, "notes": [[3000, 4000, .07, .05], [3200, 2800, .07, .05], [3000, 3600, .07, .05], [4200, 3000, .1, 0]]}},
    {"id": "housefinch", "name": "House Finch", "emoji": "🍓", "inat": "Haemorhous mexicanus", "habitat": "backyard",
     "marks": ["Strawberry-red head & chest (males)", "Brown streaky belly"],
     "art": {"body": "#a8a29e", "belly": "#fca5a5", "streaks": "#78716c", "head": "#dc2626", "wing": "#78716c",
             "tail_color": "#78716c", "beak": "#9ca3af", "beak_type": "cone", "tail": "fork"},
     "call": {"wave": "triangle", "notes": [[2600, 3400, .07, .02], [3400, 2800, .07, .02], [3000, 3800, .07, .02], [3600, 2600, .08, .02],
                                            [2800, 3600, .07, .02], [3300, 2500, .08, .02], [3000, 3900, .07, .02], [3800, 2200, .2, 0]]}},
    {"id": "wren", "name": "Carolina Wren", "emoji": "🎺", "inat": "Thryothorus ludovicianus", "habitat": "backyard",
     "marks": ["Rusty-brown with a white eyebrow", "Tail cocked up — and a LOUD song"],
     "art": {"body": "#b45309", "belly": "#fde68a", "head": "#b45309", "brow_color": "#ffffff", "wing": "#92400e",
             "wing_bars": "#451a03", "tail_color": "#92400e", "beak": "#44403c", "beak_type": "thin", "tail": "up"},
     "call": {"repeat": 4, "rest": .02, "vol": 1, "notes": [[3200, 2400, .1, .02], [2600, 3400, .1, .06]]}},
    {"id": "waxwing", "name": "Cedar Waxwing", "emoji": "🍒", "inat": "Bombycilla cedrorum", "habitat": "backyard",
     "marks": ["Silky tan crest & black mask", "Yellow belly and yellow tail tip"],
     "art": {"body": "#c8a27a", "belly": "#fde68a", "head": "#c8a27a", "crest": "#c8a27a", "mask": "#111827",
             "wing": "#78716c", "tail_color": "#57534e", "beak": "#111827", "beak_type": "small", "tail": "short"},
     "call": {"vib": 60, "vibDepth": 200, "notes": [[7500, 7800, .35, .15]] * 3}},
    {"id": "crow", "name": "American Crow", "emoji": "🐦‍⬛", "inat": "Corvus brachyrhynchos", "habitat": "open",
     "marks": ["All-black from beak to toes", "Super smart — can solve puzzles!"],
     "art": {"body": "#1f2937", "belly": "#273449", "head": "#1f2937", "wing": "#111827", "tail_color": "#111827",
             "beak": "#0f172a", "beak_type": "cone", "legs": "#111827", "tail": "fan"},
     "call": {"wave": "sawtooth", "vol": .4, "buzz": 800, "notes": [[700, 600, .3, .15]] * 3}},
    {"id": "blackbird", "name": "Red-winged Blackbird", "emoji": "🚩", "inat": "Agelaius phoeniceus", "habitat": "water",
     "marks": ["Glossy black body", "Red & yellow shoulder patches"],
     "art": {"body": "#111827", "belly": "#1f2937", "head": "#111827", "wing": "#0b0f19", "shoulder": "#ef4444",
             "tail_color": "#0b0f19", "beak": "#111827", "beak_type": "thin", "tail": "short"},
     "call": {"vib": 30, "vibDepth": 400, "notes": [[1700, 2400, .15, .04], [3000, 3500, .6, 0]]}},
    {"id": "phoebe", "name": "Eastern Phoebe", "emoji": "🪺", "inat": "Sayornis phoebe", "habitat": "open",
     "marks": ["Dark gray-brown head", "Pale belly & a tail that wags"],
     "art": {"body": "#78716c", "belly": "#f5f5dc", "head": "#44403c", "wing": "#57534e", "tail_color": "#44403c",
             "beak": "#111827", "beak_type": "thin", "tail": "long"},
     "call": {"wave": "square", "vol": .2, "repeat": 2, "rest": .4, "notes": [[3500, 3300, .15, .06], [3800, 3000, .2, 0]]}},
    {"id": "killdeer", "name": "Killdeer", "emoji": "🎭", "inat": "Charadrius vociferus", "habitat": "open",
     "marks": ["Two black bands across the chest", "Fakes a broken wing to protect its nest!"],
     "art": {"shape": "small-head", "body": "#a47551", "belly": "#ffffff", "head": "#a47551", "cheek": "#ffffff",
             "bands": "#111827", "eye_ring": "#f97316", "wing": "#8b5e3c", "tail_color": "#ea580c", "beak": "#111827",
             "beak_type": "small", "legs": "#d6d3d1", "leg_len": 20, "tail": "short"},
     "call": {"repeat": 3, "notes": [[3200, 4200, .12, .04], [4200, 3000, .2, .15]]}},
    {"id": "mallard", "name": "Mallard", "emoji": "🦆", "inat": "Anas platyrhynchos", "habitat": "water",
     "marks": ["Shiny green head & white collar (males)", "Blue-purple patch on the wing"],
     "art": {"shape": "duck", "body": "#d6d3d1", "belly": "#a8a29e", "breast": "#7c2d12", "head": "#15803d", "collar": "#ffffff",
             "wing": "#a8a29e", "wing_patch": "#4f46e5", "tail_color": "#1f2937", "beak": "#facc15", "beak_type": "bill", "tail": "short"},
     "call": {"wave": "sawtooth", "vol": .4, "buzz": 900, "notes": [[520, 420, .2, .08], [500, 400, .18, .08], [470, 380, .16, .08], [440, 360, .14, 0]]}},
    {"id": "egret", "name": "Great Egret", "emoji": "🤍", "inat": "Ardea alba", "habitat": "water",
     "marks": ["Snow-white feathers", "Yellow beak & long black legs"],
     "art": {"shape": "heron", "body": "#ffffff", "neck": "#ffffff", "head": "#ffffff", "wing": "#f1f5f9",
             "beak": "#facc15", "legs": "#111827"},
     "call": {"wave": "sawtooth", "vol": .35, "buzz": 300, "notes": [[260, 170, .45, 0]]}},
    {"id": "kingfisher", "name": "Belted Kingfisher", "emoji": "🎣", "inat": "Megaceryle alcyon", "habitat": "water",
     "marks": ["Big shaggy blue-gray head", "Dives head-first to catch fish"],
     "art": {"shape": "big-head", "body": "#5b7fa6", "belly": "#ffffff", "head": "#5b7fa6", "crest": "#5b7fa6", "crest2": True,
             "necklace": "#5b7fa6", "cheek": "#ffffff", "wing": "#4a6a8f", "wing_spots": "#ffffff", "tail_color": "#4a6a8f",
             "beak": "#1f2937", "beak_type": "long", "tail": "short", "leg_len": 8},
     "call": {"noise": True, "q": 6, "notes": [[3000, 0, .025, .03]] * 20}},
    {"id": "vulture", "name": "Turkey Vulture", "emoji": "🧹", "inat": "Cathartes aura", "habitat": "open",
     "marks": ["Bald red head", "Soars in wobbly circles — nature's cleanup crew"],
     "art": {"shape": "small-head", "body": "#2b2118", "belly": "#3b2f25", "head": "#dc2626", "wing": "#1c140e",
             "wing_edge": "#a8a29e", "tail_color": "#1c140e", "beak": "#fef3c7", "beak_type": "hook", "legs": "#e7e5e4", "tail": "fan"},
     "call": {"noise": True, "q": .7, "vol": .7, "notes": [[1500, 0, .9, .2], [1200, 0, .6, 0]]}},
    {"id": "screechowl", "name": "Eastern Screech-Owl", "emoji": "🌙", "inat": "Megascops asio", "habitat": "night",
     "marks": ["Tiny owl with pointy ear tufts", "Bright yellow eyes"],
     "art": {"shape": "owl", "tufts": True, "body": "#8a8f98", "belly": "#e5e7eb", "face": "#cbd0d8", "streaks": "#4b5563",
             "wing": "#6b7280", "iris": "#facc15", "beak": "#a3a3a3"},
     "call": {"vib": 25, "vibDepth": 60, "notes": [[1100, 600, 1.3, .3], [650, 640, 1.0, 0]]}},
    {"id": "martin", "name": "Purple Martin", "emoji": "💜", "inat": "Progne subis", "habitat": "open",
     "marks": ["Glossy dark purple-blue", "Lives in bird 'apartment' houses!"],
     "art": {"body": "#312e81", "belly": "#3730a3", "head": "#312e81", "shimmer": "#818cf8", "wing": "#1e1b4b",
             "tail_color": "#1e1b4b", "beak": "#111827", "beak_type": "small", "tail": "fork"},
     "call": {"wave": "triangle", "repeat": 2, "notes": [[2200, 2800, .06, .03], [2600, 1900, .06, .03], [2400, 3000, .08, .03], [2800, 2200, .06, .03]]}},
    {"id": "warbler", "name": "Yellow-rumped Warbler", "emoji": "🍋", "inat": "Setophaga coronata", "habitat": "backyard",
     "marks": ["Yellow patches on rump, sides & throat", "Common winter visitor"],
     "art": {"body": "#94a3b8", "belly": "#f8fafc", "flanks": "#facc15", "streaks": "#334155", "head": "#94a3b8",
             "throat": "#fde047", "wing": "#475569", "wing_bars": "#ffffff", "tail_color": "#334155", "beak": "#111827",
             "beak_type": "thin", "tail": "short"},
     "call": {"notes": [[4500, 3800, .04, .12]] * 3 + [[3500, 4500, .05, .01]] * 6}},
    # ---- 23 more (55 total). Only 2 non-native birds, because you see them everywhere: starling + house sparrow ----
    {"id": "starling", "name": "European Starling", "emoji": "✨", "inat": "Sturnus vulgaris", "habitat": "backyard",
     "marks": ["Shiny black with white star-like speckles", "Pointy yellow beak (in spring) — not native, but everywhere!"],
     "art": {"body": "#1f2937", "belly": "#273449", "streaks": "#f8fafc", "shimmer": "#a78bfa", "head": "#1f2937",
             "wing": "#111827", "wing_spots": "#e2e8f0", "tail_color": "#111827", "beak": "#facc15", "beak_type": "long", "tail": "short"},
     "call": {"wave": "square", "vol": .15, "notes": [[3000, 5000, .05, .03], [5000, 2500, .05, .03], [1500, 4000, .2, .05], [4000, 3800, .04, .02], [4000, 3800, .04, .1]]}},
    {"id": "housesparrow", "name": "House Sparrow", "emoji": "🏠", "inat": "Passer domesticus", "habitat": "backyard",
     "marks": ["Gray cap, chestnut sides & black bib (males)", "Not native, but lives near people everywhere"],
     "art": {"body": "#a8a29e", "belly": "#e7e5e4", "head": "#92400e", "cap": "#6b7280", "cap_h": .5, "cheek": "#e7e5e4", "bib": "#111827",
             "wing": "#92400e", "wing_bars": "#451a03", "tail_color": "#78716c", "beak": "#111827", "beak_type": "cone", "tail": "short"},
     "call": {"vol": .7, "notes": [[3000, 3600, .08, .15]] * 4}},
    {"id": "wwdove", "name": "White-winged Dove", "emoji": "🤍", "inat": "Zenaida asiatica", "habitat": "backyard",
     "marks": ["White stripe along the wing", "Red eye with a bright blue eye ring"],
     "art": {"shape": "small-head", "body": "#c8b8a6", "belly": "#e7dccf", "head": "#c8b8a6", "wing": "#a8977f", "wing_edge": "#ffffff",
             "eye_ring": "#60a5fa", "iris": "#ef4444", "tail_color": "#8b7b68", "beak": "#1f2937", "beak_type": "small", "legs": "#f472b6", "tail": "short"},
     "call": {"vol": .9, "notes": [[520, 600, .25, .08], [600, 560, .25, .08], [560, 520, .25, .08], [520, 480, .45, 0]]}},
    {"id": "downy", "name": "Downy Woodpecker", "emoji": "🥁", "inat": "Dryobates pubescens", "habitat": "backyard",
     "marks": ["Smallest woodpecker — white back & spotted wings", "Tiny red patch on the back of the head (males)"],
     "art": {"body": "#f8fafc", "belly": "#ffffff", "head": "#f8fafc", "cap": "#111827", "cap_h": .45, "nape": "#ef4444", "wing": "#111827",
             "wing_spots": "#ffffff", "tail_color": "#111827", "beak": "#1f2937", "beak_type": "chisel", "tail": "stiff"},
     "call": {"notes": [[3800, 3600, .03, .25], [3800, 3600, .03, .3]] + [[2600, 1800, .04, .02]] * 8}},
    {"id": "flicker", "name": "Northern Flicker", "emoji": "🎯", "inat": "Colaptes auratus", "habitat": "backyard",
     "marks": ["Brown with black bars & a polka-dot belly", "Black bib — a woodpecker that eats ants on the ground!"],
     "art": {"body": "#c8a27a", "belly": "#fdf6e3", "streaks": "#1f2937", "head": "#a8a29e", "nape": "#ef4444", "bib": "#111827",
             "wing": "#a47551", "zebra": "#3f2a14", "tail_color": "#1f2937", "beak": "#1f2937", "beak_type": "chisel", "tail": "stiff"},
     "call": {"wave": "triangle", "vol": .6, "notes": [[2200, 2600, .08, .04]] * 10}},
    {"id": "greathornedowl", "name": "Great Horned Owl", "emoji": "😼", "inat": "Bubo virginianus", "habitat": "night",
     "marks": ["Big feather 'horns' (tufts) on its head", "Yellow eyes & a deep hoo-h'HOO-hoo-hoo"],
     "art": {"shape": "owl", "tufts": True, "body": "#8b5e34", "belly": "#e9d5b5", "face": "#d6a76c", "streaks": "#5b3a1e",
             "wing": "#6b4423", "iris": "#facc15", "beak": "#44403c"},
     "call": {"notes": [[330, 320, .35, .12], [330, 320, .15, .05], [340, 330, .15, .12], [320, 300, .4, .2], [310, 290, .4, 0]]}},
    {"id": "coopershawk", "name": "Cooper's Hawk", "emoji": "⚡", "inat": "Astur cooperii", "habitat": "backyard",
     "marks": ["Blue-gray back & orange-barred chest", "Red eyes — zips through yards chasing birds"],
     "art": {"body": "#64748b", "belly": "#fed7aa", "streaks": "#ea580c", "head": "#64748b", "cap": "#334155", "cap_h": .5, "iris": "#dc2626",
             "wing": "#475569", "tail_color": "#475569", "beak": "#374151", "beak_type": "hook", "brow": True, "legs": "#facc15", "tail": "long"},
     "call": {"wave": "sawtooth", "vol": .3, "buzz": 1800, "notes": [[1600, 1400, .08, .06]] * 8}},
    {"id": "redshouldered", "name": "Red-shouldered Hawk", "emoji": "🧡", "inat": "Buteo lineatus", "habitat": "open",
     "marks": ["Orange-barred chest", "Checkered black & white wings"],
     "art": {"body": "#78350f", "belly": "#fb923c", "streaks": "#fff7ed", "head": "#92400e", "wing": "#3f2a14", "wing_spots": "#ffffff",
             "tail_color": "#1f2937", "beak": "#374151", "beak_type": "hook", "brow": True, "legs": "#facc15", "tail": "fan"},
     "call": {"wave": "sawtooth", "vol": .3, "vib": 20, "vibDepth": 80, "notes": [[2600, 1800, .35, .15]] * 4}},
    {"id": "kestrel", "name": "American Kestrel", "emoji": "🪁", "inat": "Falco sparverius", "habitat": "open",
     "marks": ["Smallest falcon: rusty back, blue-gray wings", "Two black 'mustache' stripes on its face"],
     "art": {"body": "#ea580c", "belly": "#fde7c8", "streaks": "#1f2937", "head": "#cbd5e1", "cap": "#ea580c", "cap_h": .35, "face_stripes": "#111827",
             "wing": "#64748b", "wing_spots": "#111827", "tail_color": "#ea580c", "beak": "#374151", "beak_type": "hook", "legs": "#facc15", "tail": "long"},
     "call": {"wave": "triangle", "notes": [[4200, 4000, .07, .04]] * 8}},
    {"id": "snowyegret", "name": "Snowy Egret", "emoji": "👟", "inat": "Egretta thula", "habitat": "water",
     "marks": ["White with a thin black beak", "Black legs with bright yellow 'slippers'"],
     "art": {"shape": "heron", "body": "#ffffff", "neck": "#ffffff", "head": "#ffffff", "wing": "#f1f5f9", "beak": "#111827", "legs": "#111827"},
     "call": {"wave": "sawtooth", "vol": .35, "buzz": 350, "notes": [[300, 200, .35, .1], [280, 190, .3, 0]]}},
    {"id": "greenheron", "name": "Green Heron", "emoji": "🎣", "inat": "Butorides virescens", "habitat": "water",
     "marks": ["Short, hunched heron with a chestnut neck", "Dark green back — uses bait to catch fish!"],
     "art": {"shape": "heron", "body": "#3f5a4a", "neck": "#9a3412", "head": "#14532d", "wing": "#365314", "beak": "#1f2937", "legs": "#f59e0b"},
     "call": {"wave": "sawtooth", "vol": .35, "buzz": 1200, "notes": [[1800, 700, .3, 0]]}},
    {"id": "woodduck", "name": "Wood Duck", "emoji": "🎨", "inat": "Aix sponsa", "habitat": "water",
     "marks": ["Rainbow-colored head with a swept-back crest (males)", "Nests in tree holes!"],
     "art": {"shape": "duck", "body": "#d6c3a5", "belly": "#a8a29e", "breast": "#7c2d12", "head": "#065f46", "crest": "#065f46", "throat": "#ffffff",
             "iris": "#dc2626", "wing": "#1e3a8a", "wing_patch": "#ffffff", "tail_color": "#1f2937", "beak": "#ef4444", "beak_type": "bill", "tail": "short"},
     "call": {"vib": 12, "vibDepth": 150, "notes": [[1200, 2600, .35, .2]] * 2}},
    {"id": "shoveler", "name": "Northern Shoveler", "emoji": "🥄", "inat": "Spatula clypeata", "habitat": "water",
     "marks": ["Huge spoon-shaped bill", "Green head, white chest & rusty sides (males)"],
     "art": {"shape": "duck", "body": "#f8fafc", "belly": "#ffffff", "flanks": "#c2410c", "head": "#166534", "iris": "#facc15",
             "wing": "#94a3b8", "wing_patch": "#16a34a", "tail_color": "#1f2937", "beak": "#1f2937", "beak_type": "bill", "tail": "short"},
     "call": {"vol": .9, "notes": [[400, 350, .1, .12]] * 5}},
    {"id": "goose", "name": "Canada Goose", "emoji": "🪿", "inat": "Branta canadensis", "habitat": "water",
     "marks": ["Black head & neck with a white chinstrap", "Flies in a V and honks"],
     "art": {"shape": "duck", "body": "#a8a29e", "belly": "#e7e5e4", "breast": "#d6d3d1", "head": "#111827", "cheek": "#ffffff",
             "wing": "#78716c", "tail_color": "#111827", "beak": "#111827", "beak_type": "bill", "tail": "short"},
     "call": {"wave": "sawtooth", "vol": .4, "buzz": 600, "notes": [[420, 380, .25, .15]] * 3}},
    {"id": "coot", "name": "American Coot", "emoji": "🎱", "inat": "Fulica americana", "habitat": "water",
     "marks": ["Sooty black with a white chicken-like bill", "Lobed toes instead of webbed feet"],
     "art": {"shape": "duck", "body": "#334155", "belly": "#1f2937", "head": "#111827", "forehead": "#f8fafc", "iris": "#dc2626",
             "wing": "#1f2937", "tail_color": "#111827", "beak": "#f8fafc", "beak_type": "small", "tail": "short"},
     "call": {"wave": "square", "vol": .25, "notes": [[300, 250, .08, .1], [600, 500, .06, .1], [300, 250, .08, .1], [700, 450, .15, 0]]}},
    {"id": "cormorant", "name": "Double-crested Cormorant", "emoji": "🌊", "inat": "Nannopterum auritum", "habitat": "water",
     "marks": ["Long black diving bird with an orange face", "Stands with wings spread to dry them"],
     "art": {"shape": "heron", "body": "#1f2937", "neck": "#273449", "head": "#1f2937", "wing": "#111827", "beak": "#f59e0b", "legs": "#111827"},
     "call": {"wave": "sawtooth", "vol": .35, "buzz": 250, "notes": [[180, 140, .3, .2]] * 2}},
    {"id": "gull", "name": "Ring-billed Gull", "emoji": "🍟", "inat": "Larus delawarensis", "habitat": "water",
     "marks": ["White with pale gray wings & black wingtips", "Black ring around a yellow bill"],
     "art": {"body": "#ffffff", "belly": "#ffffff", "head": "#ffffff", "wing": "#cbd5e1", "wing_tips": "#111827", "iris": "#fde047",
             "tail_color": "#ffffff", "beak": "#facc15", "beak_type": "long", "legs": "#facc15", "tail": "short"},
     "call": {"wave": "sawtooth", "vol": .3, "vib": 8, "vibDepth": 60, "notes": [[1800, 1200, .2, .08]] * 4}},
    {"id": "swallow", "name": "Barn Swallow", "emoji": "🪃", "inat": "Hirundo rustica", "habitat": "open",
     "marks": ["Shiny blue back & rusty throat", "Long forked tail — builds mud nests under bridges"],
     "art": {"body": "#1e3a8a", "belly": "#fdba74", "head": "#1e3a8a", "throat": "#c2410c", "forehead": "#c2410c", "wing": "#172554",
             "tail_color": "#172554", "beak": "#111827", "beak_type": "small", "tail": "scissor"},
     "call": {"notes": [[3200, 4200, .05, .02], [4200, 3400, .05, .02]] * 6}},
    {"id": "meadowlark", "name": "Eastern Meadowlark", "emoji": "🌾", "inat": "Sturnella magna", "habitat": "open",
     "marks": ["Bright yellow chest with a black V", "Sings a sweet flute-like song from fence posts"],
     "art": {"body": "#a16207", "belly": "#facc15", "streaks": "#713f12", "head": "#a16207", "throat": "#facc15", "necklace": "#111827",
             "wing": "#854d0e", "wing_bars": "#422006", "tail_color": "#854d0e", "beak": "#94a3b8", "beak_type": "long", "legs": "#fda4af", "tail": "short"},
     "call": {"notes": [[2400, 3200, .25, .05], [2800, 2600, .2, .05], [3600, 2400, .35, .05], [2000, 2600, .25, 0]]}},
    {"id": "thrasher", "name": "Brown Thrasher", "emoji": "🍂", "inat": "Toxostoma rufum", "habitat": "backyard",
     "marks": ["Rusty-red with a streaky chest", "Yellow eyes — knows over 1,000 songs!"],
     "art": {"body": "#b45309", "belly": "#fef3c7", "streaks": "#78350f", "head": "#b45309", "iris": "#facc15", "wing": "#9a3412",
             "wing_bars": "#fef3c7", "tail_color": "#9a3412", "beak": "#44403c", "beak_type": "long", "tail": "long"},
     "call": {"notes": [[2200, 2800, .12, .05], [2200, 2800, .12, .15], [3000, 2000, .12, .05], [3000, 2000, .12, .15], [2600, 3400, .1, .05], [2600, 3400, .1, 0]]}},
    {"id": "junco", "name": "Dark-eyed Junco", "emoji": "❄️", "inat": "Junco hyemalis", "habitat": "backyard",
     "marks": ["Slate-gray with a snow-white belly", "Pink beak — a winter visitor"],
     "art": {"body": "#475569", "belly": "#ffffff", "head": "#475569", "wing": "#334155", "tail_color": "#334155",
             "beak": "#f9a8d4", "beak_type": "cone", "legs": "#fda4af", "tail": "short"},
     "call": {"notes": [[4000, 4100, .04, .015]] * 16}},
    {"id": "kingbird", "name": "Western Kingbird", "emoji": "👑", "inat": "Tyrannus verticalis", "habitat": "open",
     "marks": ["Pale gray head & lemon-yellow belly", "Black tail with white edges — sits on power lines"],
     "art": {"body": "#d1d5db", "belly": "#fde047", "head": "#d1d5db", "throat": "#f1f5f9", "wing": "#57534e",
             "tail_color": "#111827", "beak": "#111827", "beak_type": "thin", "tail": "short"},
     "call": {"wave": "square", "vol": .2, "notes": [[3000, 3600, .05, .02]] * 6 + [[3600, 2600, .2, 0]]}},
    {"id": "indigobunting", "name": "Indigo Bunting", "emoji": "💎", "inat": "Passerina cyanea", "habitat": "open",
     "marks": ["All bright blue (males)", "Sings in pairs: sweet-sweet, where-where!"],
     "art": {"body": "#2563eb", "belly": "#3b82f6", "head": "#1d4ed8", "wing": "#1e40af", "tail_color": "#1e3a8a",
             "beak": "#94a3b8", "beak_type": "cone", "tail": "short"},
     "call": {"notes": [[5000, 4600, .12, .04], [5000, 4600, .12, .08], [4200, 4400, .12, .04], [4200, 4400, .12, .08], [3800, 4600, .15, 0]]}},
    # ---- 18 more (73 total): a cowbird, sparrows, prairie birds and shorebirds ----
    {"id": "cowbird", "name": "Brown-headed Cowbird", "emoji": "🐄", "inat": "Molothrus ater", "habitat": "open",
     "marks": ["Glossy black body with a brown head (males)", "Follows cows to catch the bugs they stir up"],
     "art": {"body": "#111827", "belly": "#1f2937", "shimmer": "#4338ca", "head": "#5b3a29", "wing": "#0b0f19",
             "tail_color": "#0b0f19", "beak": "#111827", "beak_type": "cone", "tail": "short"},
     "call": {"notes": [[600, 900, .15, .05], [2500, 9000, .3, 0]]}},
    {"id": "chippingsparrow", "name": "Chipping Sparrow", "emoji": "🧢", "inat": "Spizella passerina", "habitat": "backyard",
     "marks": ["Bright rusty cap", "White eyebrow with a black line through the eye"],
     "art": {"body": "#a8a29e", "belly": "#e5e7eb", "head": "#d1d5db", "cap": "#c2410c", "cap_h": .45, "brow_color": "#ffffff",
             "eye_line": "#111827", "wing": "#92400e", "wing_bars": "#f5f5f4", "tail_color": "#78716c", "beak": "#1f2937",
             "beak_type": "cone", "legs": "#fda4af", "tail": "fork"},
     "call": {"notes": [[5000, 5200, .03, .02]] * 18}},
    {"id": "whitecrowned", "name": "White-crowned Sparrow", "emoji": "👑", "inat": "Zonotrichia leucophrys", "habitat": "backyard",
     "marks": ["Bold black-and-white striped crown", "Orange-pink beak — a winter visitor"],
     "art": {"body": "#9ca3af", "belly": "#e5e7eb", "head": "#d1d5db", "cap": "#111827", "cap_h": .55, "crown_stripe": "#ffffff",
             "brow_color": "#ffffff", "eye_line": "#111827", "wing": "#92400e", "wing_bars": "#ffffff", "tail_color": "#78716c",
             "beak": "#fb923c", "beak_type": "cone", "legs": "#fda4af", "tail": "long"},
     "call": {"notes": [[3800, 3800, .5, .05], [3300, 3500, .2, .05], [4200, 3800, .15, .03]] + [[3000, 3400, .06, .02]] * 4}},
    {"id": "harrissparrow", "name": "Harris's Sparrow", "emoji": "🎭", "inat": "Zonotrichia querula", "habitat": "backyard",
     "marks": ["Black face and bib with a pink beak", "Biggest sparrow — spends winter in Texas"],
     "art": {"body": "#a8a29e", "belly": "#f5f5f4", "flanks": "#d6b48c", "streaks": "#57534e", "head": "#9ca3af", "cap": "#111827",
             "cap_h": .5, "bib": "#111827", "wing": "#92400e", "wing_bars": "#f5f5f4", "tail_color": "#78716c", "beak": "#f9a8d4",
             "beak_type": "cone", "legs": "#fda4af", "tail": "long"},
     "call": {"notes": [[3600, 3600, .5, .3], [3200, 3200, .5, 0]]}},
    {"id": "songsparrow", "name": "Song Sparrow", "emoji": "🎵", "inat": "Melospiza melodia", "habitat": "backyard",
     "marks": ["Streaky brown with a dark spot on the chest", "Pumps its tail when it flies"],
     "art": {"body": "#a47551", "belly": "#f5f5f4", "streaks": "#5b3a1e", "breast_spot": "#5b3a1e", "head": "#a47551",
             "eye_line": "#5b3a1e", "brow_color": "#d6d3d1", "wing": "#8b5e3c", "wing_bars": "#5b3a1e", "tail_color": "#8b5e3c",
             "beak": "#78716c", "beak_type": "cone", "legs": "#fda4af", "tail": "long"},
     "call": {"notes": [[3000, 3000, .08, .08]] * 3 + [[4500, 3500, .4, .05], [2800, 3600, .05, .02], [2800, 3600, .05, .02], [3200, 2600, .3, 0]]}},
    {"id": "whitethroated", "name": "White-throated Sparrow", "emoji": "🍋", "inat": "Zonotrichia albicollis", "habitat": "backyard",
     "marks": ["Bright white throat & yellow spot by the eye", "Sings 'Oh-sweet-Canada-Canada'"],
     "art": {"body": "#a47551", "belly": "#d1d5db", "head": "#9ca3af", "cap": "#111827", "cap_h": .55, "crown_stripe": "#ffffff",
             "brow_color": "#ffffff", "forehead": "#facc15", "throat": "#ffffff", "wing": "#92400e", "wing_bars": "#f5f5f4",
             "tail_color": "#78716c", "beak": "#78716c", "beak_type": "cone", "legs": "#fda4af", "tail": "long"},
     "call": {"notes": [[3000, 3000, .4, .05], [3900, 3900, .4, .05]] + [[3500, 3500, .2, .03]] * 6}},
    {"id": "larksparrow", "name": "Lark Sparrow", "emoji": "🤡", "inat": "Chondestes grammacus", "habitat": "open",
     "marks": ["Clown-like chestnut, black & white face", "One dark spot in the middle of its white chest"],
     "art": {"body": "#a8a29e", "belly": "#f8fafc", "breast_spot": "#111827", "head": "#f8fafc", "cheek": "#9a3412", "cap": "#9a3412",
             "cap_h": .4, "crown_stripe": "#f8fafc", "eye_line": "#111827", "wing": "#78716c", "wing_bars": "#e7e5e4",
             "tail_color": "#44403c", "beak": "#94a3b8", "beak_type": "cone", "legs": "#fda4af", "tail": "fan"},
     "call": {"wave": "triangle", "notes": [[3200, 3800, .1, .03], [3800, 3000, .1, .03], [2400, 2400, .2, .05]] + [[4200, 4000, .04, .02]] * 6}},
    {"id": "savannahsparrow", "name": "Savannah Sparrow", "emoji": "🌾", "inat": "Passerculus sandwichensis", "habitat": "open",
     "marks": ["Streaky brown with a yellow eyebrow", "Hides in grassy fields all winter"],
     "art": {"body": "#a47551", "belly": "#f5f5f4", "streaks": "#5b3a1e", "head": "#a47551", "brow_color": "#fde047",
             "wing": "#8b5e3c", "wing_bars": "#5b3a1e", "tail_color": "#8b5e3c", "beak": "#fda4af", "beak_type": "small",
             "legs": "#fda4af", "tail": "fork"},
     "call": {"notes": [[6000, 6000, .03, .05]] * 3 + [[7000, 7500, .5, .05], [4000, 3800, .2, 0]]}},
    {"id": "dickcissel", "name": "Dickcissel", "emoji": "🌻", "inat": "Spiza americana", "habitat": "open",
     "marks": ["Yellow chest with a black V (like a mini meadowlark)", "Sings its name: dick-dick-ciss-ciss-ciss!"],
     "art": {"body": "#a8a29e", "belly": "#fde047", "throat": "#ffffff", "necklace": "#111827", "head": "#9ca3af",
             "brow_color": "#fde047", "shoulder": "#b45309", "wing": "#78716c", "tail_color": "#57534e", "beak": "#94a3b8",
             "beak_type": "cone", "legs": "#fda4af", "tail": "short"},
     "call": {"wave": "square", "vol": .2, "notes": [[3000, 2600, .08, .1], [3000, 2600, .08, .15]] + [[4500, 3500, .06, .05]] * 3}},
    {"id": "shrike", "name": "Loggerhead Shrike", "emoji": "🦹", "inat": "Lanius ludovicianus", "habitat": "open",
     "marks": ["Gray with a black bandit mask", "'Butcher bird' — stores its food on thorns!"],
     "art": {"body": "#9ca3af", "belly": "#f8fafc", "head": "#9ca3af", "mask": "#111827", "eye_line": "#111827", "wing": "#111827",
             "wing_patch": "#ffffff", "tail_color": "#111827", "beak": "#111827", "beak_type": "hook", "legs": "#111827", "tail": "long"},
     "call": {"wave": "sawtooth", "vol": .3, "notes": [[2000, 1800, .12, .1]] * 4}},
    {"id": "bobwhite", "name": "Northern Bobwhite", "emoji": "🐔", "inat": "Colinus virginianus", "habitat": "open",
     "marks": ["Round little quail with a white throat & eyebrow", "Whistles its name: bob-WHITE!"],
     "art": {"shape": "small-head", "body": "#9a5b2e", "belly": "#f5e6c8", "streaks": "#5b3a1e", "head": "#7c2d12", "throat": "#ffffff",
             "brow_color": "#ffffff", "eye_line": "#111827", "wing": "#8b5e34", "spots": "#f5e6c8", "tail_color": "#7c2d12",
             "beak": "#44403c", "beak_type": "small", "legs": "#a8a29e", "tail": "short"},
     "call": {"notes": [[1300, 1500, .15, .15], [1500, 2900, .35, 0]]}},
    {"id": "uplandsandpiper", "name": "Upland Sandpiper", "emoji": "🏞️", "inat": "Bartramia longicauda", "habitat": "open",
     "marks": ["A sandpiper that lives on prairies, not beaches", "Small head with big dark eyes on a long neck"],
     "art": {"shape": "wader", "body": "#c8a27a", "belly": "#fef3c7", "streaks": "#5b3a1e", "head": "#c8a27a", "eye_scale": 1.2,
             "wing": "#a47551", "spots": "#5b3a1e", "tail_color": "#a47551", "beak": "#facc15", "beak_type": "thin",
             "legs": "#facc15", "leg_len": 22, "tail": "wader"},
     "call": {"notes": [[1500, 2500, .4, .05], [2500, 4000, .6, .05], [4000, 2000, .9, 0]]}},
    {"id": "spottedsandpiper", "name": "Spotted Sandpiper", "emoji": "🔵", "inat": "Actitis macularius", "habitat": "water",
     "marks": ["Big dark spots on a white belly (summer)", "Bobs its tail up and down all the time"],
     "art": {"shape": "wader", "body": "#78716c", "belly": "#ffffff", "streaks": "#111827", "head": "#78716c", "brow_color": "#ffffff",
             "wing": "#57534e", "tail_color": "#57534e", "beak": "#f97316", "beak_type": "thin", "legs": "#fda4af", "leg_len": 16, "tail": "wader"},
     "call": {"notes": [[3800, 3400, .1, .06]] * 5}},
    {"id": "leastsandpiper", "name": "Least Sandpiper", "emoji": "🤏", "inat": "Calidris minutilla", "habitat": "water",
     "marks": ["World's smallest sandpiper", "Yellow-green legs & a thin drooping beak"],
     "art": {"shape": "wader", "body": "#8b5e34", "belly": "#ffffff", "streaks": "#5b3a1e", "head": "#8b5e34", "brow_color": "#e7e5e4",
             "wing": "#6b4423", "wing_bars": "#d6b48c", "tail_color": "#5b3a1e", "beak": "#111827", "beak_type": "thin",
             "legs": "#a3e635", "leg_len": 14, "tail": "wader"},
     "call": {"notes": [[5000, 6000, .15, .1], [5000, 6000, .15, 0]]}},
    {"id": "yellowlegs", "name": "Greater Yellowlegs", "emoji": "🦵", "inat": "Tringa melanoleuca", "habitat": "water",
     "marks": ["Long, bright yellow legs", "Calls 'tew-tew-tew' when it flies off"],
     "art": {"shape": "wader", "body": "#6b7280", "belly": "#ffffff", "streaks": "#374151", "head": "#9ca3af", "wing": "#4b5563",
             "spots": "#f8fafc", "tail_color": "#4b5563", "beak": "#111827", "beak_type": "long", "legs": "#facc15", "leg_len": 28, "tail": "wader"},
     "call": {"notes": [[3200, 2800, .12, .06]] * 3}},
    {"id": "stilt", "name": "Black-necked Stilt", "emoji": "🩰", "inat": "Himantopus mexicanus", "habitat": "water",
     "marks": ["Sharp black-and-white tuxedo", "Super-long bright pink legs"],
     "art": {"shape": "wader", "body": "#111827", "belly": "#ffffff", "head": "#111827", "throat": "#ffffff", "iris": "#dc2626",
             "wing": "#0b0f19", "tail_color": "#e5e7eb", "beak": "#111827", "beak_type": "needle", "legs": "#f472b6", "leg_len": 30, "tail": "wader"},
     "call": {"wave": "square", "vol": .2, "notes": [[2400, 2200, .08, .1]] * 6}},
    {"id": "avocet", "name": "American Avocet", "emoji": "🥢", "inat": "Recurvirostra americana", "habitat": "water",
     "marks": ["Cinnamon head with a thin upturned beak", "Swishes its beak side to side to catch food"],
     "art": {"shape": "wader", "body": "#ffffff", "belly": "#ffffff", "head": "#e6a77a", "wing": "#111827", "wing_edge": "#ffffff",
             "tail_color": "#e5e7eb", "beak": "#111827", "beak_type": "upturned", "legs": "#93c5fd", "leg_len": 28, "tail": "wader"},
     "call": {"notes": [[2800, 3200, .1, .1]] * 5}},
    {"id": "snipe", "name": "Wilson's Snipe", "emoji": "🥷", "inat": "Gallinago delicata", "habitat": "water",
     "marks": ["Super-long straight beak", "Striped head — hides perfectly in marsh grass"],
     "art": {"shape": "small-head", "body": "#8b5e34", "belly": "#f5e6c8", "streaks": "#3f2a14", "head": "#8b5e34", "crown_stripe": "#f5e6c8",
             "brow_color": "#f5e6c8", "eye_line": "#3f2a14", "wing": "#6b4423", "wing_bars": "#f5e6c8", "tail_color": "#ea580c",
             "beak": "#57534e", "beak_type": "needle", "legs": "#a3e635", "leg_len": 10, "tail": "short"},
     "call": {"wave": "sawtooth", "vol": .3, "buzz": 3000, "notes": [[3000, 2600, .15, .4]] * 2}},
]

# ---- Cartoon art generator ----
# Every cartoon is built from the same simple shapes (egg body, round head, wing, tail, beak, big eyes)
# and the "art" recipe picks colors and extras. "__UID__" is swapped for a unique id in the browser,
# so the same bird can be drawn many times on one page without clip-paths clashing.
OUTLINE = "#1e293b"
GEOMETRY = {  # body (cx, cy, rx, ry), head (hx, hy, r)
    "songbird":    {"body": (56, 74, 30, 24), "head": (80, 46, 20)},
    "small-head":  {"body": (54, 72, 31, 22), "head": (82, 48, 16)},
    "big-head":    {"body": (54, 76, 28, 21), "head": (80, 46, 22)},
    "roadrunner":  {"body": (56, 74, 31, 19), "head": (82, 48, 17)},
    "hummingbird": {"body": (58, 74, 22, 17), "head": (76, 54, 15)},
    "duck":        {"body": (58, 78, 36, 20), "head": (86, 46, 17)},
    "wader":       {"body": (52, 62, 28, 17), "head": (78, 40, 13)},   # shorebirds: raised body for long legs
}
TAILS = {  # drawn behind the body, pointing left
    "short":   "M36,70 L10,80 L14,92 L40,86 Z",
    "long":    "M36,70 L4,88 L10,100 L40,86 Z",
    "scissor": "M36,74 Q14,92 2,116 Q18,98 40,84 Z M38,80 Q22,102 16,118 Q28,100 42,88 Z",
    "fan":     "M36,68 L6,74 L4,96 L38,90 Z",
    "keel":    "M36,68 L2,80 L6,106 L40,90 Z",
    "up":      "M32,74 L6,42 L0,52 L30,86 Z",
    "stiff":   "M36,78 L16,100 L24,104 L42,86 Z",
    "tiny":    "M40,78 L20,88 L26,96 L42,86 Z",
    "fork":    "M36,72 L6,78 L18,84 L6,92 L40,86 Z",
    "wader":   "M30,58 L8,62 L10,72 L32,68 Z",
}


def _n(x):
    return f"{x:.1f}"


def _st(step, svg):
    """Tag a piece of the drawing with its step in the Draw Birds guide:
    1 body · 2 head (+ crest/neck) · 3 tail & wings · 4 eye & beak · 5 legs · 6 colors & markings (0 = shadow)."""
    return f'<g data-step="{step}">{svg}</g>'


def _songbird_parts(a):
    S = OUTLINE
    shape = a.get("shape", "songbird")
    cx, cy, rx, ry = GEOMETRY[shape]["body"]
    hx, hy, r = GEOMETRY[shape]["head"]
    s = rx / 30
    if shape == "hummingbird":
        wing = f"M{cx-2},{cy-12} Q{cx-24},{cy-46} {cx+4},{cy-50} Q{cx+12},{cy-30} {cx+6},{cy-10} Z"
    else:
        wing = (f"M{_n(cx-18*s)},{_n(cy-10*s)} Q{_n(cx+2*s)},{_n(cy-19*s)} {_n(cx+16*s)},{_n(cy-3*s)} "
                f"Q{_n(cx+4*s)},{_n(cy+18*s)} {_n(cx-26*s)},{_n(cy+12*s)} Q{_n(cx-31*s)},{cy} {_n(cx-18*s)},{_n(cy-10*s)} Z")
    o = [f'<defs><clipPath id="b__UID__"><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/></clipPath>'
         f'<clipPath id="h__UID__"><circle cx="{hx}" cy="{hy}" r="{r}"/></clipPath>'
         f'<clipPath id="w__UID__"><path d="{wing}"/></clipPath></defs>']
    if shape == "duck":
        o.append(_st(0, '<path d="M8,98 Q30,92 60,98 T112,98" stroke="#7dd3fc" stroke-width="3" fill="none" stroke-linecap="round"/>'
                        '<ellipse cx="60" cy="100" rx="44" ry="6" fill="#bae6fd" opacity="0.6"/>'))
    else:  # shadow right under the feet (so long-legged shorebirds don't float)
        feet_y = min(112, cy + ry - 3 + a.get("leg_len", 12) + 3)
        o.append(_st(0, f'<ellipse cx="60" cy="{feet_y}" rx="30" ry="5" fill="#0f172a" opacity="0.12"/>'))
    o.append(_st(3, f'<path d="{TAILS[a.get("tail", "short")]}" fill="{a["tail_color"]}" stroke="{S}" stroke-width="2.5" stroke-linejoin="round"/>'))
    if shape != "duck":
        lc, ll = a.get("legs", "#f59e0b"), a.get("leg_len", 12)
        top = cy + ry - 3
        o.append(_st(5, "".join(f'<path d="M{lx},{top} L{lx},{top+ll} M{lx-4},{top+ll} L{lx+5},{top+ll}" stroke="{lc}" '
                                f'stroke-width="3" stroke-linecap="round" fill="none"/>' for lx in (cx - 6, cx + 6))))
    # body + belly details (clipped so nothing pokes outside the outline)
    o.append(_st(1, f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{a["body"]}"/>'))
    m = [f'<ellipse cx="{_n(cx+rx*.3)}" cy="{_n(cy+ry*.35)}" rx="{_n(rx*.75)}" ry="{_n(ry*.7)}" fill="{a["belly"]}"/>']
    if a.get("breast"):
        m.append(f'<ellipse cx="{_n(cx+rx*.85)}" cy="{_n(cy-ry*.1)}" rx="{_n(rx*.35)}" ry="{_n(ry*.6)}" fill="{a["breast"]}"/>')
    if a.get("vent"):
        m.append(f'<ellipse cx="{_n(cx+rx*.15)}" cy="{_n(cy+ry*.95)}" rx="{_n(rx*.45)}" ry="{_n(ry*.35)}" fill="{a["vent"]}"/>')
    if a.get("flanks"):
        m.append(f'<ellipse cx="{_n(cx+rx*.05)}" cy="{_n(cy+ry*.55)}" rx="{_n(rx*.45)}" ry="{_n(ry*.3)}" fill="{a["flanks"]}"/>')
    if a.get("streaks"):
        for dx, dy in ((0, 0), (8, 4), (16, 0), (4, 10), (12, 12), (20, 8)):
            m.append(f'<ellipse cx="{_n(cx+rx*.15+dx)}" cy="{_n(cy+ry*.15+dy)}" rx="1.4" ry="3" fill="{a["streaks"]}" opacity="0.8"/>')
    if a.get("breast_spot"):  # one dark spot in the middle of the chest (song & lark sparrows)
        m.append(f'<circle cx="{_n(cx+rx*.6)}" cy="{_n(cy-ry*.05)}" r="3.2" fill="{a["breast_spot"]}"/>')
    if a.get("shimmer"):
        m.append(f'<path d="M{cx-14},{cy-8} Q{cx},{cy-16} {cx+14},{cy-8}" stroke="{a["shimmer"]}" stroke-width="3" fill="none" opacity="0.7" stroke-linecap="round"/>')
    o.append(_st(6, '<g clip-path="url(#b__UID__)">' + "".join(m) + '</g>'))
    o.append(_st(1, f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{S}" stroke-width="2.5"/>'))
    # wing (its markings are step 6, nested inside step 3)
    wclass = "cb-buzz" if shape == "hummingbird" else "cb-wing"
    wop = ' opacity="0.75"' if shape == "hummingbird" else ""
    w = []
    if a.get("wing_bars"):
        for k in (0, 7, 14):
            w.append(f'<path d="M{cx-14+k},{cy-14} L{cx-20+k},{cy+16}" stroke="{a["wing_bars"]}" stroke-width="2.2"/>')
    if a.get("wing_tips"):
        for k in (0, 7, 14):
            w.append(f'<circle cx="{cx-21+k}" cy="{cy+9}" r="1.8" fill="{a["wing_tips"]}"/>')
    if a.get("wing_patch"):
        w.append(f'<ellipse cx="{cx-6}" cy="{cy+4}" rx="7" ry="4" fill="{a["wing_patch"]}"/>')
    if a.get("wing_spots"):
        for dx, dy in ((-12, -2), (-4, 2), (-16, 6), (-8, 8)):
            w.append(f'<circle cx="{cx+dx}" cy="{cy+dy}" r="1.5" fill="{a["wing_spots"]}"/>')
    if a.get("spots"):
        for dx, dy in ((-10, -4), (0, 0), (-16, 4), (-6, 8), (4, -8)):
            w.append(f'<circle cx="{cx+dx}" cy="{cy+dy}" r="2" fill="{a["spots"]}"/>')
    if a.get("zebra"):
        for k in range(-14, 20, 6):
            w.append(f'<path d="M{cx-30},{cy+k} L{cx+20},{cy+k-6}" stroke="{a["zebra"]}" stroke-width="2.4"/>')
    if a.get("wing_edge"):
        w.append(f'<path d="{wing}" fill="none" stroke="{a["wing_edge"]}" stroke-width="7" transform="translate(-3 4)"/>')
    if a.get("shoulder"):
        w.append(f'<ellipse cx="{cx+8}" cy="{cy-8}" rx="8" ry="5" fill="{a["shoulder"]}"/>'
                 f'<ellipse cx="{cx+6}" cy="{cy-3}" rx="7" ry="2" fill="#fde047"/>')
    o.append(_st(3, f'<g class="{wclass}"><path d="{wing}" fill="{a["wing"]}"{wop}/>'
                    + _st(6, '<g clip-path="url(#w__UID__)">' + "".join(w) + '</g>')
                    + f'<path d="{wing}" fill="none" stroke="{S}" stroke-width="2.2" stroke-linejoin="round"/></g>'))
    # crest (drawn before the head so its base tucks underneath)
    if a.get("crest"):
        c = (f'<path d="M{_n(hx-r*.45)},{_n(hy-r*.75)} Q{_n(hx-r*.95)},{_n(hy-r*1.45)} {_n(hx-r*.9)},{_n(hy-r*1.85)} '
             f'Q{_n(hx-r*.05)},{_n(hy-r*1.5)} {_n(hx+r*.35)},{_n(hy-r*.85)} Z" fill="{a["crest"]}" stroke="{S}" stroke-width="2.2" stroke-linejoin="round"/>')
        if a.get("crest2") or shape == "roadrunner":
            c += (f'<path d="M{_n(hx-r*.8)},{_n(hy-r*.5)} Q{_n(hx-r*1.5)},{_n(hy-r*1)} {_n(hx-r*1.6)},{_n(hy-r*1.3)} '
                  f'Q{_n(hx-r*.9)},{_n(hy-r*1.1)} {_n(hx-r*.3)},{_n(hy-r*.8)} Z" fill="{a["crest"]}" stroke="{S}" stroke-width="2.2" stroke-linejoin="round"/>')
        o.append(_st(2, c))
    # head + face markings (clipped to the head circle)
    o.append(_st(2, f'<circle cx="{hx}" cy="{hy}" r="{r}" fill="{a["head"]}"/>'))
    f = []
    if a.get("cheek"):
        f.append(f'<ellipse cx="{_n(hx+r*.15)}" cy="{_n(hy+r*.5)}" rx="{_n(r*.8)}" ry="{_n(r*.5)}" fill="{a["cheek"]}"/>')
    if a.get("cap"):
        f.append(f'<rect x="{hx-r}" y="{hy-r}" width="{2*r}" height="{_n(r*a.get("cap_h", .8))}" fill="{a["cap"]}"/>')
    if a.get("crown_stripe"):  # a pale stripe along the middle of the crown (white-crowned & white-throated sparrows)
        f.append(f'<path d="M{_n(hx-r*.95)},{_n(hy-r*.5)} Q{_n(hx)},{_n(hy-r*.85)} {_n(hx+r*.6)},{_n(hy-r*.62)}" '
                 f'stroke="{a["crown_stripe"]}" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
    if a.get("eye_line"):  # a dark line through the eye
        f.append(f'<path d="M{_n(hx-r*.95)},{_n(hy-r*.02)} L{_n(hx+r*.72)},{_n(hy-r*.14)}" stroke="{a["eye_line"]}" stroke-width="2.6" stroke-linecap="round"/>')
    if a.get("nape"):  # small patch on the back of the head (woodpeckers)
        f.append(f'<ellipse cx="{_n(hx-r*.85)}" cy="{_n(hy-r*.3)}" rx="{_n(r*.3)}" ry="{_n(r*.25)}" fill="{a["nape"]}"/>')
    if a.get("mask"):
        f.append(f'<ellipse cx="{_n(hx+r*.8)}" cy="{_n(hy+r*.15)}" rx="{_n(r*.5)}" ry="{_n(r*.42)}" fill="{a["mask"]}"/>')
    if a.get("face_stripes"):  # kestrel "mustache": one stripe under the eye, one behind it
        for dx in (.3, -.25):
            f.append(f'<path d="M{_n(hx+r*dx)},{_n(hy+r*.1)} L{_n(hx+r*(dx-.05))},{_n(hy+r*.7)}" stroke="{a["face_stripes"]}" stroke-width="3" stroke-linecap="round"/>')
    if a.get("throat"):
        f.append(f'<ellipse cx="{_n(hx+r*.45)}" cy="{_n(hy+r*.9)}" rx="{_n(r*.6)}" ry="{_n(r*.42)}" fill="{a["throat"]}"/>')
    if a.get("bib"):
        f.append(f'<ellipse cx="{_n(hx+r*.45)}" cy="{_n(hy+r*1.0)}" rx="{_n(r*.5)}" ry="{_n(r*.42)}" fill="{a["bib"]}"/>')
    if a.get("collar"):
        f.append(f'<rect x="{hx-r}" y="{_n(hy+r*.78)}" width="{2*r}" height="3.5" fill="{a["collar"]}"/>')
    if a.get("necklace"):
        f.append(f'<path d="M{_n(hx-r*.7)},{_n(hy+r*.5)} Q{_n(hx+r*.2)},{_n(hy+r*1.1)} {_n(hx+r)},{_n(hy+r*.4)}" '
                 f'stroke="{a["necklace"]}" stroke-width="3.5" fill="none"/>')
    if a.get("bands"):  # killdeer: two black bands across the throat
        for k in (.45, .85):
            f.append(f'<path d="M{_n(hx-r)},{_n(hy+r*k)} Q{_n(hx+r*.2)},{_n(hy+r*(k+.3))} {_n(hx+r)},{_n(hy+r*(k-.1))}" '
                     f'stroke="{a["bands"]}" stroke-width="3.5" fill="none"/>')
    if a.get("forehead"):
        f.append(f'<ellipse cx="{_n(hx+r*.85)}" cy="{_n(hy-r*.15)}" rx="{_n(r*.25)}" ry="{_n(r*.22)}" fill="{a["forehead"]}"/>')
    if a.get("eye_patch"):
        f.append(f'<ellipse cx="{_n(hx-r*.05)}" cy="{_n(hy-r*.1)}" rx="{_n(r*.28)}" ry="{_n(r*.16)}" fill="#f97316"/>'
                 f'<ellipse cx="{_n(hx-r*.3)}" cy="{_n(hy-r*.1)}" rx="{_n(r*.14)}" ry="{_n(r*.12)}" fill="#3b82f6"/>')
    if a.get("streaks") and shape == "roadrunner":
        for dx, dy in ((-8, -8), (-4, -12), (-12, -2)):
            f.append(f'<ellipse cx="{hx+dx}" cy="{hy+dy}" rx="1.2" ry="2.6" fill="{a["streaks"]}"/>')
    o.append(_st(6, '<g clip-path="url(#h__UID__)">' + "".join(f) + '</g>'))
    o.append(_st(2, f'<circle cx="{hx}" cy="{hy}" r="{r}" fill="none" stroke="{S}" stroke-width="2.5"/>'))
    # eye
    ex, ey = hx + .32 * r, hy - .12 * r
    er = r * .34 * a.get("eye_scale", 1)
    if a.get("brow_color"):
        o.append(_st(6, f'<path d="M{_n(ex-er*2.4)},{_n(ey-er*1.1)} Q{_n(ex)},{_n(ey-er*1.9)} {_n(ex+er*1.6)},{_n(ey-er*1.2)}" '
                        f'stroke="{a["brow_color"]}" stroke-width="3" fill="none" stroke-linecap="round"/>'))
    if a.get("eye_ring"):
        o.append(_st(6, f'<circle cx="{_n(ex)}" cy="{_n(ey)}" r="{_n(er+2.2)}" fill="{a["eye_ring"]}"/>'))
    iris = a.get("iris", "#ffffff")
    pupil = .42 if iris != "#ffffff" else .58
    o.append(_st(4, f'<g class="bird-blink"><circle cx="{_n(ex)}" cy="{_n(ey)}" r="{_n(er)}" fill="{iris}" stroke="{S}" stroke-width="2"/>'
                    f'<circle cx="{_n(ex+er*.18)}" cy="{_n(ey+er*.08)}" r="{_n(er*pupil)}" fill="#0f172a"/>'
                    f'<circle cx="{_n(ex+er*.38)}" cy="{_n(ey-er*.3)}" r="{_n(er*.25)}" fill="#fff"/></g>'))
    if a.get("brow"):
        o.append(_st(4, f'<path d="M{_n(ex-er*1.3)},{_n(ey-er*1.3)} L{_n(ex+er*1.3)},{_n(ey-er*.7)}" stroke="{S}" stroke-width="2.6" stroke-linecap="round"/>'))
    o.append(_st(6, f'<ellipse cx="{_n(hx+r*.12)}" cy="{_n(hy+r*.42)}" rx="{_n(r*.22)}" ry="{_n(r*.13)}" fill="#fb7185" opacity="0.45"/>'))
    # beak
    bx, by = hx + r * .88, hy + r * .12
    bt = a.get("beak_type", "small")
    if bt == "cone":
        d = f"M{_n(bx-2)},{_n(by-r*.42)} L{_n(bx+r*.8)},{_n(by)} L{_n(bx-2)},{_n(by+r*.42)} Z"
    elif bt == "thin":
        d = f"M{_n(bx-1)},{_n(by-r*.17)} L{_n(bx+r*.75)},{_n(by)} L{_n(bx-1)},{_n(by+r*.17)} Z"
    elif bt == "long":
        d = f"M{_n(bx-1)},{_n(by-r*.2)} L{_n(bx+r*1.1)},{_n(by+1)} L{_n(bx-1)},{_n(by+r*.2)} Z"
    elif bt == "hook":
        d = (f"M{_n(bx-2)},{_n(by-r*.35)} Q{_n(bx+r*.75)},{_n(by-r*.4)} {_n(bx+r*.7)},{_n(by+r*.28)} "
             f"L{_n(bx+r*.45)},{_n(by+r*.05)} L{_n(bx-2)},{_n(by+r*.3)} Z")
    elif bt == "chisel":
        d = f"M{_n(bx-1)},{_n(by-r*.22)} L{_n(bx+r*.95)},{_n(by)} L{_n(bx-1)},{_n(by+r*.22)} Z"
    elif bt == "needle":
        d = f"M{_n(bx-1)},{_n(by-1.6)} L{_n(bx+r*1.9)},{_n(by)} L{_n(bx-1)},{_n(by+1.6)} Z"
    elif bt == "upturned":  # avocet
        d = (f"M{_n(bx-1)},{_n(by-r*.18)} Q{_n(bx+r*1.2)},{_n(by-r*.2)} {_n(bx+r*1.9)},{_n(by-r*.9)} "
             f"Q{_n(bx+r*1.1)},{_n(by+r*.15)} {_n(bx-1)},{_n(by+r*.2)} Z")
    elif bt == "bill":
        d = (f"M{_n(bx-2)},{_n(by-r*.3)} Q{_n(bx+r*.9)},{_n(by-r*.3)} {_n(bx+r*.95)},{_n(by+r*.1)} "
             f"Q{_n(bx+r*.5)},{_n(by+r*.35)} {_n(bx-2)},{_n(by+r*.25)} Z")
    else:
        d = f"M{_n(bx-1)},{_n(by-r*.24)} L{_n(bx+r*.5)},{_n(by)} L{_n(bx-1)},{_n(by+r*.24)} Z"
    beak = f'<path d="{d}" fill="{a["beak"]}" stroke="{S}" stroke-width="2" stroke-linejoin="round"/>'
    if bt == "cone":
        beak += f'<path d="M{_n(bx-1)},{_n(by)} L{_n(bx+r*.6)},{_n(by)}" stroke="{S}" stroke-width="1.4"/>'
    o.append(_st(4, beak))
    return "".join(o)


def _heron_parts(a):
    S = OUTLINE
    o = [_st(0, '<ellipse cx="58" cy="113" rx="28" ry="5" fill="#0f172a" opacity="0.12"/>')]
    o.append(_st(5, "".join(f'<path d="M{x1},76 L{x2},110 M{x2-5},110 L{x2+6},110" stroke="{a["legs"]}" stroke-width="3" stroke-linecap="round" fill="none"/>'
                            for x1, x2 in ((50, 48), (60, 62)))))
    o.append(_st(3, f'<path d="M30,62 L8,72 L12,80 L32,72 Z" fill="{a["wing"]}" stroke="{S}" stroke-width="2.2" stroke-linejoin="round"/>'))
    neck = "M68,60 Q60,42 72,34 Q84,26 84,20"
    o.append(_st(2, f'<path d="{neck}" stroke="{S}" stroke-width="13" fill="none" stroke-linecap="round"/>'
                    f'<path d="{neck}" stroke="{a["neck"]}" stroke-width="8.5" fill="none" stroke-linecap="round"/>'))
    o.append(_st(1, f'<ellipse cx="50" cy="64" rx="28" ry="15" transform="rotate(-12 50 64)" fill="{a["body"]}" stroke="{S}" stroke-width="2.5"/>'))
    o.append(_st(3, f'<path class="cb-wing" d="M28,58 Q50,46 70,56 Q56,76 24,70 Q20,62 28,58 Z" fill="{a["wing"]}" stroke="{S}" stroke-width="2.2" stroke-linejoin="round"/>'))
    o.append(_st(2, f'<circle cx="86" cy="20" r="11" fill="{a["head"]}" stroke="{S}" stroke-width="2.5"/>'))
    if a.get("plume"):
        o.append(_st(6, f'<path d="M80,13 Q90,9 96,15" stroke="{a["plume"]}" stroke-width="4" fill="none" stroke-linecap="round"/>'
                        f'<path d="M80,14 Q70,12 62,18" stroke="{a["plume"]}" stroke-width="3" fill="none" stroke-linecap="round"/>'))
    o.append(_st(4, '<g class="bird-blink"><circle cx="89" cy="19" r="3.8" fill="#fde047" stroke="#1e293b" stroke-width="1.6"/>'
                    '<circle cx="89.6" cy="19.3" r="1.7" fill="#0f172a"/></g>'))
    o.append(_st(4, f'<path d="M95,19 L119,23 L95,26 Z" fill="{a["beak"]}" stroke="{S}" stroke-width="2" stroke-linejoin="round"/>'))
    o.append(_st(6, '<ellipse cx="84" cy="25" rx="2.6" ry="1.5" fill="#fb7185" opacity="0.45"/>'))
    return "".join(o)


def _owl_parts(a):
    S = OUTLINE
    o = [_st(0, '<ellipse cx="60" cy="112" rx="30" ry="5" fill="#0f172a" opacity="0.12"/>'), '<g class="owl-sway">']
    o.append(_st(1, f'<ellipse cx="60" cy="76" rx="31" ry="32" fill="{a["body"]}"/>'))
    marks = [f'<ellipse cx="60" cy="86" rx="20" ry="20" fill="{a["belly"]}"/>']
    marks += [f'<path d="M{x},76 L{x},98" stroke="{a["streaks"]}" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="5 3"/>' for x in (52, 60, 68)]
    marks += [f'<path d="M46,{y} Q60,{y+4} 74,{y}" stroke="{a["streaks"]}" stroke-width="2.2" fill="none"/>' for y in (68, 73)]
    o.append(_st(6, "".join(marks)))
    o.append(_st(1, f'<ellipse cx="60" cy="76" rx="31" ry="32" fill="none" stroke="{S}" stroke-width="2.5"/>'))
    o.append(_st(3, f'<ellipse cx="33" cy="80" rx="9" ry="22" transform="rotate(12 33 80)" fill="{a["wing"]}" stroke="{S}" stroke-width="2.2"/>'
                    f'<ellipse cx="87" cy="80" rx="9" ry="22" transform="rotate(-12 87 80)" fill="{a["wing"]}" stroke="{S}" stroke-width="2.2"/>'))
    if a.get("tufts"):
        o.append(_st(2, f'<path d="M38,30 L34,8 L52,22 Z M82,30 L86,8 L68,22 Z" fill="{a["body"]}" stroke="{S}" stroke-width="2.2" stroke-linejoin="round"/>'))
    o.append(_st(2, f'<circle cx="60" cy="42" r="27" fill="{a["body"]}" stroke="{S}" stroke-width="2.5"/>'))
    for cx in (48, 72):
        o.append(_st(4, f'<ellipse cx="{cx}" cy="44" rx="13.5" ry="14" fill="{a["face"]}"/>'))
        o.append(_st(6, f'<ellipse cx="{cx}" cy="44" rx="10.5" ry="11" fill="none" stroke="{a["streaks"]}" stroke-width="1" opacity="0.5"/>'))
        o.append(_st(4, f'<g class="bird-blink"><circle cx="{cx}" cy="44" r="7.5" fill="{a["iris"]}" stroke="{S}" stroke-width="2"/>'
                        f'<circle cx="{cx}" cy="44" r="3.8" fill="#0f172a"/><circle cx="{cx+2.4}" cy="41.4" r="1.9" fill="#fff"/></g>'))
    o.append(_st(4, f'<path d="M56,50 L64,50 L60,59 Z" fill="{a["beak"]}" stroke="{S}" stroke-width="1.8" stroke-linejoin="round"/>'))
    o.append(_st(5, "".join(f'<path d="M{x-5},106 L{x-3},100 M{x},107 L{x},100 M{x+5},106 L{x+3},100" stroke="#facc15" stroke-width="3" stroke-linecap="round"/>'
                            for x in (52, 68))))
    o.append(_st(6, '<ellipse cx="42" cy="56" rx="4" ry="2.2" fill="#fb7185" opacity="0.4"/><ellipse cx="78" cy="56" rx="4" ry="2.2" fill="#fb7185" opacity="0.4"/>'))
    o.append('</g>')
    return "".join(o)


def face_viewbox(a):
    """The square part of a cartoon that shows the bird's head and beak (used for map pins)."""
    shape = a.get("shape", "songbird")
    if shape == "owl":
        return "28 6 64 64"
    hx, hy, r = (86, 20, 11) if shape == "heron" else GEOMETRY[shape]["head"]
    return f"{_n(hx - 1.35 * r)} {_n(hy - 1.5 * r)} {_n(3 * r)} {_n(3 * r)}"


def cartoon_bird_svg(bird):
    a = bird["art"]
    shape = a.get("shape", "songbird")
    inner = _owl_parts(a) if shape == "owl" else _heron_parts(a) if shape == "heron" else _songbird_parts(a)
    return f'<svg viewBox="0 0 120 120" class="bird-svg cartoon" role="img" aria-label="{bird["name"]} cartoon">{inner}</svg>'


for _b in TEXAS_BIRDS:
    _b["svg"] = cartoon_bird_svg(_b)
    _b["face_vb"] = face_viewbox(_b["art"])
    _b["wiki"] = _b.get("wiki") or _b["name"][0] + _b["name"][1:].lower()       # "Northern cardinal"
    _b["wiki_url"] = "https://en.wikipedia.org/wiki/" + _b["wiki"].replace(" ", "_")
    # Cornell Lab's All About Birds, e.g. .../guide/Coopers_Hawk (no apostrophes in their links)
    _b["aab_url"] = "https://www.allaboutbirds.org/guide/" + _b["name"].replace(" ", "_").replace("'", "")
BIRDS_BY_ID = {b["id"]: b for b in TEXAS_BIRDS}
BIRDS_BY_SCI = {b["inat"].lower(): b for b in TEXAS_BIRDS}

# ==========================================
# 3. FACTS / VIDEOS / BADGES
# ==========================================
# Backup facts, used only until the live Wikipedia facts are ready (or if the internet is down).
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

# Showtime picks 6 random clips + 1 live cam on every page load. All IDs were checked with
# YouTube's oEmbed (exists + embeddable) on Oct 24, 2026, and are re-checked when the app runs.
SHOWTIME_VIDEOS = [
    {"title": "Learn About Baby Birds", "channel": "Nat Geo Kids", "video_id": "JF4pBKXUAFc", "emoji": "🐣"},
    {"title": "Merlin Bird ID Demo", "channel": "Cornell Lab", "video_id": "xmSUOLxyatY", "emoji": "🔍"},
    {"title": "Blue Jay", "channel": "American Bird Conservancy", "video_id": "QbWIrZUlX3Q", "emoji": "💙"},
    {"title": "50 Birds, 50 States", "channel": "Nat Geo Kids", "video_id": "Av_-_8B_ePQ", "emoji": "🗺️"},
    {"title": "Eastern Bluebird: Bird in the Spotlight", "channel": "Cornell Lab", "video_id": "PQlRkqnFdPM", "emoji": "🔵"},
    {"title": "Great Blue Heron: Bird in the Spotlight", "channel": "Cornell Lab", "video_id": "G643AE1s4gY", "emoji": "🐟"},
    {"title": "Hummingbirds Hover and Sparkle", "channel": "Cornell Lab", "video_id": "6WODTffcmhI", "emoji": "✨"},
    {"title": "Northern Cardinal Craziness at the Feeders", "channel": "Cornell Lab Bird Cams", "video_id": "o1g4RGFbB80", "emoji": "❤️"},
    {"title": "Male Cardinal Feeds Female", "channel": "Cornell Lab Bird Cams", "video_id": "YRHNo0YT4R0", "emoji": "💝"},
    {"title": "Red-bellied Woodpecker vs. Northern Cardinal", "channel": "Cornell Lab Bird Cams", "video_id": "wroiEnrehnU", "emoji": "🥊"},
    {"title": "Blue Jay Photobombs the Camera", "channel": "Cornell Lab Bird Cams", "video_id": "3zcAjudnnOA", "emoji": "📸"},
    {"title": "Blue Jays Wait for Peanuts", "channel": "Cornell Lab Bird Cams", "video_id": "zryA5ws5EP8", "emoji": "🥜"},
    {"title": "Hummingbirds Wait for a Nectar Refill", "channel": "Cornell Lab Bird Cams", "video_id": "QT2EHSx011Y", "emoji": "🌺"},
    {"title": "Barred Owl Hoots from the Nest Box", "channel": "Cornell Lab Bird Cams", "video_id": "BqKHbFLXHAk", "emoji": "🦉"},
    {"title": "Owl Mom Feeds Her Owlets (Austin, Texas!)", "channel": "Cornell Lab Bird Cams", "video_id": "_Wa7Jpxc0M8", "emoji": "🤠"},
    {"title": "Mockingbird's First Visit to the Feeder Cam", "channel": "Cornell Lab Bird Cams", "video_id": "emfMg2F9opw", "emoji": "🎶"},
    {"title": "Chickadee, Titmouse & Nuthatch Parade", "channel": "Cornell Lab Bird Cams", "video_id": "8zWOFemCPz4", "emoji": "🎉"},
    {"title": "Tufted Titmouse Smiles for the Camera", "channel": "Cornell Lab Bird Cams", "video_id": "QUp3WDWN-Oo", "emoji": "😊"},
    {"title": "Eastern Bluebird Close-Up", "channel": "Cornell Lab Bird Cams", "video_id": "CABvR7-Wqhk", "emoji": "💙"},
    {"title": "Life on the Ledge: Robin Nest Highlights", "channel": "Cornell Lab Bird Cams", "video_id": "l_pxj7u5ytE", "emoji": "🪺"},
    {"title": "Last Robin Chick Leaves the Nest", "channel": "Cornell Lab Bird Cams", "video_id": "-AZ-oY-dMI0", "emoji": "🐣"},
    {"title": "Double Catch! Heron Grabs Two Fish", "channel": "Cornell Lab Bird Cams", "video_id": "EA7vj9oXv2o", "emoji": "🎣"},
    {"title": "Great Blue Heron Preens Its Long Neck", "channel": "Cornell Lab Bird Cams", "video_id": "14SabkXlog0", "emoji": "🪶"},
    {"title": "A Group of Grackles Visits the Feeders", "channel": "Cornell Lab Bird Cams", "video_id": "9lT_s9Dcv6c", "emoji": "🖤"},
    {"title": "Mourning Dove Takeover", "channel": "Cornell Lab Bird Cams", "video_id": "56eD0DU28Hg", "emoji": "🕊️"},
    {"title": "Woodpeckers Share the Spotlight", "channel": "Cornell Lab Bird Cams", "video_id": "0ejXBJryh48", "emoji": "🪵"},
    {"title": "Red-tailed Hawk Nest Highlights", "channel": "Cornell Lab Bird Cams", "video_id": "VklUSvNqBOI", "emoji": "🦅"},
    {"title": "Hawk Fledgling Close-Up", "channel": "Cornell Lab Bird Cams", "video_id": "ksReW4lhHxs", "emoji": "🦅"},
    {"title": "Can't-Miss Bird Cam Moments", "channel": "Cornell Lab Bird Cams", "video_id": "mwZysYcqGy4", "emoji": "🌟"},
]
LIVE_CAMS = [
    {"title": "Cornell Lab FeederWatch Cam (New York)", "channel": "Cornell Lab Bird Cams", "video_id": "x10vL6_47Dw", "emoji": "🌳", "live": True},
    {"title": "Panama Hummingbird Feeder Cam", "channel": "Cornell Lab Bird Cams", "video_id": "0xFARCdZ3vA", "emoji": "🌺", "live": True},
    {"title": "Cornell Red-tailed Hawks Cam", "channel": "Cornell Lab Bird Cams", "video_id": "afsaYKQ3vac", "emoji": "🦅", "live": True},
    {"title": "Hellgate Ospreys Nest Cam (Montana)", "channel": "Cornell Lab Bird Cams", "video_id": "J7HO0dkkomE", "emoji": "🐟", "live": True},
    {"title": "Royal Albatross Cam (New Zealand)", "channel": "Cornell Lab Bird Cams", "video_id": "Mm_zVDDUeNA", "emoji": "🌊", "live": True},
]

# "type" says what a badge counts: birds checked off, best quiz score, Photo ID finds, puzzles solved,
# or "art" = different Bird Book birds you drew well enough for Photo ID to recognize (likeness 60+).
# Listed easiest first (by goal), so the Prizes tab reads in order.
PRIZE_BADGES = [
    {"id": "hatchling", "name": "Hatchling Spotter", "goal": 1, "emoji": "🥚", "color": "#94a3b8", "type": "spotted"},
    {"id": "photo_detective", "name": "Photo Detective", "goal": 1, "emoji": "🕵️", "color": "#14b8a6", "type": "photoid"},
    {"id": "fledgling", "name": "Fledgling Birder", "goal": 5, "emoji": "🐤", "color": "#22c55e", "type": "spotted"},
    {"id": "puzzle_pro", "name": "Puzzle Pro", "goal": 5, "emoji": "🧩", "color": "#6366f1", "type": "puzzle"},
    {"id": "quiz_whiz", "name": "Quiz Whiz", "goal": 8, "emoji": "🧠", "color": "#ec4899", "type": "quiz"},
    {"id": "master_artist", "name": "Master Artist", "goal": 10, "emoji": "🎨", "color": "#f97316", "type": "art"},
    {"id": "flock_leader", "name": "Flock Leader", "goal": 15, "emoji": "🐦", "color": "#0ea5e9", "type": "spotted"},
    {"id": "master_birder", "name": "Master Birder", "goal": 30, "emoji": "🦅", "color": "#f59e0b", "type": "spotted"},
    {"id": "chirp_legend", "name": "ChirpQuest Legend", "goal": len(TEXAS_BIRDS), "emoji": "🏆", "color": "#a855f7", "type": "spotted"},
]

# ==========================================
# 4. LIVE DATA: iNaturalist (photos, sightings, seasons), Wikipedia (facts), YouTube (video checks)
# ==========================================
HTTP_HEADERS = {"User-Agent": "ChirpQuest/2.0 (kids birding school project; https://github.com/narendrakumarachari/hana-projects)"}
INAT_API = "https://api.inaturalist.org/v1"
TEXAS_PLACE_ID = 18                 # iNaturalist's id for the state of Texas
DFW_CENTER = (32.78, -96.97)        # between Dallas and Fort Worth
SIGHTING_RADIUS_KM = 50

_photo_cache = {}

def fetch_inat_photo(scientific_name):
    """Return a real CC-licensed photo URL for a species, or None. Cached in memory."""
    if scientific_name in _photo_cache:
        return _photo_cache[scientific_name]
    try:
        r = requests.get(
            f"{INAT_API}/taxa",
            params={"q": scientific_name, "rank": "species", "per_page": 1},
            headers=HTTP_HEADERS, timeout=8,
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
        return None  # not cached, so it is tried again next time

_season_cache = {}

def _texas_month_counts(**taxon):
    r = requests.get(f"{INAT_API}/observations/histogram", headers=HTTP_HEADERS, timeout=10, params={
        **taxon, "place_id": TEXAS_PLACE_ID, "interval": "month_of_year", "date_field": "observed", "verifiable": "true"})
    r.raise_for_status()
    months = r.json()["results"]["month_of_year"]
    return [months.get(str(m), 0) for m in range(1, 13)]

def fetch_season(bird):
    """When to look for a bird: its share of all Texas bird sightings in each month (Jan..Dec).
    Raw counts would make every bird peak in April, just because more people go birding then."""
    if "all" not in _season_cache:
        _season_cache["all"] = _texas_month_counts(taxon_id=3)  # 3 = all birds (Aves)
    if bird["id"] not in _season_cache:
        mine = _texas_month_counts(taxon_name=bird["inat"])
        _season_cache[bird["id"]] = [round(1000 * m / a, 2) if a else 0 for m, a in zip(mine, _season_cache["all"])]
    return _season_cache[bird["id"]]

_cc_photo_cache = {}

def fetch_cc_photos(taxon_name, place_id=TEXAS_PLACE_ID):  # taxon_name: species name, or taxon id number
    """Up to 30 of the most-liked research-grade, Creative-Commons photos of a bird (or bird group) from iNaturalist."""
    key = (taxon_name, place_id)
    if not _cc_photo_cache.get(key):
        # a number is an iNaturalist taxon id (needed for groups like "all penguins"); text is a species name
        taxon = {"taxon_id": taxon_name} if isinstance(taxon_name, int) else {"taxon_name": taxon_name}
        params = {**taxon, "quality_grade": "research", "photos": "true",
                  "photo_license": "cc-by,cc-by-nc,cc0", "per_page": 30, "order_by": "votes"}
        if place_id:
            params["place_id"] = place_id
        r = requests.get(f"{INAT_API}/observations", headers=HTTP_HEADERS, timeout=10, params=params)
        r.raise_for_status()
        photos = []
        for obs in r.json().get("results", []):
            if obs.get("photos"):
                p = obs["photos"][0]
                photos.append({"url": p["url"].replace("/square.", "/medium."), "credit": p.get("attribution", "")})
        _cc_photo_cache[key] = photos
    return _cc_photo_cache[key]

_taxon_photo_cache = {}

def fetch_taxon_photos(taxon):
    """The hand-picked photos iNaturalist curators chose to show what a bird looks like (clear, close-up).
    Only Creative-Commons ones; the first 3 are the most typical."""
    if taxon not in _taxon_photo_cache:
        tid = taxon if isinstance(taxon, int) else requests.get(
            f"{INAT_API}/taxa", headers=HTTP_HEADERS, timeout=10, params={"q": taxon, "per_page": 1}).json()["results"][0]["id"]
        r = requests.get(f"{INAT_API}/taxa/{tid}", headers=HTTP_HEADERS, timeout=10)
        r.raise_for_status()
        photos = [{"url": tp["photo"]["medium_url"], "credit": tp["photo"].get("attribution", "")}
                  for tp in r.json()["results"][0].get("taxon_photos", []) if tp["photo"].get("license_code")]
        _taxon_photo_cache[taxon] = photos[:3]
    return _taxon_photo_cache[taxon]

def fetch_quiz_photos(bird):
    """Different real photos of one of our birds, taken in Texas."""
    return fetch_cc_photos(bird["inat"])

# ---- Real bird sounds: the best-rated Creative-Commons recordings on iNaturalist ----
# They are passed through this server (not linked directly) because a browser is only allowed to
# analyze audio from its own website, and the spectrogram needs to analyze it.
MAX_SOUND_BYTES = 1_500_000   # skip huge recordings (long WAV files)
_sound_list_cache = {}
_sound_file_cache = {}

def fetch_sound_list(taxon):
    """Up to 12 recordings of a bird; taxon is a scientific name or an iNaturalist taxon id."""
    if taxon not in _sound_list_cache:
        which = {"taxon_id": taxon} if isinstance(taxon, int) else {"taxon_name": taxon}
        r = requests.get(f"{INAT_API}/observations", headers=HTTP_HEADERS, timeout=12, params={
            **which, "sounds": "true", "quality_grade": "research", "sound_license": "cc-by,cc-by-nc,cc0",
            "per_page": 12, "order_by": "votes"})
        r.raise_for_status()
        sounds = []
        for obs in r.json().get("results", []):
            for s in obs.get("sounds") or []:
                if s.get("file_url") and (s.get("file_content_type") or "").startswith("audio/"):
                    sounds.append({"url": s["file_url"], "credit": s.get("attribution") or ""})
                    break
        _sound_list_cache[taxon] = sounds
    return _sound_list_cache[taxon]

def fetch_sound_file(url):
    if url not in _sound_file_cache:
        r = requests.get(url, headers=HTTP_HEADERS, timeout=20, stream=True)
        r.raise_for_status()
        data = r.raw.read(MAX_SOUND_BYTES + 1, decode_content=True)
        if len(data) > MAX_SOUND_BYTES:
            raise ValueError("recording too big")
        if len(_sound_file_cache) > 250:  # keep memory use small
            _sound_file_cache.clear()
        _sound_file_cache[url] = (r.headers.get("Content-Type", "audio/mpeg").split(";")[0], data)
    return _sound_file_cache[url]

# ---- Bird holidays: on these days the Welcome banner says "Happy ...!" with a real iNaturalist photo ----
# "when" rules:  ("date", month, day)  ·  ("nth", month, weekday, n) with Monday=0, e.g. 2nd Saturday = (5, 5, 2)
#                ("span", (m1, d1), (m2, d2)) for events that run over several days (may cross New Year)
#                ("month", m) for a whole month
#                ("gbbc",) = the 4 days ending on Presidents' Day (3rd Monday of February)
# Dates looked up Oct 2026: Geneva Environment Network (World Migratory Bird Day: 2nd Sat of May + Oct),
# Audubon (Great Backyard Bird Count), trvst.world bird awareness calendar (fixed-date days),
# awarenessdays.com (Dawn Chorus Day, Hummingbird Day), 4vultures.org (Vulture Day), nationaldaycalendar.com (Bird Day),
# hepper.com (Pet Bird Day), EarthSky (Shorebirds Day), Wikipedia (Bird-Feeding Month).
# Christmas Bird Count = Audubon's usual Dec 14 – Jan 5.
BIRD_HOLIDAYS = [
    {"id": "national-bird-day", "name": "National Bird Day", "emoji": "🐦", "when": [("date", 1, 5)],
     "taxon": "Cardinalis cardinalis", "place": TEXAS_PLACE_ID,
     "message": "A whole day for celebrating birds! Step outside and see how many you can spot."},
    {"id": "penguin-awareness-day", "name": "Penguin Awareness Day", "emoji": "🐧", "when": [("date", 1, 20)],
     "taxon": 3806, "place": None,
     "message": "No wild penguins in Texas — but these tuxedo birds are amazing swimmers that 'fly' underwater!"},
    {"id": "great-backyard-bird-count", "name": "Great Backyard Bird Count", "emoji": "📋", "when": [("gbbc",)],
     "taxon": "Poecile carolinensis", "place": TEXAS_PLACE_ID, "link": "https://www.birdcount.org/",
     "message": "Count the birds in your yard for 15 minutes and share them with scientists around the world!"},
    {"id": "world-sparrow-day", "name": "World Sparrow Day", "emoji": "🐤", "when": [("date", 3, 20)],
     "taxon": 559248, "place": TEXAS_PLACE_ID,
     "message": "Little brown birds are easy to miss. Look closely — Texas has dozens of kinds of sparrows!"},
    {"id": "draw-a-bird-day", "name": "Draw a Bird Day", "emoji": "🎨", "when": [("date", 4, 8)],
     "taxon": "Passerina ciris", "place": TEXAS_PLACE_ID,
     "message": "Grab your crayons! Try drawing the most colorful bird in Texas, the Painted Bunting."},
    {"id": "world-penguin-day", "name": "World Penguin Day", "emoji": "🐧", "when": [("date", 4, 25)],
     "taxon": 3806, "place": None,
     "message": "Penguins are starting their long migration right about now. Waddle on!"},
    {"id": "dawn-chorus-day", "name": "International Dawn Chorus Day", "emoji": "🌅", "when": [("nth", 5, 6, 1)],
     "taxon": "Mimus polyglottos", "place": TEXAS_PLACE_ID,
     "message": "Wake up early and listen: birds sing the most right around sunrise!"},
    {"id": "world-migratory-bird-day", "name": "World Migratory Bird Day", "emoji": "🦢",
     "when": [("nth", 5, 5, 2), ("nth", 10, 5, 2)], "taxon": "Antigone canadensis", "place": TEXAS_PLACE_ID,
     "link": "https://www.migratorybirdday.org/",
     "message": "Billions of birds are traveling across the sky. Sandhill Cranes fly over Texas on their trip south!"},
    {"id": "world-parrot-day", "name": "World Parrot Day", "emoji": "🦜", "when": [("date", 5, 31)],
     "taxon": "Myiopsitta monachus", "place": TEXAS_PLACE_ID,
     "message": "Did you know wild Monk Parakeets live in Dallas? They build giant stick nests together!"},
    {"id": "american-eagle-day", "name": "American Eagle Day", "emoji": "🦅", "when": [("date", 6, 20)],
     "taxon": "Haliaeetus leucocephalus", "place": TEXAS_PLACE_ID,
     "message": "The Bald Eagle came back from almost disappearing. Some even nest near Texas lakes!"},
    {"id": "owl-awareness-day", "name": "International Owl Awareness Day", "emoji": "🦉", "when": [("date", 8, 4)],
     "taxon": "Strix varia", "place": TEXAS_PLACE_ID,
     "message": "Owls can turn their heads almost all the way around. Listen for 'Who cooks for you?' tonight!"},
    {"id": "vulture-awareness-day", "name": "International Vulture Awareness Day", "emoji": "🧹", "when": [("nth", 9, 5, 1)],
     "taxon": "Cathartes aura", "place": TEXAS_PLACE_ID,
     "message": "Vultures are nature's cleanup crew — they keep the land healthy. Thank a vulture today!"},
    {"id": "christmas-bird-count", "name": "Christmas Bird Count", "emoji": "🎄", "when": [("span", (12, 14), (1, 5))],
     "taxon": "Cardinalis cardinalis", "place": TEXAS_PLACE_ID, "link": "https://www.audubon.org/conservation/join-christmas-bird-count",
     "message": "Bird lovers everywhere are counting birds for science — the longest-running bird count in the world!"},
    # ---- minor bird days: no banner or photo, just a small "Today is ..." line under Pip's message ----
    {"id": "save-the-eagles-day", "name": "National Save the Eagles Day", "emoji": "🦅", "when": [("date", 1, 10)], "major": False},
    {"id": "bird-feeding-month", "name": "National Bird-Feeding Month", "emoji": "🌻", "when": [("month", 2)], "major": False},
    {"id": "bird-day", "name": "Bird Day (since 1894!)", "emoji": "🐦", "when": [("date", 5, 4)], "major": False},
    {"id": "hummingbird-day", "name": "National Hummingbird Day", "emoji": "🌺", "when": [("nth", 9, 5, 1)], "major": False},
    {"id": "shorebirds-day", "name": "World Shorebirds Day", "emoji": "🏖️", "when": [("date", 9, 6)], "major": False},
    {"id": "pet-bird-day", "name": "National Pet Bird Day", "emoji": "🦜", "when": [("date", 9, 17)], "major": False},
]

def _nth_weekday(year, month, weekday, n):
    d = datetime.date(year, month, 1)
    return d + datetime.timedelta(days=(weekday - d.weekday()) % 7, weeks=n - 1)

def holiday_occurrences(h, year):
    """(start, end) dates of a holiday that touch the given year."""
    spans = []
    for rule in h["when"]:
        if rule[0] == "date":
            d = datetime.date(year, rule[1], rule[2]); spans.append((d, d))
        elif rule[0] == "nth":
            d = _nth_weekday(year, *rule[1:]); spans.append((d, d))
        elif rule[0] == "month":
            first = datetime.date(year, rule[1], 1)
            spans.append((first, (first + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)))
        elif rule[0] == "gbbc":
            end = _nth_weekday(year, 2, 0, 3); spans.append((end - datetime.timedelta(days=3), end))
        elif rule[0] == "span":
            (m1, d1), (m2, d2) = rule[1], rule[2]
            if (m2, d2) < (m1, d1):  # crosses New Year, e.g. Dec 14 – Jan 5
                spans += [(datetime.date(year - 1, m1, d1), datetime.date(year, m2, d2)),
                          (datetime.date(year, m1, d1), datetime.date(year + 1, m2, d2))]
            else:
                spans.append((datetime.date(year, m1, d1), datetime.date(year, m2, d2)))
    return spans

def holidays_on(day):
    """Every bird holiday happening on this day, one-day holidays first (they win over multi-day events)."""
    hits = [(end - start, h) for h in BIRD_HOLIDAYS for start, end in holiday_occurrences(h, day.year) if start <= day <= end]
    return [h for _, h in sorted(hits, key=lambda x: x[0])]

def next_holiday(day):
    upcoming = [(start, h) for h in BIRD_HOLIDAYS for y in (day.year, day.year + 1)
                for start, _ in holiday_occurrences(h, y) if start > day]
    return min(upcoming, key=lambda x: x[0])

_sightings_cache = {}

def _book_bird_for(taxon_name):
    """Match an iNaturalist name (maybe a subspecies, like 'Cardinalis cardinalis magnirostris') to our birds."""
    return BIRDS_BY_SCI.get(" ".join((taxon_name or "").lower().split()[:2]))

def fetch_sightings(lat, lng, days):
    """Recent wild-bird sightings around a point: map pins + the most-seen species. Cached 10 minutes."""
    key = (round(lat, 2), round(lng, 2), days)
    hit = _sightings_cache.get(key)
    if hit and time.time() - hit[0] < 600:
        return hit[1]
    d1 = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    area = {"iconic_taxa": "Aves", "lat": lat, "lng": lng, "radius": SIGHTING_RADIUS_KM, "d1": d1,
            "verifiable": "true", "captive": "false"}
    with ThreadPoolExecutor(2) as ex:
        obs_job = ex.submit(requests.get, f"{INAT_API}/observations", headers=HTTP_HEADERS, timeout=15,
                            params={**area, "per_page": 200, "order_by": "observed_on", "photos": "true", "geo": "true"})
        top_job = ex.submit(requests.get, f"{INAT_API}/observations/species_counts", headers=HTTP_HEADERS, timeout=15,
                            params={**area, "per_page": 8})
        obs_resp, top_resp = obs_job.result(), top_job.result()
    obs_resp.raise_for_status()
    top_resp.raise_for_status()
    sightings = []
    for o in obs_resp.json().get("results", []):
        taxon, geo = o.get("taxon") or {}, o.get("geojson") or {}
        if o.get("obscured") or geo.get("type") != "Point":
            continue  # skip blurred locations (rare birds / private nests) so every pin is accurate
        book = _book_bird_for(taxon.get("name"))
        photo = (o.get("photos") or [{}])[0]
        sightings.append({
            "name": taxon.get("preferred_common_name") or taxon.get("name") or "Unknown bird",
            "date": o.get("observed_on"), "lng": geo["coordinates"][0], "lat": geo["coordinates"][1],
            "photo": photo.get("url"), "credit": photo.get("attribution", ""), "link": o.get("uri"),
            "bird_id": book["id"] if book else None,
        })
    top = []
    for t in top_resp.json().get("results", []):
        book = _book_bird_for(t["taxon"].get("name"))
        top.append({"name": t["taxon"].get("preferred_common_name") or t["taxon"].get("name"),
                    "count": t["count"], "bird_id": book["id"] if book else None})
    data = {"total": obs_resp.json().get("total_results", 0), "sightings": sightings, "top": top,
            "center": [lat, lng], "days": days, "radius_km": SIGHTING_RADIUS_KM}
    _sightings_cache[key] = (time.time(), data)
    return data

# ---- Every bird species of North Texas (for Bird of the Day) ----
NORTH_TEXAS_RADIUS_KM = 150   # around Dallas–Fort Worth
MIN_SIGHTINGS = 25            # skips rare strays that only showed up once or twice
_nt_species = {"time": 0, "list": []}

def north_texas_species():
    """Every wild bird species (native or not, like the European Starling) with at least MIN_SIGHTINGS
    research-grade iNaturalist sightings near DFW. About 320 birds. Cached for a day."""
    if _nt_species["list"] and time.time() - _nt_species["time"] < 86400:
        return _nt_species["list"]
    r = requests.get(f"{INAT_API}/observations/species_counts", headers=HTTP_HEADERS, timeout=20, params={
        "iconic_taxa": "Aves", "lat": DFW_CENTER[0], "lng": DFW_CENTER[1], "radius": NORTH_TEXAS_RADIUS_KM,
        "quality_grade": "research", "captive": "false", "per_page": 500})
    r.raise_for_status()
    species = [{"taxon_id": x["taxon"]["id"], "name": x["taxon"].get("preferred_common_name") or x["taxon"]["name"],
                "sci": x["taxon"]["name"], "count": x["count"], "wiki": x["taxon"].get("wikipedia_url")}
               for x in r.json()["results"] if x["count"] >= MIN_SIGHTINGS and x["taxon"].get("rank") == "species"]
    species.sort(key=lambda s: s["taxon_id"])  # fixed order, so the same date always picks the same bird
    _nt_species.update(time=time.time(), list=species)
    log.info("North Texas bird list: %d species.", len(species))
    return species

# ---- Facts: real text from Wikipedia, rewritten for kids by Gemini ----
# (Cornell's All About Birds has no public API for its text, so each fact links there to learn more.)
WIKI_API = "https://en.wikipedia.org/w/api.php"
FACT_POOL_MAX_AGE = 12 * 3600
_fact_pool = []
_fact_pool_time = 0
_fact_lock = threading.Lock()

def fetch_wiki_text(bird, limit=2500):
    r = requests.get(WIKI_API, headers=HTTP_HEADERS, timeout=10, params={
        "action": "query", "prop": "extracts", "explaintext": 1, "redirects": 1, "format": "json", "titles": bird["wiki"]})
    r.raise_for_status()
    text = next(iter(r.json()["query"]["pages"].values())).get("extract", "")
    text = re.split(r"\n==\s*(See also|References|Notes|Further reading|External links)\s*==", text)[0]
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith("==")]
    return "\n".join(lines)[:limit]

def gemini_json(parts, max_tokens=4096, timeout=40):
    """One Gemini call that must answer in JSON. Tries each model in GEMINI_MODELS; returns parsed JSON or None."""
    key = get_current_gemini_key()
    if key in ("DUMMY_TEST_KEY_REPLACE_ME", "PUT_YOUR_KEY_HERE", ""):
        return None
    for model in GEMINI_MODELS:
        try:
            r = requests.post(GEMINI_URL_TEMPLATE.format(model=model), headers={"X-goog-api-key": key}, timeout=timeout, json={
                "contents": [{"parts": parts}],
                "generationConfig": {"responseMimeType": "application/json", "maxOutputTokens": max_tokens, "temperature": 0.7},
            })
            if r.status_code != 200:
                log.warning("Gemini JSON call: %s returned %s — trying the next model.", model, r.status_code)
                continue
            text = "".join(p.get("text", "") for p in r.json()["candidates"][0]["content"]["parts"])
            return json.loads(text)
        except Exception as e:
            log.warning("Gemini JSON call with %s failed: %s", model, e)
    return None

def _facts_from_gemini(batch, texts):
    prompt = (
        "You write fun facts for ChirpQuest, a birding app for kids aged 8 to 12 in North Texas. "
        "For EACH bird below, pick 3 surprising facts that are clearly stated in its text. "
        "Write each fact as one exciting sentence of at most 25 words, using simple words. "
        "Never add anything that is not in the text. "
        'Answer with a JSON list like [{"id": "<bird id>", "fact": "<sentence>"}].\n\n'
        + "\n\n".join(f"### id: {b['id']} ({b['name']})\n{texts[b['id']]}" for b in batch if texts.get(b["id"]))
    )
    result = gemini_json([{"text": prompt}], max_tokens=4096, timeout=45)
    facts = []
    for item in result if isinstance(result, list) else []:
        bird = BIRDS_BY_ID.get(str(item.get("id", "")))
        text = str(item.get("fact", "")).strip()
        if bird and 20 < len(text) < 300:
            facts.append(_fact(bird, text, ai=True))
    return facts

def _facts_from_text(bird, text, n=3):
    """No Gemini? Use plain sentences straight from Wikipedia instead."""
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if 50 <= len(s) <= 170 and "(" not in s]
    return [_fact(bird, s, ai=False) for s in random.sample(sentences, min(n, len(sentences)))]

def _fact(bird, text, ai):
    return {"text": text, "bird_id": bird["id"], "bird_name": bird["name"], "source": "Wikipedia",
            "source_url": bird["wiki_url"], "aab_url": bird["aab_url"], "ai": ai}

def build_fact_pool():
    """Download every bird's Wikipedia article, then let Gemini turn them into kid-sized facts (in 4 batches)."""
    global _fact_pool, _fact_pool_time
    if not _fact_lock.acquire(blocking=False):
        return  # another thread is already building it
    try:
        def safe_text(b):
            try:
                return fetch_wiki_text(b)
            except Exception as e:
                log.warning("Wikipedia fetch failed for %s: %s", b["name"], e)
                return ""
        with ThreadPoolExecutor(6) as ex:
            texts = dict(zip([b["id"] for b in TEXAS_BIRDS], ex.map(safe_text, TEXAS_BIRDS)))
        batches = [TEXAS_BIRDS[i:i + 8] for i in range(0, len(TEXAS_BIRDS), 8)]
        with ThreadPoolExecutor(len(batches)) as ex:
            facts = [f for batch_facts in ex.map(lambda b: _facts_from_gemini(b, texts), batches) for f in batch_facts]
        covered = {f["bird_id"] for f in facts}
        for b in TEXAS_BIRDS:  # any bird Gemini skipped still gets real sentences
            if b["id"] not in covered and texts.get(b["id"]):
                facts += _facts_from_text(b, texts[b["id"]])
        if facts:
            _fact_pool, _fact_pool_time = facts, time.time()
            log.info("Fact pool ready: %d facts (%d rewritten by Gemini).", len(facts), sum(f["ai"] for f in facts))
    finally:
        _fact_lock.release()

# ---- YouTube: hide any video that was deleted or can no longer be embedded ----
_video_ok = {}

def video_ok(video_id):
    if video_id not in _video_ok:
        try:
            r = requests.get("https://www.youtube.com/oembed", headers=HTTP_HEADERS, timeout=6,
                             params={"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"})
            _video_ok[video_id] = r.status_code == 200
        except requests.RequestException:
            return True  # can't check right now; show it and check again later
    return _video_ok[video_id]

def warm_caches():
    """Runs once in the background at startup so the first visitor doesn't wait."""
    try:
        north_texas_species()
    except Exception as e:
        log.warning("North Texas species list failed: %s", e)
    build_fact_pool()
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(lambda v: video_ok(v["video_id"]), SHOWTIME_VIDEOS + LIVE_CAMS))

# ==========================================
# 5. FRONTEND
# ==========================================
# A raw string, served as-is (not a Jinja template), so JavaScript can use any characters it likes.
WEB_PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ChirpQuest</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
:root { --teal-primary:#0f766e; --card-bg:#ffffff; --text-main:#1e293b; }
body { font-family:'Comic Sans MS',cursive,sans-serif; background:linear-gradient(135deg,#f0fdf4 0%,#e0f2fe 100%); margin:0; color:var(--text-main); min-height:100vh; display:flex; flex-direction:column; overflow-x:hidden; position:relative; }

/* ANIMATIONS */
@keyframes wingFlap { 0%,100%{transform:rotate(0deg);} 50%{transform:rotate(-12deg);} }
@keyframes wingBuzz { 0%,100%{transform:rotate(0deg);} 50%{transform:rotate(-28deg);} }
@keyframes blink { 0%,92%,100%{transform:scaleY(1);} 96%{transform:scaleY(0.1);} }
@keyframes owlSway { 0%,100%{transform:rotate(0deg);} 50%{transform:rotate(2.5deg);} }
@keyframes floatUpDown { 0%,100%{transform:translateY(0);} 50%{transform:translateY(-10px);} }
@keyframes hop { 0%,100%{transform:translateY(0);} 40%{transform:translateY(-5px);} 60%{transform:translateY(0);} }
@keyframes gentleBob { 0%,100%{transform:translateY(0) rotate(0deg);} 50%{transform:translateY(-6px) rotate(-1.5deg);} }
@keyframes popIn { 0%{transform:scale(0.7);opacity:0;} 60%{transform:scale(1.08);opacity:1;} 100%{transform:scale(1);} }
@keyframes shine { 0%{background-position:-150% 0;} 100%{background-position:250% 0;} }
@keyframes badgeGlow { 0%,100%{box-shadow:0 0 0 rgba(245,158,11,0);} 50%{box-shadow:0 0 24px rgba(245,158,11,0.55);} }
@keyframes confettiFall { 0%{transform:translateY(-20px) rotate(0deg);opacity:1;} 100%{transform:translateY(220px) rotate(360deg);opacity:0;} }
@keyframes livePulse { 0%,100%{opacity:1;} 50%{opacity:0.35;} }
@keyframes shimmer { 0%{background-position:-200px 0;} 100%{background-position:200px 0;} }

.mascot-svg { animation:gentleBob 3s ease-in-out infinite; transform-origin:center bottom; cursor:pointer; }
@keyframes crestSway { 0%,100%{transform:rotate(0deg);} 50%{transform:rotate(-6deg);} }
.mascot-crest { transform-box:fill-box; transform-origin:70% 100%; animation:crestSway 2.6s ease-in-out infinite; }
.mascot-wing { transform-box:fill-box; transform-origin:70% 20%; animation:wingFlap 1.3s ease-in-out infinite; }
.mascot-eye, .bird-blink { transform-box:fill-box; transform-origin:center; animation:blink 4s infinite; }

.bird-svg { animation:hop 3.2s ease-in-out infinite; transform-origin:center bottom; }
.cb-wing { transform-box:fill-box; transform-origin:70% 25%; animation:wingFlap 1.6s ease-in-out infinite; }
.cb-buzz { transform-box:fill-box; transform-origin:40% 95%; animation:wingBuzz 0.09s linear infinite; }
.owl-sway { transform-origin:60px 110px; animation:owlSway 3s ease-in-out infinite; }
.bird-page:hover .bird-svg { animation-duration:1.2s; }
@media (prefers-reduced-motion:reduce){ *{animation:none !important;} }

.emoji-icon { display:inline-block; animation:floatUpDown 2.6s ease-in-out infinite; }
.bg-emoji { position:fixed; font-size:28px; opacity:0.12; pointer-events:none; animation:floatUpDown 6s ease-in-out infinite; z-index:0; }

/* LAYOUT */
.app-layout { display:flex; flex:1; min-height:0; position:relative; z-index:1; }
.sidebar { width:240px; background:#0f766e; color:#fff; display:flex; flex-direction:column; box-shadow:4px 0 15px rgba(0,0,0,0.05); z-index:10; flex-shrink:0; }
.logo-area { padding:25px 20px; display:flex; align-items:center; gap:12px; border-bottom:1px solid rgba(255,255,255,0.1); }
.logo-badge { width:44px; height:44px; background:rgba(255,255,255,0.15); border-radius:14px; display:flex; align-items:center; justify-content:center; border:2px solid rgba(255,255,255,0.3); flex-shrink:0; }
.logo-badge svg { width:38px; height:38px; }
.logo-text-wrap h1 { font-size:1.4em; margin:0; letter-spacing:0.5px; color:#fff; }
.logo-text-wrap p { font-size:0.75em; margin:0; color:#99f6e4; }
.nav-links { padding:20px 15px; display:flex; flex-direction:column; gap:6px; flex:1; }
.nav-btn { background:transparent; border:none; color:#ccfbf1; padding:11px 16px; border-radius:12px; text-align:left; font-size:1em; font-weight:bold; cursor:pointer; transition:all 0.2s; display:flex; align-items:center; gap:12px; font-family:inherit; }
.nav-btn:hover { background:rgba(255,255,255,0.1); color:#fff; transform:translateX(4px); }
.nav-btn.active { background:#14b8a6; color:#fff; box-shadow:0 4px 12px rgba(20,184,166,0.3); }
.nav-new { font-size:0.62em; background:#f59e0b; color:#fff; border-radius:6px; padding:1px 5px; margin-left:auto; }

.main-content { flex:1; padding:30px; overflow-y:auto; display:flex; justify-content:center; align-items:flex-start; min-width:0; }
.content-container { width:100%; max-width:1100px; }
.tab-content { display:none; }
.tab-content.active { display:block; animation:popIn 0.35s ease-out; }
.box { background:var(--card-bg); padding:30px; border-radius:28px; box-shadow:0 10px 25px rgba(15,118,110,0.08); border:3px solid #ccfbf1; box-sizing:border-box; }
h2.tab-title { color:#0f766e; margin-top:0; }
.muted { color:#475569; }
.small { font-size:0.78em; color:#64748b; }
a { color:#0f766e; }
button { font-family:inherit; }

.mode-bar { display:flex; justify-content:flex-end; align-items:center; gap:8px; margin:-14px 0 10px; flex-wrap:wrap; }
.mode-switch { display:inline-flex; background:#fff; border:2px solid #99f6e4; border-radius:999px; padding:2px; }
.mode-switch button { border:none; background:transparent; padding:4px 11px; border-radius:999px; font-weight:bold; font-size:0.76em; color:#0f766e; cursor:pointer; }
.mode-switch button.on { background:#0f766e; color:#fff; }
.mascot-banner { display:flex; align-items:center; background:linear-gradient(135deg,#f0fdf4 0%,#ccfbf1 100%); border:3px solid #99f6e4; border-radius:22px; padding:20px 25px; margin-bottom:25px; gap:20px; }
.mascot-display { width:90px; height:100px; flex-shrink:0; }
.mascot-banner.holiday { background:linear-gradient(135deg,#fef3c7 0%,#fce7f3 55%,#e0f2fe 100%); border-color:#fbbf24; position:relative; overflow:hidden; }
.banner-photo { margin-left:auto; flex-shrink:0; text-align:center; max-width:170px; }
.banner-photo img { width:170px; height:120px; object-fit:cover; border-radius:16px; border:3px solid #fff; box-shadow:0 6px 14px rgba(0,0,0,0.15); display:block; animation:popIn 0.5s ease-out; }
.banner-photo .small { font-size:0.6em; margin-top:3px; }
@media (max-width:700px){ .mascot-banner { flex-wrap:wrap; } .banner-photo { margin:0 auto; } }

.welcome-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:15px; margin-top:20px; }
@media (min-width:1000px){ .span-2 { grid-column:span 2; } }
.card { background:#f8fafc; padding:18px 20px; border-radius:20px; border:2px solid #e2e8f0; transition:transform 0.25s; min-width:0; }
.card:hover { transform:translateY(-3px); }
.card h2 { margin-top:0; color:#0f766e; font-size:1.15em; display:flex; align-items:center; gap:8px; }
.card h2 .card-action { margin-left:auto; }
.facts-list { list-style:none; padding:0; margin:0; }
.facts-list li { padding:8px 10px; margin-bottom:6px; background:#fff; border:1px solid #e2e8f0; border-radius:12px; font-size:0.9em; color:#334155; animation:popIn 0.35s ease-out; }
.fact-src { display:block; font-size:0.72em; color:#64748b; margin-top:3px; }
.skeleton { height:34px; border-radius:12px; margin-bottom:6px; background:linear-gradient(90deg,#f1f5f9 0%,#e2e8f0 50%,#f1f5f9 100%); background-size:400px 100%; animation:shimmer 1.2s linear infinite; }
.mini-btn { background:#f0fdfa; color:#0f766e; border:2px solid #99f6e4; border-radius:10px; padding:4px 10px; font-size:0.72em; font-weight:bold; cursor:pointer; }
.mini-btn:hover { background:#ccfbf1; }
.daily-art { width:130px; height:130px; margin:0 auto; display:block; }
.daily-art img { width:100%; height:100%; object-fit:cover; border-radius:18px; border:3px solid #fff; box-shadow:0 4px 10px rgba(0,0,0,0.12); animation:popIn 0.4s ease-out; }
.center { text-align:center; }
#spectrogram { width:100%; height:90px; background:#0f172a; border-radius:12px; display:block; margin-top:6px; }
.weather-big { font-size:1.9em; font-weight:bold; color:#0f766e; }
.meter { background:#e2e8f0; border-radius:10px; height:12px; overflow:hidden; margin:8px 0; }
.meter > div { height:100%; border-radius:10px; transition:width 0.8s ease; }

/* MAP */
.map-wrap { margin-top:20px; }
.map-controls { display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin-bottom:10px; }
.chip { background:#f0fdfa; border:2px solid #99f6e4; color:#0f766e; border-radius:999px; padding:6px 12px; font-weight:bold; cursor:pointer; font-size:0.85em; }
.chip.on { background:#0f766e; border-color:#0f766e; color:#fff; }
.map-grid { display:grid; grid-template-columns:minmax(0,1fr) 260px; gap:15px; }
@media (max-width:900px){ .map-grid { grid-template-columns:1fr; } }
#bird-map { height:400px; border-radius:18px; border:3px solid #ccfbf1; z-index:1; }
.top-list { list-style:none; margin:0; padding:0; }
.top-list li { margin-bottom:9px; font-size:0.86em; }
.top-bar { height:10px; border-radius:6px; background:#5eead4; margin-top:3px; transition:width 0.6s ease; }
.top-list li.book .top-bar { background:#f59e0b; }
.leaflet-marker-icon { filter:drop-shadow(0 2px 2px rgba(0,0,0,0.3)); }
.map-popup img { width:150px; height:110px; object-fit:cover; border-radius:8px; display:block; margin-bottom:4px; }
.map-popup { font-family:'Comic Sans MS',cursive,sans-serif; }

/* BIRD BOOK */
.book-tools { display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin-top:10px; }
.search-input { flex:1; min-width:200px; padding:10px 14px; border-radius:12px; border:3px solid #99f6e4; font-size:0.95em; font-family:inherit; outline:none; }
.book-container { display:flex; flex-wrap:wrap; gap:18px; justify-content:center; margin-top:18px; }
.bird-page { background:#fff; border:3px solid #e2e8f0; border-radius:22px; padding:14px; width:230px; text-align:center; box-shadow:0 6px 12px rgba(0,0,0,0.03); transition:transform 0.2s,border-color 0.2s; }
.bird-page:hover { transform:translateY(-6px) scale(1.02); border-color:#14b8a6; }
.bird-page.spotted { border-color:#22c55e; }
.bird-stage { height:150px; background:linear-gradient(180deg,#dbeafe 0%,#f0fdf4 60%,#dcfce7 100%); border-radius:16px; border:2px solid #ccfbf1; position:relative; display:flex; justify-content:center; align-items:center; overflow:hidden; cursor:pointer; }
.bird-photo { width:100%; height:100%; object-fit:cover; border-radius:14px; display:none; }
.bird-photo.loaded { display:block; animation:popIn 0.4s ease-out; }
.photo-tag { position:absolute; bottom:4px; right:6px; font-size:0.6em; color:#fff; background:rgba(0,0,0,0.45); padding:1px 5px; border-radius:6px; }
.bird-sprite-container { width:135px; height:135px; display:inline-block; }
.bird-sprite-container svg, .daily-art svg { width:100%; height:100%; }
.bird-name-row { display:flex; align-items:center; justify-content:center; gap:6px; margin:4px 0 10px 0; color:#0f766e; font-size:1.02em; }
.field-marks { text-align:left; background:#f8fafc; padding:8px 10px; border-radius:12px; border:1px solid #e2e8f0; margin-top:10px; font-size:0.8em; }
.field-marks ul { margin:4px 0 0 0; padding-left:16px; color:#475569; }
.card-buttons { display:flex; gap:6px; justify-content:center; margin-top:8px; flex-wrap:wrap; }
.season { margin-top:8px; font-size:0.72em; color:#475569; min-height:58px; }
.season svg { width:100%; height:44px; display:block; }

/* CHECKLIST */
.checklist-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:12px; margin-top:20px; }
.check-item { background:#f8fafc; border:2px solid #e2e8f0; padding:12px 14px; border-radius:14px; display:flex; align-items:center; gap:12px; font-weight:bold; cursor:pointer; transition:all 0.2s; color:#334155; }
.check-item:hover { background:#f0fdf4; border-color:#14b8a6; color:#0f766e; }
.check-item input { width:20px; height:20px; accent-color:#0f766e; cursor:pointer; }
.check-item.checked { background:#dcfce7; border-color:#22c55e; }
.progress-bar-outer { background:#e2e8f0; border-radius:10px; height:14px; margin-top:20px; overflow:hidden; }
.progress-bar-inner { background:linear-gradient(90deg,#14b8a6,#22c55e,#14b8a6); background-size:200% 100%; height:100%; border-radius:10px; animation:shine 2.5s linear infinite; transition:width 0.6s ease; }

/* CHAT */
.chat-box { display:flex; flex-direction:column; height:380px; border:3px solid #e2e8f0; border-radius:20px; background:#f8fafc; padding:20px; overflow-y:auto; gap:12px; }
.chat-msg { padding:12px 18px; border-radius:16px; max-width:75%; font-weight:bold; font-size:0.95em; animation:popIn 0.25s ease-out; white-space:pre-wrap; }
.bot-msg { background:#e0f2fe; color:#0369a1; border:2px solid #bae6fd; align-self:flex-start; }
.user-msg { background:#dcfce7; color:#15803d; border:2px solid #bbf7d0; align-self:flex-end; }
.typing-msg { background:#e0f2fe; color:#0369a1; border:2px solid #bae6fd; align-self:flex-start; padding:12px 18px; border-radius:16px; }
.typing-dot { display:inline-block; width:6px; height:6px; background:#0369a1; border-radius:50%; margin-right:3px; animation:floatUpDown 0.8s infinite; }
.typing-dot:nth-child(2){animation-delay:0.15s;} .typing-dot:nth-child(3){animation-delay:0.3s;}
.chat-controls { display:flex; gap:10px; margin-top:15px; }
.chat-input { flex:1; padding:14px 18px; border-radius:14px; border:3px solid #14b8a6; font-size:1em; font-family:inherit; outline:none; background:#fff; min-width:0; }
.chat-input:focus { box-shadow:0 0 0 3px rgba(20,184,166,0.2); }
.chat-send-btn, .big-btn { background:#0f766e; color:#fff; border:none; padding:14px 26px; border-radius:14px; font-weight:bold; font-size:1em; cursor:pointer; transition:background 0.2s,transform 0.1s; }
.chat-send-btn:hover, .big-btn:hover { background:#115e59; transform:scale(1.04); }
.chat-send-btn:disabled, .big-btn:disabled { opacity:0.5; cursor:not-allowed; transform:none; }
.big-btn.alt { background:#0ea5e9; } .big-btn.alt:hover { background:#0284c7; }
.big-btn.warm { background:#f59e0b; } .big-btn.warm:hover { background:#d97706; }
.chat-suggest { display:flex; gap:6px; flex-wrap:wrap; margin-top:10px; }

.sound-btn { background:#0ea5e9; color:#fff; border:none; padding:9px 16px; border-radius:12px; font-weight:bold; cursor:pointer; margin-top:10px; transition:background 0.2s,transform 0.1s; }
.sound-btn:hover { background:#0284c7; transform:scale(1.05); }

/* PHOTO ID */
.id-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:20px; margin-top:20px; }
.drop-zone { border:3px dashed #5eead4; border-radius:20px; background:#f0fdfa; min-height:260px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:10px; padding:16px; text-align:center; cursor:pointer; transition:background 0.2s; }
.drop-zone.drag { background:#ccfbf1; }
.drop-zone img { max-width:100%; max-height:300px; border-radius:14px; display:none; }
.id-result { background:#f8fafc; border:3px solid #e2e8f0; border-radius:20px; padding:20px; min-height:260px; }
.id-result h3 { margin-top:0; color:#0f766e; }

/* QUIZ */
.quiz-modes { display:flex; gap:10px; flex-wrap:wrap; margin-top:15px; }
.quiz-stage { margin-top:20px; background:#f8fafc; border:3px solid #e2e8f0; border-radius:22px; padding:20px; text-align:center; min-height:300px; }
.quiz-hud { display:flex; justify-content:space-between; font-weight:bold; color:#0f766e; margin-bottom:12px; flex-wrap:wrap; gap:6px; }
.quiz-picture { height:240px; display:flex; align-items:center; justify-content:center; }
.quiz-picture img { max-height:240px; max-width:100%; border-radius:16px; }
.quiz-picture .bird-svg { width:220px; height:220px; }
.quiz-choices { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:10px; margin-top:16px; }
.choice { background:#fff; border:3px solid #cbd5e1; border-radius:14px; padding:12px; font-weight:bold; font-size:0.95em; cursor:pointer; transition:all 0.15s; color:#334155; }
.choice:hover:not(:disabled) { border-color:#14b8a6; transform:translateY(-2px); }
.choice.right { background:#dcfce7; border-color:#22c55e; color:#15803d; }
.choice.wrong { background:#fee2e2; border-color:#ef4444; color:#b91c1c; }

/* PUZZLE */
.puzzle-layout { display:grid; grid-template-columns:minmax(0,440px) minmax(0,1fr); gap:20px; margin-top:15px; align-items:start; }
@media (max-width:900px){ .puzzle-layout { grid-template-columns:1fr; } }
#puzzle-board { width:100%; max-width:440px; aspect-ratio:1; border-radius:18px; border:4px solid #99f6e4; background:#f0fdfa; cursor:pointer; touch-action:manipulation; display:block; }
.puzzle-side { background:#f8fafc; border:3px solid #e2e8f0; border-radius:20px; padding:18px; }
.puzzle-stats { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; text-align:center; margin:10px 0; }
.puzzle-stats div { background:#fff; border:2px solid #e2e8f0; border-radius:12px; padding:8px 4px; font-size:0.8em; color:#64748b; }
.puzzle-stats b { display:block; font-size:1.5em; color:#0f766e; }

#now-playing { position:fixed; right:16px; bottom:16px; max-width:min(420px, calc(100vw - 32px)); background:#0f172a; color:#e2e8f0; font-size:0.78em; padding:8px 12px; border-radius:12px; box-shadow:0 6px 18px rgba(0,0,0,0.25); opacity:0; transform:translateY(10px); transition:opacity 0.3s, transform 0.3s; pointer-events:none; z-index:50; }
#now-playing.show { opacity:0.95; transform:none; }

/* DRAW BIRDS */
.draw-steps { display:grid; grid-template-columns:repeat(auto-fill,minmax(165px,1fr)); gap:14px; margin-top:16px; }
.draw-step { background:#fff; border:3px solid #e2e8f0; border-radius:18px; padding:10px; text-align:center; position:relative; }
.draw-step.final { border-color:#f59e0b; background:#fffbeb; }
.draw-step svg { width:100%; height:auto; aspect-ratio:1; }
.draw-step, .draw-step * { animation:none !important; }
.draw-num { position:absolute; top:8px; left:10px; background:#0f766e; color:#fff; width:26px; height:26px; border-radius:50%; font-weight:bold; line-height:26px; }
.draw-step p { margin:4px 0 0; font-size:0.84em; color:#334155; }
.sketch * { fill:none !important; stroke:#cbd5e1 !important; stroke-width:2 !important; opacity:1 !important; }
.sketch .new-part, .sketch .new-part * { stroke:#0ea5e9 !important; stroke-width:3 !important; }

/* SHOWTIME */
.live-card { background:#0f172a; border-radius:22px; padding:14px; margin-top:18px; }
.live-title { color:#fff; font-weight:bold; margin:10px 4px 2px; display:flex; align-items:center; gap:8px; }
.live-dot { background:#ef4444; color:#fff; font-size:0.75em; padding:2px 8px; border-radius:6px; animation:livePulse 1.4s ease-in-out infinite; }
.video-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:20px; margin-top:20px; }
.video-card { background:#f8fafc; border:3px solid #e2e8f0; border-radius:20px; padding:14px; transition:transform 0.2s,border-color 0.2s; }
.video-card:hover { transform:translateY(-4px); border-color:#14b8a6; }
.video-frame-wrap { position:relative; width:100%; padding-top:56.25%; border-radius:14px; overflow:hidden; background:#000; }
.video-frame-wrap iframe { position:absolute; top:0; left:0; width:100%; height:100%; border:0; }
.video-title { margin:10px 0 0 0; color:#0f766e; font-weight:bold; font-size:0.95em; display:flex; align-items:center; gap:6px; }

/* PRIZES */
.badge-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:18px; margin-top:20px; }
.badge-card { background:#f8fafc; border:3px solid #e2e8f0; border-radius:20px; padding:20px 14px; text-align:center; transition:transform 0.25s; position:relative; overflow:hidden; }
.badge-card.unlocked { border-color:var(--badge-color,#f59e0b); animation:badgeGlow 2.4s ease-in-out infinite; }
.badge-card.unlocked:hover { transform:translateY(-6px) scale(1.03); }
.badge-emoji { font-size:2.6em; display:block; margin-bottom:8px; filter:grayscale(1); opacity:0.4; }
.badge-card.unlocked .badge-emoji { filter:none; opacity:1; animation:popIn 0.5s ease-out; }
.badge-name { font-weight:bold; color:#334155; }
.badge-card.unlocked .badge-name { color:#0f766e; }
.badge-progress { font-size:0.8em; color:#64748b; margin-top:6px; }
.confetti-piece { position:absolute; width:8px; height:8px; top:0; animation:confettiFall 1.4s ease-in forwards; border-radius:2px; pointer-events:none; }

@media (max-width:768px){
  .app-layout{flex-direction:column;} .sidebar{width:100%;height:auto;}
  .nav-links{flex-direction:row;flex-wrap:wrap;justify-content:center;} .nav-new{display:none;}
  .main-content{padding:14px;} .box{padding:18px;}
}
</style>
</head>
<body>
<div id="now-playing" role="status"></div>
<div class="bg-emoji" style="top:8%;left:4%;">🍃</div>
<div class="bg-emoji" style="top:70%;left:90%;animation-delay:1.2s;">🍃</div>
<div class="bg-emoji" style="top:40%;left:96%;animation-delay:2.4s;">☁️</div>

<div class="app-layout">
    <aside class="sidebar">
        <div class="logo-area">
            <div class="logo-badge">__LOGO__</div>
            <div class="logo-text-wrap"><h1>ChirpQuest</h1><p>North Texas Bird Guide</p></div>
        </div>
        <nav class="nav-links">
            <button class="nav-btn active" data-tab="welcome"><span class="emoji-icon">🏠</span> Welcome</button>
            <button class="nav-btn" data-tab="chat"><span class="emoji-icon">💬</span> Ask Pip</button>
            <button class="nav-btn" data-tab="book"><span class="emoji-icon">📖</span> Bird Book</button>
            <button class="nav-btn" data-tab="photoid"><span class="emoji-icon">📷</span> Photo ID <span class="nav-new">NEW</span></button>
            <button class="nav-btn" data-tab="quiz"><span class="emoji-icon">🎯</span> Bird Quiz <span class="nav-new">NEW</span></button>
            <button class="nav-btn" data-tab="puzzle"><span class="emoji-icon">🧩</span> Bird Puzzle <span class="nav-new">NEW</span></button>
            <button class="nav-btn" data-tab="draw"><span class="emoji-icon">✏️</span> Draw Birds <span class="nav-new">NEW</span></button>
            <button class="nav-btn" data-tab="checklist"><span class="emoji-icon">✅</span> Checklist</button>
            <button class="nav-btn" data-tab="showtime"><span class="emoji-icon">📺</span> Showtime</button>
            <button class="nav-btn" data-tab="prizes"><span class="emoji-icon">🏆</span> Prizes</button>
        </nav>
    </aside>

    <main class="main-content">
        <div class="content-container">
            <div class="mode-bar">
                <span class="small" id="mode-note"></span>
                <div class="mode-switch" role="group" aria-label="Website mode">
                    <button data-mode="demo" title="Badges & Bird of the Day reset every time you refresh">🎬 Demo</button>
                    <button data-mode="normal" title="Progress is saved; Bird of the Day changes daily">💾 Normal</button>
                </div>
            </div>
            <!-- WELCOME -->
            <section id="tab-welcome" class="tab-content active">
                <div class="box">
                    <div class="mascot-banner" id="banner">
                        <div class="mascot-display" id="mascot-container" title="Click Pip!"></div>
                        <div style="min-width:0;">
                            <h2 id="banner-title" style="margin:0 0 5px 0;color:#0f766e;">Meet Pip the Cockatiel!</h2>
                            <p id="banner-text" style="margin:0;color:#334155;font-size:0.95em;">Your official ChirpQuest guide. Ask Pip anything in the Ask Pip tab, or snap a bird photo in Photo ID! (Psst… click Pip.)</p>
                            <p id="banner-next" class="small" style="margin:6px 0 0;"></p>
                        </div>
                        <div class="banner-photo" id="banner-photo"></div>
                    </div>
                    <h1 style="color:#0f766e;margin-top:0;">Welcome to ChirpQuest! 🐦</h1>
                    <p class="muted">Explore <b id="bird-count">32</b> North Texas birds with real photos, live sightings, cartoons, games and an AI bird buddy.</p>

                    <div class="welcome-grid">
                        <div class="card span-2">
                            <h2>📚 Bird Facts <button class="mini-btn card-action" onclick="loadFacts()">🔄 New facts</button></h2>
                            <ul id="facts-list" class="facts-list"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div></ul>
                            <p class="small" style="margin:6px 0 0;">Real facts from Wikipedia, rewritten for kids by Pip ✨. Tap "All About Birds" to read more at the Cornell Lab.</p>
                        </div>
                        <div class="card center">
                            <h2>🐦 Bird of the Day</h2>
                            <div id="daily-art" class="daily-art"></div>
                            <p id="daily-bird" style="font-weight:bold;font-size:1.05em;color:#0f766e;margin:6px 0 0;">Loading...</p>
                            <p id="daily-extra" class="small" style="margin:2px 0 0;"></p>
                            <div class="card-buttons">
                                <button class="sound-btn" id="daily-ask" onclick="askAboutDailyBird()">💬 Ask Pip about it</button>
                                <button class="sound-btn" id="daily-hear" onclick="hearDailyBird()">🔊 Hear it</button>
                            </div>
                        </div>
                        <div class="card span-2">
                            <h2>🔊 Bird Sounds <span class="small" style="margin-left:auto;">a live spectrogram, like Merlin's</span></h2>
                            <canvas id="spectrogram" width="600" height="90"></canvas>
                            <p id="sound-bird-name" style="font-weight:bold;margin:8px 0 0;color:#0f766e;">Press play to see a call as a picture!</p>
                            <button class="sound-btn" onclick="playRandomBirdCall()">Play a Random Bird 🎵</button>
                            <p class="small" id="sound-credit" style="margin:6px 0 0;">Real bird recordings shared by iNaturalist users — a different one each time you play.</p>
                        </div>
                        <div class="card">
                            <h2>🌤️ Birding Weather</h2>
                            <div id="weather-box" class="muted">Checking the sky…</div>
                        </div>
                    </div>

                    <div class="card map-wrap">
                        <h2>🗺️ Live Bird Map <span class="small" style="margin-left:auto;" id="map-status">loading sightings…</span></h2>
                        <div class="map-controls">
                            <button class="chip" data-days="1">Today</button>
                            <button class="chip on" data-days="7">This week</button>
                            <button class="chip" data-days="30">This month</button>
                            <button class="chip" id="book-only-chip">⭐ Bird Book birds only</button>
                            <button class="chip" id="near-me-chip">📍 Near me</button>
                        </div>
                        <div class="map-grid">
                            <div id="bird-map"></div>
                            <div>
                                <h3 style="margin:0 0 8px;color:#0f766e;font-size:1em;">🏅 Most-seen birds</h3>
                                <ul class="top-list" id="top-list"><div class="skeleton"></div><div class="skeleton"></div></ul>
                                <p class="small">📍 Pins with a bird face are Bird Book birds; gray <b>?</b> pins are other birds. Tap any pin to see the photo. ⭐ Orange bars = in your Bird Book. Every pin is a real sighting someone photographed and shared on iNaturalist.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- ASK PIP -->
            <section id="tab-chat" class="tab-content">
                <div class="box">
                    <h2 class="tab-title">💬 Chat with Pip</h2>
                    <div class="chat-box" id="chat-container">
                        <div class="chat-msg bot-msg">Chirp chirp! I'm Pip the Cockatiel! Ask me anything about North Texas birds!</div>
                    </div>
                    <div class="chat-suggest">
                        <button class="mini-btn" onclick="askPip('Why do birds migrate?')">Why do birds migrate?</button>
                        <button class="mini-btn" onclick="askPip('How can I attract hummingbirds to my yard?')">Attract hummingbirds?</button>
                        <button class="mini-btn" onclick="askPip('Which North Texas bird is the fastest?')">Fastest bird?</button>
                        <button class="mini-btn" onclick="askPip('How do owls see at night?')">Owl night vision?</button>
                    </div>
                    <div class="chat-controls">
                        <input type="text" id="user-input" class="chat-input" placeholder="Type your bird question here..." onkeydown="if(event.key==='Enter') sendChatMessage()">
                        <button class="chat-send-btn" id="send-btn" type="button" onclick="sendChatMessage()">Send</button>
                    </div>
                </div>
            </section>

            <!-- BIRD BOOK -->
            <section id="tab-book" class="tab-content">
                <div class="box">
                    <h2 class="tab-title">📖 North Texas Field Guide (<span class="bird-total">32</span> Species)</h2>
                    <p class="muted">Cartoon drawings with real Creative-Commons photos. Tap a picture to switch between them. 📅 shows the months people spot each bird in Texas.</p>
                    <div class="book-tools">
                        <input id="book-search" class="search-input" placeholder="🔍 Search birds… (try 'red' or 'owl')">
                        <button class="chip on" data-habitat="all">All</button>
                        <button class="chip" data-habitat="backyard">🏡 Backyard</button>
                        <button class="chip" data-habitat="water">💧 Water</button>
                        <button class="chip" data-habitat="open">🌾 Fields & Sky</button>
                        <button class="chip" data-habitat="night">🌙 Night</button>
                    </div>
                    <div class="book-container" id="bird-grid"></div>
                </div>
            </section>

            <!-- PHOTO ID -->
            <section id="tab-photoid" class="tab-content">
                <div class="box">
                    <h2 class="tab-title">📷 Pip's Photo ID</h2>
                    <p class="muted">Took a bird picture, or drew one? Pip uses Google Gemini AI to guess which bird it is (any bird, not just the Bird Book), just like Merlin's Photo ID. Your picture is shrunk first and is only sent to Gemini to ask.</p>
                    <div class="quiz-modes" style="align-items:center;">
                        <b style="color:#0f766e;">This picture is:</b>
                        <button class="chip on" data-id-kind="bird">📷 A real bird</button>
                        <button class="chip" data-id-kind="drawing">✏️ My drawing</button>
                        <button class="chip" data-id-kind="other">❓ Something else</button>
                    </div>
                    <div class="id-grid">
                        <label class="drop-zone" id="drop-zone">
                            <input type="file" id="photo-input" accept="image/*" style="display:none">
                            <span style="font-size:3em;" id="drop-emoji">📸</span>
                            <b id="drop-text">Tap to choose a photo, or drop one here</b>
                            <img id="id-preview" alt="Your bird photo">
                        </label>
                        <div class="id-result" id="id-result">
                            <h3>How it works</h3>
                            <ol class="muted" style="font-size:0.9em;padding-left:18px;">
                                <li>Choose what kind of picture it is: a real bird, your drawing, or something else.</li>
                                <li>Pick a picture (or try a sample) and press <b>Identify!</b></li>
                                <li>Pip tells you the bird and the clues it used. For drawings, you get a "looks-like" score. Every different Bird Book bird you draw that scores 60+ counts toward the 🎨 Master Artist badge!</li>
                            </ol>
                        </div>
                    </div>
                    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:15px;">
                        <button class="big-btn" id="identify-btn" onclick="identifyPhoto()" disabled>🔍 Identify!</button>
                        <button class="big-btn alt" id="sample-btn" onclick="loadSamplePhoto()">🎲 Try a sample photo</button>
                    </div>
                </div>
            </section>

            <!-- QUIZ -->
            <section id="tab-quiz" class="tab-content">
                <div class="box">
                    <h2 class="tab-title">🎯 Bird Quiz</h2>
                    <p class="muted">10 questions. Can you name the bird? Best score so far: <b id="quiz-best">0</b>/10</p>
                    <div class="quiz-modes">
                        <button class="big-btn" onclick="startQuiz('photo')">📸 Real Photos</button>
                        <button class="big-btn warm" onclick="startQuiz('cartoon')">🎨 Cartoons</button>
                        <button class="big-btn alt" onclick="startQuiz('sound')">🔊 Sounds</button>
                    </div>
                    <div class="quiz-stage" id="quiz-stage">
                        <p style="font-size:3em;margin:20px 0 0;">🐦❓</p>
                        <p class="muted">Pick a mode to start!</p>
                    </div>
                </div>
            </section>

            <!-- PUZZLE -->
            <section id="tab-puzzle" class="tab-content">
                <div class="box">
                    <h2 class="tab-title">🧩 Mystery Bird Puzzle</h2>
                    <p class="muted">A bird picture got scrambled! Tap two tiles to swap them. Put every tile back to reveal the mystery bird. Solve 5 to earn the 🧩 <b>Puzzle Pro</b> badge. Puzzles solved: <b id="puzzle-solved-count">0</b></p>
                    <div class="quiz-modes">
                        <button class="chip on" data-pz-pic="photo">📸 Real photo</button>
                        <button class="chip" data-pz-pic="cartoon">🎨 Cartoon</button>
                        <span style="width:10px;"></span>
                        <button class="chip on" data-pz-size="3">Easy 3×3</button>
                        <button class="chip" data-pz-size="4">Medium 4×4</button>
                        <button class="chip" data-pz-size="5">Hard 5×5</button>
                    </div>
                    <div class="puzzle-layout">
                        <canvas id="puzzle-board" width="600" height="600" aria-label="Bird puzzle board"></canvas>
                        <div class="puzzle-side">
                            <h3 style="margin:0;color:#0f766e;" id="puzzle-title">Who is the mystery bird? 🤔</h3>
                            <div class="puzzle-stats">
                                <div><b id="pz-moves">0</b>swaps</div>
                                <div><b id="pz-time">0:00</b>time</div>
                                <div><b id="pz-place">0/9</b>in place</div>
                            </div>
                            <div style="display:flex;gap:8px;flex-wrap:wrap;">
                                <button class="big-btn" onclick="newPuzzle()">🧩 New puzzle</button>
                                <button class="big-btn alt" id="pz-peek" onpointerdown="peekPuzzle(true)" onpointerup="peekPuzzle(false)" onpointerleave="peekPuzzle(false)">👀 Hold to peek</button>
                            </div>
                            <div id="puzzle-message" class="muted" style="margin-top:12px;">Tip: tiles that are in the right spot get a green check ✅.</div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- DRAW BIRDS -->
            <section id="tab-draw" class="tab-content">
                <div class="box">
                    <h2 class="tab-title">✏️ How to Draw Birds</h2>
                    <p class="muted">Draw any Bird Book bird in a few easy steps, using ChirpQuest's cartoons as your guide. The <b style="color:#0ea5e9;">blue lines</b> show what to draw next. When you finish, take a photo of your drawing and send it to <b>Photo ID → ✏️ My drawing</b>. Every different bird that scores 60+ counts toward the 🎨 <b>Master Artist</b> badge.</p>
                    <div class="book-tools">
                        <select id="draw-pick" class="search-input" style="flex:0 1 300px;" onchange="renderDrawGuide(this.value)"></select>
                        <button class="big-btn alt" onclick="pickRandomDrawing()">🎲 Random bird</button>
                        <button class="big-btn" onclick="openTab('photoid'); setIdKind('drawing');">📸 Check my drawing</button>
                    </div>
                    <div class="draw-steps" id="draw-steps"></div>
                    <p class="muted" style="margin-top:16px;">🎨 Master Artist: <b id="art-count">0</b>/10 different birds drawn <span id="art-gallery" class="small"></span></p>
                </div>
            </section>

            <!-- CHECKLIST -->
            <section id="tab-checklist" class="tab-content">
                <div class="box">
                    <h2 class="tab-title">✅ North Texas Bird Log & Checklist</h2>
                    <p class="muted">Check off every bird as you spot them outdoors! <b id="checklist-count">0</b> / <span class="bird-total">32</span> spotted.</p>
                    <div class="progress-bar-outer"><div class="progress-bar-inner" id="checklist-progress-bar" style="width:0%;"></div></div>
                    <div class="checklist-grid" id="checklist-container"></div>
                </div>
            </section>

            <!-- SHOWTIME -->
            <section id="tab-showtime" class="tab-content">
                <div class="box">
                    <h2 class="tab-title" style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">📺 Showtime: Bird Videos
                        <button class="mini-btn" style="margin-left:auto;font-size:0.6em;" onclick="loadVideos()">🔀 Shuffle videos</button></h2>
                    <p class="muted">A new mix of bird videos from the Cornell Lab and Nat Geo Kids every time you visit, plus a live bird cam!</p>
                    <div id="live-cam"></div>
                    <div class="video-grid" id="video-grid"></div>
                </div>
            </section>

            <!-- PRIZES -->
            <section id="tab-prizes" class="tab-content">
                <div class="box">
                    <h2 class="tab-title">🏆 Prizes & Badges</h2>
                    <p class="muted">Unlock badges by spotting birds, acing the quiz, and solving a Photo ID!</p>
                    <div class="badge-grid" id="badge-grid"></div>
                </div>
            </section>
        </div>
    </main>
</div>

<script>
// ---------- helpers ----------
const $ = id => document.getElementById(id);
function esc(s){ return String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c]); }
function shuffle(a){ a=[...a]; for(let i=a.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [a[i],a[j]]=[a[j],a[i]]; } return a; }
function store(key, fallback){ try{ const v=localStorage.getItem(key); return v===null?fallback:JSON.parse(v); }catch(e){ return fallback; } }
function save(key, value){ try{ localStorage.setItem(key, JSON.stringify(value)); }catch(e){} }
let artCounter=0;
function birdArt(bird){ return bird.svg.replaceAll("__UID__", "u"+(++artCounter)); }  // unique clip-path ids per drawing

let allBirds=[], birdById={}, dailyBird=null, dailyPick={};
// 🎬 Demo mode: every page refresh is a fresh start — badges, checklist, quiz, Photo ID and puzzle progress
//    reset and a random Bird of the Day is picked. Demo progress is kept apart, so it never touches Normal progress.
// 💾 Normal mode: progress is saved (until there are accounts), and Bird of the Day changes once a day.
let mode=store("chirpquest_mode", "demo");
const MODE_NOTES={demo:"Demo: badges & Bird of the Day reset every time you refresh",
                  normal:"Normal: your progress is saved · new Bird of the Day every day"};
const PROGRESS=["checked","quiz_best","photo_ids","puzzles","art"];
const pkey=name=>(mode==="demo" ? "chirpquest_demo_" : "chirpquest_")+name;  // separate saves per mode
let checkedSet, quizBest, photoIds, puzzlesSolved, artSet;  // artSet = Bird Book birds drawn well (Master Artist)
function loadProgress(){
    checkedSet=new Set(store(pkey("checked"), []));
    quizBest=store(pkey("quiz_best"), 0); photoIds=store(pkey("photo_ids"), 0); puzzlesSolved=store(pkey("puzzles"), 0);
    artSet=new Set(store(pkey("art"), []));
}
function clearDemoProgress(){
    PROGRESS.forEach(n=>{ try{ localStorage.removeItem("chirpquest_demo_"+n); }catch(e){} });
    try{ sessionStorage.clear(); }catch(e){}
}
function startProgress(){
    clearDemoProgress();  // runs on every page load, so a refresh restarts the demo
    loadProgress();
}
function renderModeSwitch(){
    document.querySelectorAll(".mode-switch button").forEach(b=>b.classList.toggle("on", b.dataset.mode===mode));
    $("mode-note").textContent=MODE_NOTES[mode];
}
function setMode(m){
    if(m===mode) return;
    mode=m; save("chirpquest_mode", m);
    if(m==="demo") clearDemoProgress();
    loadProgress(); renderModeSwitch(); showDailyBird();
    // show the other mode's progress everywhere
    if(allBirds.length){ renderChecklist(); allBirds.forEach(b=>$("card-"+b.id)?.classList.toggle("spotted",checkedSet.has(b.id))); }
    $("quiz-best").textContent=quizBest; $("puzzle-solved-count").textContent=puzzlesSolved; updateArtCount();
    if($("tab-prizes").classList.contains("active")) renderBadges();
}
// Bird of the Day: any of ~320 North Texas birds (not only the Bird Book). Normal = same bird all day,
// Demo = new on every refresh. Each mode's pick is remembered while the page is open.
async function showDailyBird(){
    try{
        if(!dailyPick[mode]) dailyPick[mode]=await (await fetch("/api/bird_of_the_day?mode="+mode)).json();
    }catch(e){ $("daily-bird").textContent="Couldn't pick a bird right now."; return; }
    const b=dailyPick[mode];
    dailyBird=b.bird_id ? birdById[b.bird_id] : null;  // in the Bird Book? then it has a cartoon + call
    $("daily-art").innerHTML = b.photo ? `<img src="${esc(b.photo)}" alt="${esc(b.name)}">` : (dailyBird ? birdArt(dailyBird) : "🐦");
    $("daily-bird").textContent=`${dailyBird?dailyBird.emoji+" ":""}${b.name}`;
    $("daily-extra").innerHTML=`<i>${esc(b.sci)}</i>`
        + (b.count ? ` · seen ${b.count.toLocaleString()} times near DFW` : "")
        + (dailyBird ? " · ⭐ in your Bird Book" : "")
        + (b.wiki ? ` · <a href="${esc(b.wiki)}" target="_blank" rel="noopener">Wikipedia</a>` : "")
        + (b.credit ? `<br><span style="font-size:0.85em;">📷 ${esc(b.credit)}</span>` : "");
}
function hearDailyBird(){  // works for any bird, even ones not in the Bird Book
    const b=dailyPick[mode]; if(!b) return;
    $("sound-bird-name").textContent=`${dailyBird?dailyBird.emoji+" ":"🐦 "}${b.name}`;
    playBirdCall(dailyBird || {taxon_id:b.taxon_id, name:b.name});
}
function askAboutDailyBird(){
    const b=dailyPick[mode]; if(!b) return;
    openTab("chat"); askPip(`Tell me about the ${b.name}! Where can I see one in North Texas?`);
}
document.querySelectorAll(".mode-switch button").forEach(b=>b.addEventListener("click",()=>setMode(b.dataset.mode)));
loadProgress();

// ---------- tabs ----------
document.querySelectorAll(".nav-btn").forEach(btn => btn.addEventListener("click", () => openTab(btn.dataset.tab)));
function openTab(name){
    document.querySelectorAll(".tab-content").forEach(c=>c.classList.remove("active"));
    document.querySelectorAll(".nav-btn").forEach(b=>b.classList.toggle("active", b.dataset.tab===name));
    $("tab-"+name).classList.add("active");
    history.replaceState(null, "", name==="welcome" ? location.pathname : "#"+name);  // shareable links like /#quiz
    if(name==="chat") setTimeout(()=>$("user-input")?.focus(),100);
    if(name==="prizes") renderBadges();
    if(name==="puzzle" && !pz) newPuzzle();
    if(name==="welcome" && birdMap) setTimeout(()=>birdMap.invalidateSize(),50);
}

// ---------- sound engine (Web Audio) + spectrogram ----------
let audioCtx=null, master=null, analyser=null, noiseBuf=null;
function getAudio(){
    if(!audioCtx){
        audioCtx=new (window.AudioContext||window.webkitAudioContext)();
        master=audioCtx.createGain(); master.gain.value=0.35;
        analyser=audioCtx.createAnalyser(); analyser.fftSize=1024; analyser.smoothingTimeConstant=0.2;
        master.connect(analyser); analyser.connect(audioCtx.destination);
        noiseBuf=audioCtx.createBuffer(1, audioCtx.sampleRate*2, audioCtx.sampleRate);
        const d=noiseBuf.getChannelData(0); for(let i=0;i<d.length;i++) d[i]=Math.random()*2-1;
    }
    if(audioCtx.state==="suspended") audioCtx.resume();
    return audioCtx;
}
function tone(t, f0, f1, dur, wave, vib, vibDepth, vol){
    const c=audioCtx, o=c.createOscillator(), g=c.createGain();
    o.type=wave; o.frequency.setValueAtTime(f0,t); o.frequency.exponentialRampToValueAtTime(Math.max(30,f1), t+dur);
    if(vib){ const l=c.createOscillator(), lg=c.createGain(); l.frequency.value=vib; lg.gain.value=vibDepth; l.connect(lg); lg.connect(o.frequency); l.start(t); l.stop(t+dur); }
    g.gain.setValueAtTime(0.0001,t); g.gain.exponentialRampToValueAtTime(vol, t+Math.min(0.02,dur/4)); g.gain.exponentialRampToValueAtTime(0.0001, t+dur);
    o.connect(g); g.connect(master); o.start(t); o.stop(t+dur+0.02);
}
function noiseBurst(t, freq, dur, q, vol){
    const c=audioCtx, src=c.createBufferSource(), bp=c.createBiquadFilter(), g=c.createGain();
    src.buffer=noiseBuf; bp.type="bandpass"; bp.frequency.value=freq; bp.Q.value=q;
    g.gain.setValueAtTime(0.0001,t); g.gain.exponentialRampToValueAtTime(vol, t+Math.min(0.01,dur/4)); g.gain.exponentialRampToValueAtTime(0.0001, t+dur);
    src.connect(bp); bp.connect(g); g.connect(master); src.start(t, Math.random()*1.5, dur+0.05);
}
function mimicPhrase(){  // the mockingbird borrows bits of 3 other birds' calls, twice each
    const singers=shuffle(allBirds.filter(b=>!b.call.noise && !b.call.mimic && b.call.notes.length)).slice(0,3);
    return singers.flatMap(b=>{ const bit=b.call.notes.slice(0,3); return [...bit, ...bit]; });
}
// Real recordings: picked by the server from iNaturalist's best-rated Creative-Commons sounds.
// They play straight into the analyser, so the spectrogram draws exactly what you hear.
const MAX_CALL_SECONDS=10;
const decodedCalls=new Map();  // recording file → decoded audio, so a replay starts instantly
let currentCall=null, callToken=0;
let toastTimer=null;
function setSoundCredit(text, seconds){  // the credit shows on the Welcome card, and as a small note on every other tab
    const el=$("sound-credit"); if(el) el.textContent=text;
    const toast=$("now-playing"); toast.textContent=text; toast.classList.add("show");
    clearTimeout(toastTimer); toastTimer=setTimeout(()=>toast.classList.remove("show"), (seconds||4)*1000+1500);
}
function stopCall(){ if(currentCall){ try{ currentCall.stop(); }catch(e){} currentCall=null; } }
async function playBirdCall(bird){
    if(!bird) return 0;
    const c=getAudio(), token=++callToken;
    stopCall();
    const query = bird.id ? "bird="+encodeURIComponent(bird.id) : bird.taxon_id ? "taxon="+encodeURIComponent(bird.taxon_id) : null;
    setSoundCredit("⏳ Loading a real recording…");
    try{
        if(!query) throw new Error("no bird");
        const info=await (await fetch("/api/sound?"+query)).json();
        if(!info.file) throw new Error("no recording");
        let buf=decodedCalls.get(info.file);
        if(!buf){ buf=await c.decodeAudioData(await (await fetch(info.file)).arrayBuffer()); decodedCalls.set(info.file,buf); }
        if(token!==callToken) return 0;  // another sound was started while this one was loading
        const dur=Math.min(buf.duration, MAX_CALL_SECONDS), data=buf.getChannelData(0);
        let peak=0;  // even out loud and quiet recordings
        for(let i=0, end=Math.min(data.length, buf.sampleRate*dur); i<end; i+=4) peak=Math.max(peak, Math.abs(data[i]));
        const src=c.createBufferSource(), g=c.createGain(), t=c.currentTime+0.02, vol=Math.min(4, 0.8/Math.max(peak,0.01));
        src.buffer=buf;
        g.gain.setValueAtTime(vol,t); g.gain.setValueAtTime(vol,t+Math.max(0,dur-0.4)); g.gain.linearRampToValueAtTime(0.0001,t+dur);
        src.connect(g); g.connect(analyser);  // analyser → speakers, and the spectrogram reads it
        src.start(t,0,dur); currentCall=src;
        startSpectrogram(dur);
        setSoundCredit(`🎙️ ${bird.name ? bird.name+" — " : ""}real recording: ${info.credit || "an iNaturalist user"} · iNaturalist`, dur);
        return dur;
    }catch(e){
        if(token!==callToken) return 0;
        if(!bird.call) { setSoundCredit("No recording available right now."); return 0; }
        setSoundCredit("🎛️ No recording right now — playing ChirpQuest's made-up version instead.");
        return playSynthCall(bird);
    }
}
function playMysteryCall(id){  // quiz: same recording, but the credit note doesn't say which bird it is
    const b=birdById[id]; playBirdCall({id:b.id, call:b.call});
}
function playSynthCall(bird){  // the old made-up calls: a backup when a recording can't load (e.g. offline)
    if(!bird || !bird.call) return 0;
    const c=getAudio(), s=bird.call, p=0.93+Math.random()*0.14;  // tiny pitch wobble: never exactly the same twice
    const notes=s.mimic ? mimicPhrase() : s.notes;
    let t=c.currentTime+0.05;
    for(let r=0;r<(s.repeat||1);r++){
        for(const [f0,f1,dur,gap] of notes){
            if(s.noise) noiseBurst(t, f0*p, dur, s.q||4, s.vol||0.9);
            else tone(t, f0*p, f1*p, dur, s.wave||"sine", s.vib||0, s.vibDepth||0, s.vol||0.8);
            if(s.buzz) noiseBurst(t, s.buzz*p, dur, 2, 0.25);
            t+=dur+gap;
        }
        t+=s.rest ?? 0.25;
    }
    const seconds=t-c.currentTime; startSpectrogram(seconds); return seconds;
}
function playRandomBirdCall(){
    if(!allBirds.length) return;
    const b=allBirds[Math.floor(Math.random()*allBirds.length)];
    $("sound-bird-name").textContent=`${b.emoji} ${b.name}`;
    playBirdCall(b);
}
let specRunning=false, specUntil=0;
function startSpectrogram(seconds){ specUntil=Math.max(specUntil, performance.now()+seconds*1000+500); if(!specRunning){ specRunning=true; requestAnimationFrame(drawSpectrogram); } }
function drawSpectrogram(){
    const cv=$("spectrogram"), g=cv.getContext("2d"), w=cv.width, h=cv.height, col=3;
    g.drawImage(cv, -col, 0);  // scroll left, then paint the newest slice on the right
    const data=new Uint8Array(analyser.frequencyBinCount); analyser.getByteFrequencyData(data);
    const maxBin=Math.floor(data.length*Math.min(1, 9000/(audioCtx.sampleRate/2)));  // show 0–9 kHz
    for(let y=0;y<h;y++){
        const v=data[Math.floor((1-y/h)*maxBin)]/255;
        g.fillStyle = v<0.12 ? "#0f172a" : `hsl(${190-v*150},95%,${18+v*52}%)`;
        g.fillRect(w-col, y, col, 1);
    }
    if(performance.now()<specUntil) requestAnimationFrame(drawSpectrogram); else specRunning=false;
}
function pipWhistle(){ playSynthCall({call:{notes:[[1800,3200,.12,.04],[3200,2400,.12,.04],[2000,3600,.2,0]]}}); }

// ---------- facts ----------
async function loadFacts(){
    const list=$("facts-list");
    try{
        const d=await (await fetch("/api/facts")).json();
        list.innerHTML=d.facts.map(f=>`<li>${esc(f.text)}${f.bird_name?`<span class="fact-src">${esc(f.bird_name)} · <a href="${esc(f.source_url)}" target="_blank" rel="noopener">Wikipedia</a> · <a href="${esc(f.aab_url)}" target="_blank" rel="noopener">All About Birds ↗</a>${f.ai?" · ✨ kid-friendly rewrite":""}</span>`:""}</li>`).join("");
        if(d.loading) setTimeout(loadFacts, 5000);  // live facts are still being prepared — check again soon
    }catch(e){ list.innerHTML="<li>Pip couldn't fetch facts right now. Try again in a moment!</li>"; }
}

// ---------- bird holidays (Welcome banner) ----------
// Add ?date=2027-05-31 to the address to preview what the banner shows on any day.
async function loadHoliday(){
    try{
        const preview=new URLSearchParams(location.search).get("date");
        const d=await (await fetch("/api/holiday"+(preview?"?date="+encodeURIComponent(preview):""))).json();
        const h=d.today, minor=(d.minor||[]).map(m=>`${m.emoji} ${m.name}`).join(" and ");
        if(!h){  // minor bird day: just a small line. Otherwise: countdown to the next one
            $("banner-next").textContent = minor ? `🎈 Today is ${minor}!`
                : d.next ? `📅 Next bird holiday: ${d.next.emoji} ${d.next.name} — in ${d.next.days} day${d.next.days===1?"":"s"}` : "";
            return;
        }
        $("banner").classList.add("holiday");
        $("banner-title").textContent=`${h.emoji} Happy ${h.name}!`;
        $("banner-text").innerHTML=esc(h.message)+(h.link?` <a href="${esc(h.link)}" target="_blank" rel="noopener">Learn more ↗</a>`:"");
        $("banner-next").textContent = minor ? `🎈 Today is also ${minor}!` : "— from Pip the Cockatiel 🎉";
        if(h.photo && h.photo.url) $("banner-photo").innerHTML=`<img src="${esc(h.photo.url)}" alt="${esc(h.name)} bird photo"><div class="small">${esc(h.photo.credit)} · iNaturalist</div>`;
        setTimeout(()=>fireConfetti($("banner")),400);
    }catch(e){}
}

// ---------- weather ----------
const WX={0:"☀️ Clear",1:"🌤️ Mostly clear",2:"⛅ Partly cloudy",3:"☁️ Cloudy",45:"🌫️ Foggy",48:"🌫️ Foggy",51:"🌦️ Drizzle",53:"🌦️ Drizzle",55:"🌦️ Drizzle",61:"🌧️ Rain",63:"🌧️ Rain",65:"🌧️ Heavy rain",71:"🌨️ Snow",73:"🌨️ Snow",75:"🌨️ Snow",80:"🌦️ Showers",81:"🌦️ Showers",82:"⛈️ Heavy showers",95:"⛈️ Thunderstorm",96:"⛈️ Thunderstorm",99:"⛈️ Thunderstorm"};
function clock(iso){ const [h,m]=iso.split("T")[1].split(":").map(Number); return `${(h%12)||12}:${String(m).padStart(2,"0")} ${h<12?"AM":"PM"}`; }
async function loadWeather(lat,lng){
    try{
        const u=`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lng}&current=temperature_2m,weather_code,wind_speed_10m&daily=sunrise,sunset&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=auto&forecast_days=1`;
        const d=await (await fetch(u)).json();
        const temp=Math.round(d.current.temperature_2m), code=d.current.weather_code, wind=Math.round(d.current.wind_speed_10m);
        let score=100;
        if(code>=51&&code<80) score-=45; if(code>=80) score-=35; if(code>=95) score-=40; if(code===45||code===48) score-=20;
        if(wind>20) score-=30; else if(wind>12) score-=15; if(temp<35||temp>98) score-=25;
        score=Math.max(5,Math.min(100,score));
        const color=score>=80?"#22c55e":score>=55?"#eab308":score>=30?"#f97316":"#ef4444";
        const msg=score>=80?"Awesome birding weather! Grab your binoculars 🔭":score>=55?"Pretty good — birds are out there!":score>=30?"So-so. Try watching a window feeder.":"Stay cozy inside — perfect time for the Bird Quiz!";
        const sunriseH=Number(d.daily.sunrise[0].split("T")[1].split(":")[0]), nowH=new Date().getHours();
        const dawn=(nowH>=sunriseH && nowH<sunriseH+3) ? "<p class='small'>🌅 It's the dawn chorus — birds sing the most right now!</p>" : "";
        $("weather-box").innerHTML=`<div class="weather-big">${temp}°F</div><div>${WX[code]||"🌡️"} · 💨 ${wind} mph</div>
            <div class="meter"><div style="width:${score}%;background:${color};"></div></div>
            <b style="color:${color};">Birding score: ${score}/100</b><p style="margin:4px 0;font-size:0.88em;">${msg}</p>
            <p class="small" style="margin:0;">🌅 ${clock(d.daily.sunrise[0])} · 🌇 ${clock(d.daily.sunset[0])}</p>${dawn}`;
    }catch(e){ $("weather-box").textContent="Couldn't reach the weather service right now."; }
}

// ---------- live map (iNaturalist sightings) ----------
let birdMap=null, mapLayer=null, rangeCircle=null, mapState={lat:32.78,lng:-96.97,days:7,bookOnly:false}, lastSightings=null;
function initMap(){
    if(!window.L){ $("map-status").textContent="Map library didn't load (offline?)"; return; }
    birdMap=L.map("bird-map",{scrollWheelZoom:false}).setView([mapState.lat,mapState.lng],9);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:18,attribution:'&copy; OpenStreetMap contributors · sightings © iNaturalist users'}).addTo(birdMap);
    mapLayer=L.layerGroup().addTo(birdMap);
    document.querySelectorAll(".chip[data-days]").forEach(ch=>ch.addEventListener("click",()=>{
        document.querySelectorAll(".chip[data-days]").forEach(c=>c.classList.toggle("on",c===ch));
        mapState.days=Number(ch.dataset.days); loadSightings();
    }));
    $("book-only-chip").addEventListener("click",e=>{ mapState.bookOnly=!mapState.bookOnly; e.currentTarget.classList.toggle("on",mapState.bookOnly); drawSightings(); });
    $("near-me-chip").addEventListener("click",()=>{
        if(!navigator.geolocation){ $("map-status").textContent="This browser can't share location."; return; }
        $("map-status").textContent="Finding you…";
        navigator.geolocation.getCurrentPosition(p=>{
            mapState.lat=+p.coords.latitude.toFixed(3); mapState.lng=+p.coords.longitude.toFixed(3);
            $("near-me-chip").classList.add("on"); birdMap.setView([mapState.lat,mapState.lng],10);
            loadSightings(); loadWeather(mapState.lat,mapState.lng);
        },()=>{ $("map-status").textContent="Location not shared — showing Dallas–Fort Worth."; });
    });
    loadSightings();
}
async function loadSightings(){
    $("map-status").textContent="loading sightings…";
    try{
        const r=await fetch(`/api/sightings?lat=${mapState.lat}&lng=${mapState.lng}&days=${mapState.days}`);
        if(!r.ok) throw new Error(r.status);
        lastSightings=await r.json(); drawSightings();
    }catch(e){ $("map-status").textContent="Couldn't load sightings right now."; }
}
// Map pins: a teal pin with the bird's cartoon face for Bird Book birds, a smaller gray "?" pin for every other bird.
// Each kind of pin is drawn once as an image and reused.
const pinIcons={};
function birdPinIcon(book){
    const key=book ? book.id : "?";
    if(!pinIcons[key]){
        const face = book
            ? `<svg x="19" y="13" width="62" height="62" viewBox="${book.face_vb}">${book.svg.replace(/^<svg[^>]*>/,"").replace(/<\/svg>\s*$/,"").replaceAll("__UID__","pin")}</svg>`
            : `<text x="50" y="59" text-anchor="middle" font-family="Arial,sans-serif" font-size="42" font-weight="bold" fill="#475569">?</text>`;
        const svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 120"><defs><clipPath id="pinFace"><circle cx="50" cy="44" r="31"/></clipPath></defs>`
            +`<path d="M50,117 C50,117 10,72 10,44 A40,40 0 1 1 90,44 C90,72 50,117 50,117 Z" fill="${book?"#14b8a6":"#cbd5e1"}" stroke="#1e293b" stroke-width="5" stroke-linejoin="round"/>`
            +`<circle cx="50" cy="44" r="31" fill="#fff"/><g clip-path="url(#pinFace)">${face}</g>`
            +`<circle cx="50" cy="44" r="31" fill="none" stroke="#1e293b" stroke-width="3"/></svg>`;
        const [w,h]=book ? [40,48] : [24,29];
        pinIcons[key]=L.icon({iconUrl:"data:image/svg+xml;charset=utf-8,"+encodeURIComponent(svg), iconSize:[w,h], iconAnchor:[w/2,h], popupAnchor:[0,-h+4]});
    }
    return pinIcons[key];
}
function drawSightings(){
    const d=lastSightings; if(!d) return;
    mapLayer.clearLayers();
    if(rangeCircle) rangeCircle.remove();
    rangeCircle=L.circle(d.center,{radius:d.radius_km*1000,color:"#14b8a6",weight:1.5,fillOpacity:0.04,dashArray:"6 6"}).addTo(birdMap);
    const shown=d.sightings.filter(s=>!mapState.bookOnly||s.bird_id);
    shown.forEach(s=>{
        const book=s.bird_id?birdById[s.bird_id]:null;
        const marker=L.marker([s.lat,s.lng],{icon:birdPinIcon(book), zIndexOffset:book?100:0, title:s.name, alt:s.name});
        marker.bindPopup(`<div class="map-popup">${s.photo?`<img src="${esc(s.photo.replace("/square.","/small."))}" alt="">`:""}
            <b>${esc(s.name)}</b>${book?" ⭐":""}<br>📅 ${esc(s.date||"")}<br><span style="font-size:0.75em;color:#64748b;">${esc(s.credit)}</span><br>
            <a href="${esc(s.link)}" target="_blank" rel="noopener">See it on iNaturalist ↗</a></div>`);
        mapLayer.addLayer(marker);
    });
    const when={1:"today",7:"this week",30:"this month"}[d.days];
    $("map-status").textContent=`${d.total.toLocaleString()} bird sightings ${when} within ${d.radius_km} km · showing ${shown.length} newest`;
    const max=Math.max(1,...d.top.map(t=>t.count));
    $("top-list").innerHTML=d.top.map((t,i)=>`<li class="${t.bird_id?"book":""}">${i+1}. ${t.bird_id?esc(birdById[t.bird_id].emoji)+" ":""}${esc(t.name)} <b style="float:right;">${t.count}</b>
        <div class="top-bar" style="width:${Math.round(t.count/max*100)}%;"></div></li>`).join("") || "<li>No sightings yet — be the first!</li>";
}

// ---------- chat (text is inserted safely, never as HTML) ----------
function addChatMsg(text, cls){ const c=$("chat-container"), div=document.createElement("div"); div.className="chat-msg "+cls; div.textContent=text; c.appendChild(div); c.scrollTop=c.scrollHeight; return div; }
function askPip(q){ $("user-input").value=q; sendChatMessage(); }
async function sendChatMessage(){
    const input=$("user-input"), btn=$("send-btn"), text=input.value.trim(); if(!text) return;
    const c=$("chat-container");
    addChatMsg(text,"user-msg"); input.value=""; btn.disabled=true;
    const typing=document.createElement("div"); typing.className="typing-msg";
    typing.innerHTML='<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
    c.appendChild(typing); c.scrollTop=c.scrollHeight;
    try{
        const r=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:text})});
        const data=await r.json(); typing.remove(); addChatMsg(data.reply,"bot-msg");
    }catch(e){ typing.remove(); addChatMsg("Chirp! Something ruffled my feathers. Try again?","bot-msg"); }
    finally{ btn.disabled=false; input.focus(); }
}

// ---------- bird book ----------
let bookFilter={habitat:"all", q:""};
function renderBook(){
    const grid=$("bird-grid"); grid.innerHTML="";
    allBirds.forEach(bird=>{
        const card=document.createElement("div");
        card.className="bird-page"+(checkedSet.has(bird.id)?" spotted":""); card.id="card-"+bird.id; card.dataset.id=bird.id;
        card.innerHTML=`
            <h3 class="bird-name-row"><span class="emoji-icon">${esc(bird.emoji)}</span> ${esc(bird.name)}</h3>
            <div class="bird-stage" title="Tap to switch photo / cartoon" onclick="toggleView('${bird.id}')">
                <div class="bird-sprite-container" id="sprite-${bird.id}">${birdArt(bird)}</div>
                <img class="bird-photo" id="photo-${bird.id}" alt="Photo of a ${esc(bird.name)}">
                <span class="photo-tag" id="tag-${bird.id}">cartoon</span>
            </div>
            <div class="field-marks"><strong style="color:#0f766e;">Key Marks:</strong><ul>${bird.marks.map(m=>`<li>${esc(m)}</li>`).join("")}</ul></div>
            <div class="season" id="season-${bird.id}">📅 …</div>
            <div class="card-buttons">
                <button class="mini-btn" onclick="playBirdCall(birdById['${bird.id}'])">🔊 Call</button>
                <button class="mini-btn" onclick="openDrawGuide('${bird.id}')">✏️ Draw it</button>
                <a class="mini-btn" href="${esc(bird.aab_url)}" target="_blank" rel="noopener" style="text-decoration:none;">All About Birds ↗</a>
            </div>`;
        grid.appendChild(card);
    });
    applyBookFilter();
    // load photos and season charts only when a card scrolls into view
    const io=new IntersectionObserver(entries=>entries.forEach(en=>{
        if(!en.isIntersecting) return;
        io.unobserve(en.target);
        const b=birdById[en.target.dataset.id]; loadBirdPhoto(b); loadSeason(b);
    }),{rootMargin:"200px"});
    document.querySelectorAll(".bird-page").forEach(c=>io.observe(c));
}
function applyBookFilter(){
    const q=bookFilter.q.toLowerCase();
    allBirds.forEach(b=>{
        const hay=(b.name+" "+b.marks.join(" ")+" "+b.inat).toLowerCase();
        const show=(bookFilter.habitat==="all"||b.habitat===bookFilter.habitat) && (!q||hay.includes(q));
        $("card-"+b.id).style.display=show?"":"none";
    });
}
$("book-search").addEventListener("input",e=>{ bookFilter.q=e.target.value.trim(); applyBookFilter(); });
document.querySelectorAll(".chip[data-habitat]").forEach(ch=>ch.addEventListener("click",()=>{
    document.querySelectorAll(".chip[data-habitat]").forEach(c=>c.classList.toggle("on",c===ch));
    bookFilter.habitat=ch.dataset.habitat; applyBookFilter();
}));
function loadBirdPhoto(bird){
    fetch("/api/photo?name="+encodeURIComponent(bird.inat)).then(r=>r.json()).then(d=>{
        if(d && d.url){ const img=$("photo-"+bird.id); img.dataset.src=d.url; }
    }).catch(()=>{});
}
function toggleView(id){  // cartoon first; the photo appears on tap
    const img=$("photo-"+id), sprite=$("sprite-"+id), tag=$("tag-"+id);
    if(!img.dataset.src){ tag.textContent="photo loading…"; return; }
    if(!img.src){ img.onload=()=>img.classList.add("loaded"); img.src=img.dataset.src; }
    const showPhoto=sprite.style.display!=="none";
    sprite.style.display=showPhoto?"none":"inline-block"; img.style.display=showPhoto?"block":"none";
    tag.textContent=showPhoto?"real photo · iNaturalist":"cartoon";
}
const MONTHS="JFMAMJJASOND";
async function loadSeason(bird){
    const box=$("season-"+bird.id);
    try{
        const d=await (await fetch("/api/season?bird="+bird.id)).json();
        if(!d.months) throw new Error();
        const max=Math.max(1,...d.months), now=new Date().getMonth(), best=d.months.indexOf(Math.max(...d.months));
        const bars=d.months.map((v,i)=>{ const h=Math.max(2,Math.round(v/max*30)); return `<rect x="${i*16+2}" y="${32-h}" width="12" height="${h}" rx="2" fill="${i===now?"#f59e0b":"#5eead4"}"/><text x="${i*16+8}" y="43" font-size="8" text-anchor="middle" fill="#64748b">${MONTHS[i]}</text>`; }).join("");
        const names=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
        box.innerHTML=`📅 Easiest to spot in Texas: <b>${names[best]}</b><svg viewBox="0 0 194 44">${bars}</svg>`;
    }catch(e){ box.textContent="📅 season chart unavailable"; }
}

// ---------- checklist ----------
function renderChecklist(){
    const cl=$("checklist-container"); cl.innerHTML="";
    allBirds.forEach(bird=>{
        const on=checkedSet.has(bird.id);
        cl.insertAdjacentHTML("beforeend",`<label class="check-item ${on?"checked":""}" id="label-${bird.id}">
            <input type="checkbox" id="check-${bird.id}" ${on?"checked":""} onchange="setSpotted('${bird.id}', this.checked)">
            <span>${esc(bird.emoji)} ${esc(bird.name)}</span></label>`);
    });
    updateChecklistProgress();
}
function setSpotted(id, on){
    if(on) checkedSet.add(id); else checkedSet.delete(id);
    save(pkey("checked"),[...checkedSet]);
    $("check-"+id).checked=on; $("label-"+id).classList.toggle("checked",on); $("card-"+id)?.classList.toggle("spotted",on);
    updateChecklistProgress();
}
function updateChecklistProgress(){
    const total=allBirds.length||1;
    $("checklist-progress-bar").style.width=Math.round(checkedSet.size/total*100)+"%";
    $("checklist-count").textContent=checkedSet.size;
}

// ---------- photo ID (Gemini vision) ----------
let pendingImage=null;
const dz=$("drop-zone");
$("photo-input").addEventListener("change",e=>handlePhotoFile(e.target.files[0]));
dz.addEventListener("dragover",e=>{ e.preventDefault(); dz.classList.add("drag"); });
dz.addEventListener("dragleave",()=>dz.classList.remove("drag"));
dz.addEventListener("drop",e=>{ e.preventDefault(); dz.classList.remove("drag"); handlePhotoFile(e.dataTransfer.files[0]); });
function resizeImage(file, max){  // shrink big phone photos before sending (faster + more private)
    return new Promise((resolve,reject)=>{
        const img=new Image();
        img.onload=()=>{ const s=Math.min(1,max/Math.max(img.width,img.height)), cv=document.createElement("canvas");
            cv.width=Math.round(img.width*s); cv.height=Math.round(img.height*s);
            cv.getContext("2d").drawImage(img,0,0,cv.width,cv.height); URL.revokeObjectURL(img.src); resolve(cv.toDataURL("image/jpeg",0.85)); };
        img.onerror=reject; img.src=URL.createObjectURL(file);
    });
}
function showPreview(dataUrl){
    pendingImage=dataUrl; const p=$("id-preview"); p.src=dataUrl; p.style.display="block";
    $("drop-emoji").style.display="none"; $("drop-text").textContent="Tap to choose a different photo";
    $("identify-btn").disabled=false;
}
async function handlePhotoFile(file){
    if(!file || !file.type.startsWith("image/")) return;
    pendingSample=false;
    try{ showPreview(await resizeImage(file,800)); }catch(e){ $("id-result").innerHTML="<h3>Hmm…</h3><p>Pip couldn't open that picture. Try a JPG or PNG.</p>"; }
}
let idKind="bird";
document.querySelectorAll(".chip[data-id-kind]").forEach(ch=>ch.addEventListener("click",()=>setIdKind(ch.dataset.idKind)));
function setIdKind(k){
    idKind=k;
    document.querySelectorAll(".chip[data-id-kind]").forEach(c=>c.classList.toggle("on",c.dataset.idKind===k));
    $("sample-btn").textContent = k==="drawing" ? "🎲 Try a sample drawing" : "🎲 Try a sample photo";
}
async function cartoonPicture(bird, size=600, sky=false){  // turn a cartoon into an image (a sample "drawing", or a puzzle picture)
    const cv=document.createElement("canvas"); cv.width=cv.height=size; const g=cv.getContext("2d");
    if(sky){ const s=g.createLinearGradient(0,0,0,size); s.addColorStop(0,"#dbeafe"); s.addColorStop(0.65,"#f0fdf4"); s.addColorStop(1,"#bbf7d0"); g.fillStyle=s; }
    else g.fillStyle="#ffffff";
    g.fillRect(0,0,size,size);
    const svg=birdArt(bird).replace("<svg ",`<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" `);
    const url=URL.createObjectURL(new Blob([svg],{type:"image/svg+xml"}));
    try{ g.drawImage(await loadImage(url),0,0,size,size); } finally{ URL.revokeObjectURL(url); }
    return cv;
}
async function loadSamplePhoto(){
    const btn=$("sample-btn"); btn.disabled=true;
    try{
        if(idKind==="drawing"){
            const b=allBirds[Math.floor(Math.random()*allBirds.length)];
            showPreview((await cartoonPicture(b,600)).toDataURL("image/jpeg",0.9));
            $("id-result").innerHTML=`<h3>Sample drawing loaded!</h3><p class="muted">One of ChirpQuest's own cartoons. Can Pip tell which bird it is? (Samples don't count toward Master Artist — draw your own!)</p>`;
            pendingSample=true; return;
        }
        const d=await (await fetch("/api/sample_photo")).json(); if(d.image){ showPreview(d.image); pendingSample=true; }
        $("id-result").innerHTML=`<h3>Sample loaded!</h3><p class="muted">A real Texas bird photo from iNaturalist. Can you guess it before Pip does? (Samples don't count toward badges.)</p><p class="small">${esc(d.credit)}</p>`;
    }catch(e){} finally{ btn.disabled=false; }
}
let pendingSample=false;
function meter(score, label){
    const color=score>=75?"#22c55e":score>=45?"#eab308":"#f97316";
    return `<div class="meter"><div style="width:${score}%;background:${color};"></div></div><b style="color:${color};">${label}</b>`;
}
function askPipAbout(name){ openTab("chat"); askPip(`Tell me about the ${name}!`); }
async function identifyPhoto(){
    if(!pendingImage) return;
    const btn=$("identify-btn"), box=$("id-result"), sample=pendingSample; btn.disabled=true;
    box.innerHTML='<h3>Pip is looking closely… 🔍</h3><div class="skeleton"></div><div class="skeleton"></div>';
    try{
        const r=await fetch("/api/identify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({image:pendingImage, kind:idKind})});
        const d=await r.json();
        if(d.error){ box.innerHTML=`<h3>Oops!</h3><p>${esc(d.error)}</p>`; return; }
        const book=d.bird_id?birdById[d.bird_id]:null;
        const askBtn=n=>`<button class="mini-btn" onclick="askPipAbout(${esc(JSON.stringify(n))})">💬 Ask Pip about it</button>`;
        if(d.kind==="other"){
            box.innerHTML=`<h3>🔎 What Pip sees</h3><p>${esc(d.what_it_is)}</p>
                ${d.bird_name?`<p>…and I spotted a bird in there: <b>${esc(d.bird_name)}</b>! ${askBtn(d.bird_name)}</p>`:""}
                <p><b>💡 Fun fact:</b> ${esc(d.fun_fact)}</p>`;
            return;
        }
        if(d.kind==="drawing"){
            if(!d.is_drawing){ box.innerHTML=`<h3>🤔 Hmm, I can't find a bird drawing</h3><p>${esc(d.fun_fact)}</p><p class="small">Is it a photo of a real bird? Pick "📷 A real bird" above.</p>`; return; }
            let art="";
            if(sample) art="<p class='small'>That was a sample — draw your own bird to earn Master Artist! ✏️</p>";
            else if(d.counts_for_art && artSet.has(book.id)) art=`<p>🎨 You already drew a ${esc(book.name)} — draw a <b>different</b> bird to earn more!</p>`;
            else if(d.counts_for_art){ artSet.add(book.id); save(pkey("art"),[...artSet]); updateArtCount();
                art=`<p><b>🎨 +1 for Master Artist!</b> (${Math.min(artSet.size,10)}/10 different birds)${artSet.size===10?" 🏆 You're a Master Artist!":""}</p>`; fireConfetti(box); }
            else if(book) art=`<p>🎯 Score ${d.likeness_needed}+ to count toward Master Artist — try the tip above!</p>`;
            else art="<p class='small'>Draw a Bird Book bird to count toward Master Artist.</p>";
            box.innerHTML=`<h3>✏️ Your drawing looks like a ${esc(d.name)}!</h3>${meter(d.likeness,`Looks-like score: ${d.likeness}/100`)}
                <p><b>⭐ You got right:</b> ${esc(d.got_right)}</p><p><b>💡 Tip:</b> ${esc(d.tip)}</p>${art}
                ${book?`<button class="mini-btn" onclick="openDrawGuide('${book.id}')">✏️ See the step-by-step guide</button>`:""}`;
            return;
        }
        if(!d.is_bird){ box.innerHTML=`<h3>🤔 Hmm, no bird?</h3><p>${esc(d.fun_fact)}</p><p class="small">Is it a drawing? Pick "✏️ My drawing" above.</p>`; return; }
        if(!sample){ photoIds+=1; save(pkey("photo_ids"),photoIds); }
        const conf=Math.max(0,Math.min(100,Number(d.confidence)||0));
        box.innerHTML=`<h3>${book?esc(book.emoji)+" ":"🐦 "}It looks like a ${esc(d.name)}!</h3>${meter(conf,`Pip is ${conf}% sure`)}
            <p><b>🔎 Clues:</b> ${esc(d.clues)}</p><p><b>💡 Fun fact:</b> ${esc(d.fun_fact)}</p>
            <p>${d.north_texas_count?`📍 Lives in North Texas — seen ${d.north_texas_count.toLocaleString()} times near DFW.`:"🧳 Not on the North Texas list — a rare visitor, or a bird from somewhere else!"} ${askBtn(d.name)}</p>
            ${book?`<p>This bird is in your Bird Book! ${checkedSet.has(book.id)?"✅ Already spotted.":`<button class="mini-btn" onclick="setSpotted('${book.id}',true);this.outerHTML='✅ Added to your checklist!'">✅ Mark as spotted</button>`}</p>`:""}
            <p class="small">AI can make mistakes — check the Bird Book to compare field marks!</p>`;
    }catch(e){ box.innerHTML="<h3>Oops!</h3><p>Pip couldn't reach the AI. Try again!</p>"; }
    finally{ btn.disabled=false; }
}

// ---------- quiz ----------
let quiz=null;
function startQuiz(mode){
    if(allBirds.length<4) return;
    quiz={mode, n:0, total:10, score:0, streak:0, order:shuffle(allBirds).slice(0,10)};
    nextQuestion();
}
async function nextQuestion(){
    const stage=$("quiz-stage"), answer=quiz.order[quiz.n];
    const choices=shuffle([answer, ...shuffle(allBirds.filter(b=>b.id!==answer.id)).slice(0,3)]);
    stage.innerHTML=`<div class="quiz-hud"><span>Question ${quiz.n+1} / ${quiz.total}</span><span>⭐ ${quiz.score}</span><span>🔥 Streak ${quiz.streak}</span></div>
        <div class="quiz-picture" id="quiz-picture"><div class="skeleton" style="width:200px;height:200px;"></div></div><p class="small" id="quiz-credit"></p>
        <div class="quiz-choices">${choices.map(c=>`<button class="choice" data-id="${c.id}">${esc(c.name)}</button>`).join("")}</div>`;
    stage.querySelectorAll(".choice").forEach(b=>b.addEventListener("click",()=>answerQuestion(b.dataset.id)));
    const pic=$("quiz-picture");
    if(quiz.mode==="cartoon") pic.innerHTML=birdArt(answer);
    else if(quiz.mode==="sound"){ pic.innerHTML=`<button class="big-btn alt" style="font-size:1.3em;" onclick="playMysteryCall('${answer.id}')">🔊 Play the call again</button>`; playMysteryCall(answer.id); }
    else{
        try{ const d=await (await fetch("/api/quiz_photo?bird="+answer.id)).json();
             if(!d.url) throw new Error();
             pic.innerHTML=`<img src="${esc(d.url)}" alt="Mystery bird">`; $("quiz-credit").textContent=d.credit||"";
        }catch(e){ pic.innerHTML=birdArt(answer); $("quiz-credit").textContent="(photo unavailable — here's the cartoon!)"; }
    }
}
function answerQuestion(id){
    const answer=quiz.order[quiz.n], right=id===answer.id;
    document.querySelectorAll(".choice").forEach(b=>{ b.disabled=true; if(b.dataset.id===answer.id) b.classList.add("right"); else if(b.dataset.id===id) b.classList.add("wrong"); });
    if(right){ quiz.score++; quiz.streak++; } else quiz.streak=0;
    const stage=$("quiz-stage");
    stage.insertAdjacentHTML("beforeend",`<p style="font-weight:bold;color:${right?"#15803d":"#b91c1c"};">${right?"Correct! 🎉":"Not quite — it's the "+esc(answer.name)+"."} <span class="small">${esc(answer.marks[0])}</span></p>
        <button class="big-btn" id="quiz-next">${quiz.n+1<quiz.total?"Next ➜":"See my score 🏁"}</button>`);
    $("quiz-next").addEventListener("click",()=>{ quiz.n++; if(quiz.n<quiz.total) nextQuestion(); else finishQuiz(); });
}
function finishQuiz(){
    const s=quiz.score, stage=$("quiz-stage");
    const newBest=s>quizBest; if(newBest){ quizBest=s; save(pkey("quiz_best"),s); $("quiz-best").textContent=s; }
    const msg=s===10?"PERFECT! You're a bird genius! 🏆":s>=8?"Amazing birding skills! 🧠":s>=5?"Nice work — keep practicing! 🐤":"Every expert starts somewhere. Try the Bird Book, then play again! 📖";
    stage.innerHTML=`<p style="font-size:3em;margin:10px 0;">${s>=8?"🏆":s>=5?"🎉":"🐣"}</p><h2 style="color:#0f766e;">You scored ${s} / ${quiz.total}</h2><p>${msg}</p>
        ${newBest?"<p><b>🌟 New best score!</b></p>":""}<button class="big-btn" onclick="startQuiz('${quiz.mode}')">Play again</button>`;
    if(s>=8) fireConfetti(stage);
}

// ---------- mystery bird puzzle ----------
// The picture is drawn into a square "source" canvas, cut into n×n tiles, and shuffled.
// order[spot] = which tile is sitting in that spot; solved when order[i]===i everywhere.
let pz=null, pzPic="photo", pzSize=3, pzTimer=null;
document.querySelectorAll(".chip[data-pz-pic]").forEach(ch=>ch.addEventListener("click",()=>{
    document.querySelectorAll(".chip[data-pz-pic]").forEach(c=>c.classList.toggle("on",c===ch)); pzPic=ch.dataset.pzPic; newPuzzle();
}));
document.querySelectorAll(".chip[data-pz-size]").forEach(ch=>ch.addEventListener("click",()=>{
    document.querySelectorAll(".chip[data-pz-size]").forEach(c=>c.classList.toggle("on",c===ch)); pzSize=Number(ch.dataset.pzSize); newPuzzle();
}));
function loadImage(src){ return new Promise((res,rej)=>{ const im=new Image(); im.onload=()=>res(im); im.onerror=rej; im.src=src; }); }
async function puzzleSource(bird){
    const S=600, src=document.createElement("canvas"); src.width=src.height=S;
    const g=src.getContext("2d");
    if(pzPic==="photo"){
        try{
            const d=await (await fetch("/api/quiz_photo?bird="+bird.id)).json();
            if(!d.url) throw new Error();
            const im=await loadImage(d.url), side=Math.min(im.width,im.height);  // square crop from the middle
            g.drawImage(im,(im.width-side)/2,(im.height-side)/2,side,side,0,0,S,S);
            return {canvas:src, credit:d.credit||""};
        }catch(e){ /* fall through to the cartoon */ }
    }
    return {canvas:await cartoonPicture(bird,S,true), credit:""};
}
async function newPuzzle(){
    if(!allBirds.length) return;
    clearInterval(pzTimer);
    const bird=allBirds[Math.floor(Math.random()*allBirds.length)], n=pzSize;
    $("puzzle-title").textContent="Who is the mystery bird? 🤔"; $("puzzle-message").textContent="Mixing up the tiles…";
    const {canvas, credit}=await puzzleSource(bird);
    let order; do{ order=shuffle([...Array(n*n).keys()]); }while(order.every((t,i)=>t===i));  // never start already solved
    pz={bird, n, src:canvas, order, sel:null, moves:0, start:Date.now(), solved:false, peek:false, credit};
    $("puzzle-message").textContent="Tip: tiles that are in the right spot get a green check ✅.";
    pzTimer=setInterval(updatePuzzleStats,1000);
    drawPuzzle(); updatePuzzleStats();
}
function drawPuzzle(){
    const cv=$("puzzle-board"), g=cv.getContext("2d"), W=cv.width;
    if(!pz){ g.fillStyle="#f0fdfa"; g.fillRect(0,0,W,W); return; }
    const n=pz.n, ts=W/n, ss=pz.src.width/n;
    g.clearRect(0,0,W,W);
    if(pz.solved||pz.peek){ g.drawImage(pz.src,0,0,W,W); return; }
    pz.order.forEach((tile,spot)=>{
        const dx=(spot%n)*ts, dy=Math.floor(spot/n)*ts;
        g.drawImage(pz.src,(tile%n)*ss,Math.floor(tile/n)*ss,ss,ss,dx,dy,ts,ts);
        g.strokeStyle="rgba(255,255,255,0.9)"; g.lineWidth=3; g.strokeRect(dx+1.5,dy+1.5,ts-3,ts-3);
        if(tile===spot){ g.font=`${Math.round(ts*0.18)}px sans-serif`; g.fillText("✅",dx+6,dy+ts*0.22); }
    });
    if(pz.sel!==null){
        const dx=(pz.sel%n)*ts, dy=Math.floor(pz.sel/n)*ts;
        g.strokeStyle="#f59e0b"; g.lineWidth=8; g.strokeRect(dx+4,dy+4,ts-8,ts-8);
    }
}
function updatePuzzleStats(){
    if(!pz) return;
    const secs=Math.floor(((pz.end||Date.now())-pz.start)/1000);
    $("pz-moves").textContent=pz.moves; $("pz-time").textContent=`${Math.floor(secs/60)}:${String(secs%60).padStart(2,"0")}`;
    $("pz-place").textContent=`${pz.order.filter((t,i)=>t===i).length}/${pz.n*pz.n}`;
}
$("puzzle-board").addEventListener("click",e=>{
    if(!pz||pz.solved) return;
    const r=e.currentTarget.getBoundingClientRect(), n=pz.n;
    const col=Math.min(n-1,Math.floor((e.clientX-r.left)/r.width*n)), row=Math.min(n-1,Math.floor((e.clientY-r.top)/r.height*n));
    const spot=row*n+col;
    if(pz.sel===null) pz.sel=spot;
    else if(pz.sel===spot) pz.sel=null;
    else{ [pz.order[pz.sel],pz.order[spot]]=[pz.order[spot],pz.order[pz.sel]]; pz.sel=null; pz.moves++; }
    if(pz.order.every((t,i)=>t===i)) solvePuzzle();
    drawPuzzle(); updatePuzzleStats();
});
function peekPuzzle(on){ if(pz&&!pz.solved){ pz.peek=on; drawPuzzle(); } }
function solvePuzzle(){
    pz.solved=true; pz.end=Date.now(); clearInterval(pzTimer);
    puzzlesSolved+=1; save(pkey("puzzles"),puzzlesSolved); $("puzzle-solved-count").textContent=puzzlesSolved;
    const b=pz.bird;
    $("puzzle-title").textContent=`🎉 It's a ${b.name}! ${b.emoji}`;
    $("puzzle-message").innerHTML=`You rebuilt it in <b>${pz.moves}</b> swaps! <br>💡 ${esc(b.marks[0])}.
        ${puzzlesSolved===5?"<br><b>🧩 You unlocked the Puzzle Pro badge!</b>":puzzlesSolved<5?`<br>${5-puzzlesSolved} more for the Puzzle Pro badge.`:""}
        <div class="card-buttons" style="justify-content:flex-start;"><button class="mini-btn" onclick="playBirdCall(birdById['${b.id}'])">🔊 Hear its call</button>
        <button class="mini-btn" onclick="newPuzzle()">🧩 Next puzzle</button></div>${pz.credit?`<p class="small">${esc(pz.credit)}</p>`:""}`;
    fireConfetti($("puzzle-message"));
}

// ---------- draw birds (step-by-step guides made from the cartoons) ----------
// Every part of a cartoon is tagged with data-step (1 body, 2 head, 3 tail & wings, 4 eye & beak, 5 legs,
// 6 colors & markings). Panel k shows steps 1..k as a pencil sketch, with step k in blue; the last panel is in color.
function drawStepText(k, b){
    const shape=b.shape;
    return {
        1: shape==="owl" ? "Draw a big round body, like a fat egg." : shape==="heron" ? "Draw a long, tilted oval for the body."
           : shape==="duck" ? "Draw a long oval body, like a little boat." : "Draw an egg shape for the body.",
        2: shape==="heron" ? "Add a curvy S-shaped neck and a small round head."
           : shape==="owl" ? "Add a big round head on top." : "Add a circle for the head, overlapping the body (plus any crest).",
        3: shape==="owl" ? "Add a wing on each side." : "Draw the tail, then a teardrop-shaped wing.",
        4: shape==="owl" ? "Draw two round face patches, big eyes and a small beak." : "Give it a big round eye with a shiny dot, and the beak.",
        5: shape==="heron" ? "Add two long, skinny legs." : "Add the legs and little feet.",
        6: "Color it in! Look for: " + b.marks.join(" · "),
    }[k];
}
function renderDrawGuide(id){
    const b=birdById[id]; if(!b) return;
    $("draw-pick").value=id;
    const box=$("draw-steps"); box.innerHTML="";
    const probe=document.createElement("div"); probe.innerHTML=b.svg;
    const steps=[...new Set([...probe.querySelectorAll("[data-step]")].map(g=>+g.dataset.step))].filter(s=>s>0).sort((x,y)=>x-y);
    steps.forEach((k,i)=>{
        const last=i===steps.length-1, card=document.createElement("div");
        card.className="draw-step"+(last?" final":"");
        card.innerHTML=`<div class="draw-num">${i+1}</div>${birdArt(b)}<p>${esc(drawStepText(k,b))}</p>`;
        const svg=card.querySelector("svg");
        svg.querySelectorAll("[data-step]").forEach(g=>{
            const s=+g.dataset.step;
            if(s>k || (s===0 && !last)) g.style.display="none";
            else if(s===k && !last) g.classList.add("new-part");
        });
        if(!last) svg.classList.add("sketch");
        box.appendChild(card);
    });
}
function openDrawGuide(id){ openTab("draw"); renderDrawGuide(id); }
function pickRandomDrawing(){ renderDrawGuide(allBirds[Math.floor(Math.random()*allBirds.length)].id); }
function updateArtCount(){
    if(!$("art-count")) return;
    $("art-count").textContent=Math.min(artSet.size,10);
    $("art-gallery").textContent=artSet.size ? "· Drawn: "+[...artSet].map(id=>birdById[id]?birdById[id].emoji+" "+birdById[id].name:"").join(", ") : "";
}
function initDrawTab(){
    $("draw-pick").innerHTML=[...allBirds].sort((x,y)=>x.name.localeCompare(y.name))
        .map(b=>`<option value="${b.id}">${esc(b.emoji)} ${esc(b.name)}</option>`).join("");
    renderDrawGuide("cardinal"); updateArtCount();
}

// ---------- showtime ----------
async function loadVideos(){
    try{
        const v=await (await fetch("/api/videos")).json();
        const embed=x=>`https://www.youtube-nocookie.com/embed/${encodeURIComponent(x.video_id)}`;
        $("live-cam").innerHTML=v.live?`<div class="live-card"><div class="video-frame-wrap"><iframe src="${embed(v.live)}" title="${esc(v.live.title)}" allowfullscreen loading="lazy"></iframe></div>
            <p class="live-title"><span class="live-dot">● LIVE CAM</span> ${esc(v.live.emoji)} ${esc(v.live.title)}</p></div>`:"";
        $("video-grid").innerHTML=v.clips.map(x=>`<div class="video-card"><div class="video-frame-wrap"><iframe src="${embed(x)}" title="${esc(x.title)}" allowfullscreen loading="lazy"></iframe></div>
            <p class="video-title">${esc(x.emoji)} ${esc(x.title)}</p><p class="small" style="margin:2px 0 0;">${esc(x.channel)}</p></div>`).join("");
    }catch(e){ $("video-grid").innerHTML="<p>Couldn't load videos right now.</p>"; }
}

// ---------- prizes ----------
function fireConfetti(container){
    const colors=["#ef4444","#f97316","#eab308","#22c55e","#0ea5e9","#a855f7"];
    for(let i=0;i<24;i++){
        const p=document.createElement("div"); p.className="confetti-piece";
        p.style.left=Math.random()*100+"%"; p.style.background=colors[Math.floor(Math.random()*colors.length)];
        p.style.animationDelay=(Math.random()*0.3)+"s"; container.style.position="relative";
        container.appendChild(p); setTimeout(()=>p.remove(),1700);
    }
}
async function renderBadges(){
    let badges=[]; try{ badges=await (await fetch("/api/prizes")).json(); }catch(e){ return; }
    const grid=$("badge-grid"); grid.innerHTML="";
    badges.forEach(b=>{
        const have={quiz:quizBest, photoid:photoIds, puzzle:puzzlesSolved, art:artSet.size}[b.type] ?? checkedSet.size;
        const unit={quiz:"best quiz score", photoid:"photos identified", puzzle:"puzzles solved", art:"birds drawn"}[b.type] || "birds spotted";
        const unlocked=have>=b.goal, card=document.createElement("div");
        card.className="badge-card"+(unlocked?" unlocked":""); card.style.setProperty("--badge-color",b.color);
        card.innerHTML=`<span class="badge-emoji">${esc(b.emoji)}</span><div class="badge-name">${esc(b.name)}</div><div class="badge-progress">${Math.min(have,b.goal)} / ${b.goal} ${unit}</div>`;
        grid.appendChild(card);
        let celebrated=false; try{ celebrated=!!sessionStorage.getItem("celebrated-"+b.id); sessionStorage.setItem("celebrated-"+b.id,"1"); }catch(e){}
        if(unlocked && !celebrated) setTimeout(()=>fireConfetti(card),150);
    });
}

// ---------- start ----------
document.addEventListener("DOMContentLoaded", async ()=>{
    startProgress(); renderModeSwitch();
    $("quiz-best").textContent=quizBest; $("puzzle-solved-count").textContent=puzzlesSolved;
    try{ const m=await (await fetch("/api/mascot")).json(); $("mascot-container").innerHTML=m.svg; $("mascot-container").addEventListener("click",pipWhistle); }catch(e){}
    loadFacts(); loadVideos(); loadWeather(32.78,-96.97); loadHoliday();
    try{
        allBirds=await (await fetch("/api/birds")).json();
        allBirds.forEach(b=>birdById[b.id]=b);
        document.querySelectorAll(".bird-total").forEach(el=>el.textContent=allBirds.length); $("bird-count").textContent=allBirds.length;
        showDailyBird();
        renderBook(); renderChecklist(); initDrawTab();
    }catch(e){ console.error("Error loading birds:",e); }
    initMap();  // after birds load, so pins can show Bird Book emojis
    const startTab=location.hash.slice(1);
    if(startTab && $("tab-"+startTab)) openTab(startTab);
});
</script>
</body>
</html>
"""

# The ChirpQuest logo ("Pip Badge"): Pip's face in a mint circle. Used in the sidebar and as the browser-tab icon.
LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-label="ChirpQuest logo">
<defs><clipPath id="logoPipHead"><circle cx="52" cy="56" r="24"/></clipPath></defs>
<circle cx="50" cy="50" r="47" fill="#ccfbf1" stroke="#0f766e" stroke-width="4"/>
<path d="M40,42 Q34,40 29,35 L35,33 Q29,29 26,23 L32,21 Q27,16 25,8 L62,36 Z" fill="#facc15" stroke="#1e293b" stroke-width="2.4" stroke-linejoin="round"/>
<circle cx="52" cy="56" r="24" fill="#fde68a"/>
<g clip-path="url(#logoPipHead)"><ellipse cx="32" cy="64" rx="14" ry="24" fill="#9ca3af"/></g>
<circle cx="52" cy="56" r="24" fill="none" stroke="#1e293b" stroke-width="2.5"/>
<circle cx="60" cy="66" r="7" fill="#fb923c"/>
<circle cx="60" cy="50" r="7.2" fill="#fff" stroke="#1e293b" stroke-width="2"/><circle cx="61.4" cy="50.8" r="4.2" fill="#0f172a"/><circle cx="63" cy="48.6" r="1.7" fill="#fff"/>
<path d="M73,52 Q83,52 81,62 L77,59 L73,63 Z" fill="#a8a29e" stroke="#1e293b" stroke-width="2" stroke-linejoin="round"/>
</svg>"""
WEB_PAGE = WEB_PAGE.replace("__LOGO__", LOGO_SVG)

# ==========================================
# 6. ROUTES
# ==========================================
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # Photo ID uploads (already shrunk in the browser)

@app.route("/")
def home():
    return Response(WEB_PAGE, mimetype="text/html")

@app.route("/favicon.svg")
def favicon():
    return Response(LOGO_SVG, mimetype="image/svg+xml")

# Bird of the Day, for the 🎬 Demo / 💾 Normal switch at the top right of the page:
#   Normal → a random bird that stays the same all day (the date is the random seed)
#   Demo   → a new random bird on every refresh
@app.route("/api/bird_of_the_day")
def get_bird_of_the_day():
    try:
        species = north_texas_species()
    except Exception as e:
        log.warning("North Texas species list failed: %s", e)
        species = []
    if not species:  # offline? fall back to the Bird Book birds
        species = [{"taxon_id": b["inat"], "name": b["name"], "sci": b["inat"], "count": None, "wiki": b["wiki_url"]} for b in TEXAS_BIRDS]
    if request.args.get("mode") == "demo":
        pick = random.choice(species)
    else:
        pick = random.Random(datetime.date.today().isoformat()).choice(species)
    try:
        photo = (fetch_taxon_photos(pick["taxon_id"]) or [{}])[0]
    except Exception as e:
        log.warning("Bird of the Day photo failed for %s: %s", pick["name"], e)
        photo = {}
    book = _book_bird_for(pick["sci"])
    return jsonify({**pick, "photo": photo.get("url"), "credit": photo.get("credit", ""),
                    "bird_id": book["id"] if book else None, "radius_km": NORTH_TEXAS_RADIUS_KM})

@app.route("/api/mascot")
def get_mascot():
    return jsonify(COCKATIEL_MASCOT)

@app.route("/api/birds")
def get_texas_birds():
    return jsonify([{**{k: v for k, v in b.items() if k != "art"}, "shape": b["art"].get("shape", "songbird")} for b in TEXAS_BIRDS])

@app.route("/api/facts")
def get_random_facts():
    if not _fact_pool or time.time() - _fact_pool_time > FACT_POOL_MAX_AGE:
        threading.Thread(target=build_fact_pool, daemon=True).start()
    if not _fact_pool:
        return jsonify({"loading": True, "facts": [{"text": t} for t in random.sample(BIRD_FACTS, 5)]})
    picks, seen = [], set()
    for fact in random.sample(_fact_pool, len(_fact_pool)):  # 5 facts about 5 different birds
        if fact["bird_id"] not in seen:
            seen.add(fact["bird_id"])
            picks.append(fact)
        if len(picks) == 5:
            break
    return jsonify({"loading": False, "facts": picks})

@app.route("/api/videos")
def get_videos():
    everything = SHOWTIME_VIDEOS + LIVE_CAMS
    with ThreadPoolExecutor(8) as ex:
        ok = list(ex.map(lambda v: video_ok(v["video_id"]), everything))
    good = [v for v, keep in zip(everything, ok) if keep]
    clips = [v for v in good if not v.get("live")]
    cams = [v for v in good if v.get("live")]
    return jsonify({"live": random.choice(cams) if cams else None, "clips": random.sample(clips, min(6, len(clips)))})

@app.route("/api/prizes")
def get_prizes():
    return jsonify(PRIZE_BADGES)

@app.route("/api/photo")
def get_photo():
    name = request.args.get("name", "")
    url = fetch_inat_photo(name) if name else None
    return jsonify({"url": url})

@app.route("/api/season")
def get_season():
    bird = BIRDS_BY_ID.get(request.args.get("bird", ""))
    if not bird:
        return jsonify({"error": "unknown bird"}), 404
    try:
        return jsonify({"months": fetch_season(bird)})
    except Exception as e:
        log.warning("Season fetch failed for %s: %s", bird["name"], e)
        return jsonify({"error": "season data unavailable"}), 502

@app.route("/api/sightings")
def get_sightings():
    try:
        lat = max(-90.0, min(90.0, float(request.args.get("lat", DFW_CENTER[0]))))
        lng = max(-180.0, min(180.0, float(request.args.get("lng", DFW_CENTER[1]))))
        days = int(request.args.get("days", 7))
    except ValueError:
        return jsonify({"error": "bad location"}), 400
    days = days if days in (1, 7, 30) else 7
    try:
        return jsonify(fetch_sightings(lat, lng, days))
    except Exception as e:
        log.warning("Sightings fetch failed: %s", e)
        return jsonify({"error": "sightings unavailable"}), 502

@app.route("/api/quiz_photo")
def get_quiz_photo():
    bird = BIRDS_BY_ID.get(request.args.get("bird", ""))
    if not bird:
        return jsonify({"error": "unknown bird"}), 404
    try:
        photos = fetch_quiz_photos(bird)
    except Exception as e:
        log.warning("Quiz photo fetch failed for %s: %s", bird["name"], e)
        photos = []
    return jsonify(random.choice(photos) if photos else {"url": None})

@app.route("/api/holiday")
def get_holiday():
    """Today's bird holiday (with a real photo) and the next one coming up. ?date=2027-05-31 previews any day."""
    try:
        day = datetime.date.fromisoformat(request.args["date"]) if request.args.get("date") else datetime.date.today()
    except ValueError:
        return jsonify({"error": "date must look like 2027-05-31"}), 400
    happening = holidays_on(day)
    today = next((h for h in happening if h.get("major", True)), None)  # the big banner + photo
    nxt_start, nxt = next_holiday(day)
    result = {"date": day.isoformat(), "today": None,
              "minor": [{"name": h["name"], "emoji": h["emoji"]} for h in happening if not h.get("major", True)],
              "next": {"name": nxt["name"], "emoji": nxt["emoji"], "date": nxt_start.isoformat(), "days": (nxt_start - day).days}}
    if today:
        photo = {}
        try:
            photos = fetch_taxon_photos(today["taxon"]) or fetch_cc_photos(today["taxon"], today["place"])
            photo = random.choice(photos) if photos else {}
        except Exception as e:
            log.warning("Holiday photo fetch failed for %s: %s", today["name"], e)
        result["today"] = {k: today.get(k) for k in ("id", "name", "emoji", "message", "link")}
        result["today"]["photo"] = photo
    return jsonify(result)

def _sound_request():
    """Which bird a /api/sound request is about: a Bird Book id (?bird=) or an iNaturalist taxon id (?taxon=)."""
    bird = BIRDS_BY_ID.get(request.args.get("bird", ""))
    if bird:
        return bird["inat"], f"bird={bird['id']}"
    t = request.args.get("taxon", "")
    return (int(t), f"taxon={t}") if t.isdigit() else (None, None)

@app.route("/api/sound")
def get_sound():
    """Pick one of the bird's top recordings at random (so it sounds a bit different each time)."""
    taxon, query = _sound_request()
    if taxon is None:
        return jsonify({"error": "unknown bird"}), 404
    try:
        sounds = fetch_sound_list(taxon)[:6]
    except Exception as e:
        log.warning("Sound list failed for %s: %s", taxon, e)
        sounds = []
    for n in random.sample(range(len(sounds)), len(sounds)):
        try:
            fetch_sound_file(sounds[n]["url"])  # make sure it downloads and isn't too big
            return jsonify({"file": f"/api/sound_file?{query}&n={n}", "credit": sounds[n]["credit"]})
        except Exception as e:
            log.warning("Skipping a recording of %s: %s", taxon, e)
    return jsonify({"file": None})

@app.route("/api/sound_file")
def get_sound_file():
    taxon, _ = _sound_request()
    n = request.args.get("n", "")
    try:
        sounds = fetch_sound_list(taxon) if taxon is not None else []
        if not (n.isdigit() and int(n) < len(sounds)):
            return jsonify({"error": "no such recording"}), 404
        ctype, data = fetch_sound_file(sounds[int(n)]["url"])
    except Exception as e:
        log.warning("Sound file failed: %s", e)
        return jsonify({"error": "recording unavailable"}), 502
    return Response(data, mimetype=ctype, headers={"Cache-Control": "max-age=86400"})

@app.route("/api/sample_photo")
def get_sample_photo():
    """A random real Texas bird photo, sent as image data so Photo ID can be tried without a camera."""
    for bird in random.sample(TEXAS_BIRDS, 3):
        try:
            photos = fetch_quiz_photos(bird)
            if not photos:
                continue
            pick = random.choice(photos)
            img = requests.get(pick["url"], headers=HTTP_HEADERS, timeout=10)
            img.raise_for_status()
            mime = img.headers.get("Content-Type", "image/jpeg").split(";")[0]
            return jsonify({"image": f"data:{mime};base64," + base64.b64encode(img.content).decode(), "credit": pick["credit"]})
        except Exception as e:
            log.warning("Sample photo failed for %s: %s", bird["name"], e)
    return jsonify({"error": "no sample photo right now"}), 502

# Photo ID has 3 kinds of pictures, picked by the kid: a real bird photo, their own drawing, or something else.
PHOTO_ID_PROMPTS = {
    "bird": (
        "You are Pip, a friendly bird expert in a birding app for kids in North Texas. Look at this photo. "
        "Name the bird species. It can be ANY bird, but birds that live in North Texas are the most likely{hint}. "
        "Answer in JSON with these keys: "
        '"is_bird" (true/false), "name" (the common English name of the bird species, or "" if it is not a bird), '
        '"confidence" (0-100, lower it if the photo is blurry, far away, or the bird is hard to see), '
        '"clues" (one sentence naming the field marks you used, like colors, beak shape or markings), '
        '"fun_fact" (one fun, true, kid-friendly sentence about this bird; if there is no bird, kindly say what you see '
        "and invite them to try a bird photo)."
    ),
    "drawing": (
        "You are Pip, a kind art teacher and bird expert in a birding app for kids. This picture is a kid's DRAWING of a bird. "
        "Decide which real bird species it looks most like{hint}, and judge how well it shows that species' real field marks "
        "(colors, shape, beak, special markings). Be encouraging, but honest: a plain bird shape with no matching colors "
        "should score low. Answer in JSON with these keys: "
        '"is_drawing" (true/false: is it a drawing of a bird?), "name" (the common English name of the species it looks like, or ""), '
        '"likeness" (0-100: how much it looks like that real species), '
        '"got_right" (one sentence: what they drew well), "tip" (one short, friendly tip to make it look even more like the real bird), '
        '"fun_fact" (one fun, true, kid-friendly sentence about that bird).'
    ),
    "other": (
        "You are Pip, a friendly cockatiel in a birding app for kids. The kid says this picture is NOT a bird photo. "
        "Answer in JSON with these keys: "
        '"what_it_is" (one fun, kid-friendly sentence describing what is in the picture), '
        '"bird_name" (if you can still spot a real bird or a bird picture anywhere in it, its common name, else ""), '
        '"fun_fact" (one short fun fact connected to what you see, ideally about birds).'
    ),
}
ART_LIKENESS_NEEDED = 60  # a drawing must score this much to count toward the Master Artist badge


def _norm_name(name):
    return re.sub(r"[^a-z]", "", (name or "").lower())


def _match_book_bird(name):
    n = _norm_name(name)
    return next((b for b in TEXAS_BIRDS if n and _norm_name(b["name"]) == n), None)


def _match_north_texas(name):
    try:
        n = _norm_name(name)
        return next((s for s in north_texas_species() if n and _norm_name(s["name"]) == n), None)
    except Exception:
        return None


@app.route("/api/identify", methods=["POST"])
def identify_photo():
    data = request.get_json(silent=True) or {}
    kind = data.get("kind") if data.get("kind") in PHOTO_ID_PROMPTS else "bird"
    match = re.match(r"data:(image/(?:jpeg|png|webp|gif));base64,([A-Za-z0-9+/=]+)$", data.get("image", ""))
    if not match:
        return jsonify({"error": "Please choose a JPG or PNG picture."}), 400
    hint = ""
    if kind in ("bird", "drawing"):
        try:  # nudge Gemini toward local birds: the ~320 species seen around North Texas
            hint = " (North Texas birds include: " + ", ".join(s["name"] for s in north_texas_species()) + ")"
        except Exception:
            pass
    prompt = PHOTO_ID_PROMPTS[kind].replace("{hint}", hint)
    result = gemini_json([{"text": prompt}, {"inline_data": {"mime_type": match[1], "data": match[2]}}],
                         max_tokens=700, timeout=30)
    if not isinstance(result, dict):
        return jsonify({"error": "Pip's AI eyes are tired right now. Try again in a minute!"}), 502
    log.info("Photo ID (%s): %s", kind, {k: v for k, v in result.items() if k in ("name", "confidence", "likeness", "bird_name")})
    if kind == "other":
        bird_name = str(result.get("bird_name", "")).strip()
        book = _match_book_bird(bird_name)
        return jsonify({"kind": "other", "what_it_is": str(result.get("what_it_is", "")), "bird_name": bird_name,
                        "fun_fact": str(result.get("fun_fact", "")), "bird_id": book["id"] if book else None})
    name = str(result.get("name", "")).strip()
    book, local = _match_book_bird(name), _match_north_texas(name)
    out = {"kind": kind, "name": name, "fun_fact": str(result.get("fun_fact", "")),
           "bird_id": book["id"] if book else None, "north_texas_count": local["count"] if local else None}
    if kind == "drawing":
        likeness = max(0, min(100, int(result.get("likeness") or 0)))
        out.update(is_drawing=bool(result.get("is_drawing")) and bool(name), likeness=likeness,
                   got_right=str(result.get("got_right", "")), tip=str(result.get("tip", "")),
                   counts_for_art=bool(book) and likeness >= ART_LIKENESS_NEEDED, likeness_needed=ART_LIKENESS_NEEDED)
    else:
        out.update(is_bird=bool(result.get("is_bird")) and bool(name), confidence=result.get("confidence", 0),
                   clues=str(result.get("clues", "")))
    return jsonify(out)

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
    threading.Thread(target=warm_caches, daemon=True).start()
    # debug=False: ChirpQuest gets shared through ngrok, and Flask's debugger
    # would let strangers run code on this laptop if an error page appeared.
    app.run(debug=False, host="127.0.0.1", port=5000, load_dotenv=False, threaded=True)
