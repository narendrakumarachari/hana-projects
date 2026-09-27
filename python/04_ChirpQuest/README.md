# 04_ChirpQuest: North Texas Bird Guide ⭐

<!-- circuit-card --> 🔌 **Circuit cards:** [ChirpQuest Bird Guide](https://narendrakumarachari.github.io/hana-projects/cards/py-chirpquest.html)

> A web app for kids about 16 North Texas birds. Pip the Cockatiel, the mascot, answers bird questions using Google Gemini AI. It also has real bird photos, a spotting checklist, bird videos and unlockable badges. It's written in Python (Flask) with all the HTML, CSS and JavaScript in the same file.

## Run it
```bat
cd C:\Users\narendra\HanaProjects\python
venv\Scripts\activate
pip install -r requirements.txt        :: first time only
python 04_ChirpQuest\chirpquest.py
```
Then open **http://127.0.0.1:5000** in a browser.

### 🔑 Gemini API key
The key is **not** in the code. It is read from **`04_ChirpQuest/.env`**:
```
GEMINI_API_KEY=your-key-here
```
- On this PC, `.env` already contains the key that used to be written in `chirpquest.py`.
- On a new PC, or after cloning from GitHub: copy `.env.example` to `.env` and paste a key. Free keys: <https://aistudio.google.com/apikey>.
- `.env` is git-ignored, so it never reaches GitHub.
- **No key?** The app still runs. Pip answers from a small built-in list (cardinal, owl, blue jay, hummingbird, hello).

## Features (the tabs in the app)
| Tab | What it does | How |
|---|---|---|
| 🏠 Welcome | Pip mascot (animated SVG), 5 random bird facts, a "play bird sound" button, and a random bird of the day | `/api/facts`; the sound is made in the browser (Web Audio) |
| 💬 Ask Pip | Chat with Pip: kid-friendly, 2–4 sentence answers | `/api/chat` → Gemini `gemini-flash-latest` with a system prompt |
| 📖 Bird Book | 16 species cards: a real Creative-Commons photo from **iNaturalist** (with an animated SVG drawing as fallback) and 2 field marks each. Tap to switch between photo and drawing | `/api/birds`, `/api/photo` (photos cached in memory) |
| ✅ Checklist | Tick off birds you've spotted, with a progress bar. Saved in the browser's `localStorage` | browser only |
| 📺 Showtime | 4 YouTube bird videos (Nat Geo Kids, Cornell Lab) | `/api/videos` |
| 🏆 Prizes | 5 badges unlocked at 1 / 4 / 8 / 12 / 16 birds spotted, with confetti | `/api/prizes` |

**The 16 birds:** Northern Cardinal, Blue Jay, Northern Mockingbird (Texas state bird), Scissor-tailed Flycatcher, Mourning Dove, Carolina Chickadee, Eastern Bluebird, Greater Roadrunner, Red-tailed Hawk, Red-bellied Woodpecker, Great Blue Heron, Great-tailed Grackle, American Robin, Tufted Titmouse, Ruby-throated Hummingbird, Barred Owl.

## Versions
| File | Date | What changed |
|---|---|---|
| `old_versions/chirpquest_v1.py` *(was `app.py`)* | Aug 27 | First version. 10–50-word answers, 400-token limit |
| `old_versions/chirpquest_v2_demo.py` *(was `demo chirpquest.py`)* | Sep 5, 8:33 pm | New Pip personality (patient expert, 2–4 complete sentences, says "still learning" instead of guessing), 800 tokens, mascot eye-blink fix |
| **`chirpquest.py`** *(was `Chirpquestbrd.py`)* | Sep 5, 9:59 pm | **Current.** Retries on server/network errors (500/502/503/504, timeouts), detects cut-off replies (`MAX_TOKENS`), 2048 tokens, 30 s timeout, fallback replies match whole words only (so "this" no longer matches "hi") |

All three share the same `.env`.

## Code review notes
- Good: clear numbered sections, API key rotation, photo caching, safe fallbacks when Gemini fails, and kid-safe instructions in the system prompt.
- ⚠️ **Chat messages are inserted into the page as raw HTML** (`innerHTML += \`…${text}…\``). Typing `<b>hi</b>` shows bold text, and a Gemini reply containing HTML would be rendered too. Use `textContent` for the message text.
- ⚠️ It logs the **full Gemini response** on every chat (`Gemini raw response: …`). That's useful while debugging, but noisy. Lower it to `log.debug`.
- `debug=True`: fine on your own PC, but don't use it on a shared network.
- `load_dotenv=False` in `app.run()` was a workaround for the empty `dotenv.py` file (now deleted). It's harmless, because the script loads `.env` itself.
- The file is about 860 lines, mostly HTML/CSS/JS in one big string. Moving the page into `templates/index.html` and `static/` would make it much easier to edit.

## To-do
- [ ] Escape chat text (use `textContent` instead of `innerHTML`).
- [ ] Change the "raw response" log line to debug level.
- [ ] Optional: split HTML/CSS/JS into `templates/` and `static/`.
- [ ] Optional: more birds, and real recorded bird calls instead of the synthesised chirp.
- [ ] Optional: link it to the Arduino/ESP32 bird projects, for example a button on the ESP32 that plays a bird call when a bird is ticked off.
