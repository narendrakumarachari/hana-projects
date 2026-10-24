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
| 🏠 Welcome | Pip mascot (click it to hear a whistle). **Bird Facts** are pulled live from Wikipedia and rewritten for kids by Gemini, each with a link to Cornell's *All About Birds*. **Bird of the Day**: a random bird from *all* ~320 wild species seen around North Texas (not just the Bird Book, and introduced birds like the European Starling count too), with a real photo, its sighting count, and an "Ask Pip about it" button. **Bird Sounds**: real recordings with a scrolling spectrogram, like Merlin's. **Birding Weather**: a 0–100 "birding score" plus sunrise and sunset. **Live Bird Map** of real bird sightings within 50 km over the last day, week or month (Bird Book birds get a teal map pin with their cartoon face; other birds get a smaller gray **?** pin; tap any pin for the photo), with a "Most-seen birds" chart and a 📍 Near me button | `/api/facts` (Wikipedia → Gemini, cached 12 h), `/api/bird_of_the_day?mode=` (iNaturalist species with ≥ 25 sightings within 150 km of DFW, cached 1 day), `/api/sightings` (iNaturalist, cached 10 min), Open-Meteo weather (browser), Leaflet + OpenStreetMap map |
| 💬 Ask Pip | Chat with Pip: kid-friendly, 2–4 sentence answers, plus quick-question buttons | `/api/chat` → Gemini (see the models below) |
| 📖 Bird Book | **73 species** (only 2 non-native ones, the very common European Starling and House Sparrow), each with a **cartoon drawing made by code**. Tap it to see a real Creative-Commons photo. Each card also has 2 field marks, a 🔊 call, a 📅 chart of when the bird is easiest to spot in Texas, a ✏️ Draw it button, and an All About Birds link. Search box plus habitat filters (🏡 Backyard, 💧 Water, 🌾 Fields & Sky, 🌙 Night) | `/api/birds`, `/api/photo`, `/api/season` (iNaturalist sightings by month ÷ all Texas bird sightings, so busy months don't skew it) |
| 📷 Photo ID | First pick **📷 A real bird**, **✏️ My drawing** or **❓ Something else**, then upload a picture (or try a sample). *Real bird:* Pip names **any** bird (not only Bird Book birds; it gets the ~320 North Texas species as a hint), says how sure it is and what clues it used, says whether the bird lives in North Texas, and offers to tick it off the checklist. *Drawing:* Pip says which species it looks like, gives a 0–100 looks-like score, what you got right and one tip. *Something else:* Pip describes the picture, and still spots any bird in it. Sample photos and drawings don't count toward badges | `/api/identify` (`kind` = bird / drawing / other) → Gemini vision (JSON answer); `/api/sample_photo` |
| 🎯 Bird Quiz | 10 questions in 3 modes: 📸 real photos, 🎨 cartoons, 🔊 sounds. Shows score, streak and best score | `/api/quiz_photo` (CC-licensed Texas photos) |
| ✏️ Draw Birds | Beginner step-by-step drawing guide for any Bird Book bird, made from its cartoon: 1 body → 2 head → 3 tail & wing → 4 eye & beak → 5 legs → 6 colors & markings. Each step is a pencil sketch with the new part in **blue**, and the last one is in full color. "Check my drawing" jumps to Photo ID | browser only (each part of a cartoon is tagged `data-step`) |
| 🧩 Bird Puzzle | A mystery bird picture (real photo or cartoon) is cut into 3×3, 4×4 or 5×5 scrambled tiles. Tap two tiles to swap them; tiles in the right spot get a ✅. "Hold to peek" shows the whole picture. When it's solved, the bird is revealed. Counts swaps and time | browser `<canvas>`; photos from `/api/quiz_photo` |
| ✅ Checklist | Tick off birds you've spotted, with a progress bar. Saved in the browser's `localStorage` | browser only |
| 📺 Showtime | **1 live bird cam + 6 random clips**, picked from 29 Cornell Lab / Nat Geo Kids videos and a new mix on every refresh. Deleted or non-embeddable videos are hidden automatically | `/api/videos` (YouTube oEmbed check) |
| 🏆 Prizes | 9 badges, easiest first: Hatchling Spotter (1 bird) · **Photo Detective** (1 Photo ID) · Fledgling Birder (5 birds) · **Puzzle Pro** (5 puzzles) · **Quiz Whiz** (8/10 or better) · **🎨 Master Artist** (10 *different* Bird Book birds drawn with a looks-like score of 60+) · Flock Leader (15) · Master Birder (30) · ChirpQuest Legend (all 73) | `/api/prizes` |

Tabs have their own links, for example `http://127.0.0.1:5000/#quiz`.

**🎬 Demo / 💾 Normal switch** (small, at the top right of every page; remembered by each browser; starts in Demo):

| | 🎬 Demo (for showing people) | 💾 Normal |
|---|---|---|
| Checklist, quiz, Photo ID and puzzle progress, so the badges | Reset every time you **refresh** the page | Saved (never reset) |
| Bird of the Day (random, any North Texas bird) | A new random bird on every refresh | A random bird that stays the same all day (the date is the random seed) |
| Live bird sightings, facts, videos | Live in both modes | Live in both modes |

How it works: Demo and Normal keep **separate saves** in the browser's `localStorage` (`chirpquest_demo_*` vs `chirpquest_*`). The demo save is wiped on every page load, so showing the demo to people never touches the real Normal progress. Switching modes swaps which save is shown. Starting Normal mode over will come with a future account system.

**Pip** is drawn in the same cartoon style as the Bird Book birds: a gray cockatiel with a swaying yellow crest (a triangle with a straight front edge and a notched back edge), a yellow face, orange cheeks and a white wing patch. Click Pip to hear a whistle.

**🎉 Bird holidays:** on a bird holiday, Pip's banner on the Welcome page changes to "Happy *holiday*!" with a fun message, confetti, and a real photo of a matching bird from iNaturalist (a curated, Creative-Commons photo with the photographer's credit). On other days the banner shows how many days until the next bird holiday. Preview any day by adding `?date=` to the address, for example `http://127.0.0.1:5000/?date=2027-05-31`.

| Holiday | When | Photo |
|---|---|---|
| 🐦 National Bird Day | Jan 5 | Northern Cardinal |
| 🐧 Penguin Awareness Day | Jan 20 | penguins |
| 📋 Great Backyard Bird Count | the 4 days ending on Presidents' Day (Feb) | Carolina Chickadee |
| 🐤 World Sparrow Day | Mar 20 | sparrows |
| 🎨 Draw a Bird Day | Apr 8 | Painted Bunting |
| 🐧 World Penguin Day | Apr 25 | penguins |
| 🌅 International Dawn Chorus Day | 1st Sunday of May | Northern Mockingbird |
| 🦢 World Migratory Bird Day | 2nd Saturday of May **and** of October | Sandhill Crane |
| 🦜 World Parrot Day | May 31 | Monk Parakeet (wild in Dallas!) |
| 🦅 American Eagle Day | Jun 20 | Bald Eagle |
| 🦉 International Owl Awareness Day | Aug 4 | Barred Owl |
| 🧹 International Vulture Awareness Day | 1st Saturday of September | Turkey Vulture |
| 🎄 Christmas Bird Count | Dec 14 – Jan 5 | Northern Cardinal |

**Minor bird days** don't take over the banner and have no photo. They just add a small line under Pip's message, "🎈 Today is National Pet Bird Day!", in place of the countdown. If a minor day falls on a major one, the line says "Today is also …".

| Minor day | When |
|---|---|
| 🦅 National Save the Eagles Day | Jan 10 |
| 🌻 National Bird-Feeding Month | all of February |
| 🐦 Bird Day (the first one was in 1894) | May 4 |
| 🌺 National Hummingbird Day | 1st Saturday of September (same day as Vulture Awareness Day) |
| 🏖️ World Shorebirds Day | Sep 6 |
| 🦜 National Pet Bird Day | Sep 17 |

To add a holiday, add one entry to `BIRD_HOLIDAYS` in `chirpquest.py` (add `"major": False` for a minor one).

**The 73 birds:** Northern Cardinal, Blue Jay, Northern Mockingbird (Texas state bird), Scissor-tailed Flycatcher, Mourning Dove, Carolina Chickadee, Eastern Bluebird, Greater Roadrunner, Red-tailed Hawk, Red-bellied Woodpecker, Great Blue Heron, Great-tailed Grackle, American Robin, Tufted Titmouse, Ruby-throated Hummingbird, Barred Owl, Painted Bunting, American Goldfinch, House Finch, Carolina Wren, Cedar Waxwing, American Crow, Red-winged Blackbird, Eastern Phoebe, Killdeer, Mallard, Great Egret, Belted Kingfisher, Turkey Vulture, Eastern Screech-Owl, Purple Martin, Yellow-rumped Warbler, European Starling, House Sparrow, White-winged Dove, Downy Woodpecker, Northern Flicker, Great Horned Owl, Cooper's Hawk, Red-shouldered Hawk, American Kestrel, Snowy Egret, Green Heron, Wood Duck, Northern Shoveler, Canada Goose, American Coot, Double-crested Cormorant, Ring-billed Gull, Barn Swallow, Eastern Meadowlark, Brown Thrasher, Dark-eyed Junco, Western Kingbird, Indigo Bunting, Brown-headed Cowbird, Chipping Sparrow, White-crowned Sparrow, Harris's Sparrow, Song Sparrow, White-throated Sparrow, Lark Sparrow, Savannah Sparrow, Dickcissel, Loggerhead Shrike, Northern Bobwhite, Upland Sandpiper, Spotted Sandpiper, Least Sandpiper, Greater Yellowlegs, Black-necked Stilt, American Avocet, Wilson's Snipe.

To add a bird, add one entry to `TEXAS_BIRDS`: its iNaturalist scientific name, colors for the cartoon (`art`) and a backup made-up call (`call`). The photos, real sounds, facts, season chart, map pins, drawing guide and quiz all work for it automatically.

**About the sounds:** every 🔊 button plays a **real recording**, picked at random from the bird's 6 best-rated Creative-Commons recordings on iNaturalist (`/api/sound`). The server passes the audio through (`/api/sound_file`), because a browser may only analyze audio from its own website, and the spectrogram analyzes exactly what's playing. Playback is capped at 10 seconds and loudness is evened out, and the recordist is credited under the spectrogram and in a small corner note. In the quiz's Sound mode the note doesn't name the bird. If a recording can't load (for example offline), ChirpQuest falls back to its old made-up Web Audio call for that bird. Pip's whistle is still made-up.

**Gemini models** (`GEMINI_MODELS`) are tried in order: `gemini-3.1-flash-lite` (the fastest, about 1 s), then `gemini-3.5-flash-lite`, then `gemini-flash-lite-latest`. If one is busy (503), gone (404) or slow, the next one is tried.

**Data sources (all free, no extra keys):** iNaturalist API (photos, sightings, seasons), Wikipedia API (facts), Open-Meteo (weather), OpenStreetMap tiles, YouTube embeds (`youtube-nocookie.com`).

## Versions
| File | Date | What changed |
|---|---|---|
| `old_versions/chirpquest_v1.py` *(was `app.py`)* | Aug 27 | First version. 10–50-word answers, 400-token limit |
| `old_versions/chirpquest_v2_demo.py` *(was `demo chirpquest.py`)* | Sep 5, 8:33 pm | New Pip personality (patient expert, 2–4 complete sentences, says "still learning" instead of guessing), 800 tokens, mascot eye-blink fix |
| **`chirpquest.py`** *(was `Chirpquestbrd.py`)* | Oct 24 | **Current.** 73 birds with cartoon art, real recorded calls, Draw Birds guides, Photo ID for photos/drawings/anything, live map, Wikipedia facts, Photo ID, Bird Quiz, spectrogram, birding weather, season charts, shuffled videos + live cam, Gemini model fallback list. *From the Sep 5, 9:59 pm version:* Retries on server/network errors (500/502/503/504, timeouts), detects cut-off replies (`MAX_TOKENS`), 2048 tokens, 30 s timeout, fallback replies match whole words only (so "this" no longer matches "hi") |

All three share the same `.env`.

## Code review notes
- Good: clear numbered sections, API key rotation, photo caching, safe fallbacks when Gemini fails, and kid-safe instructions in the system prompt.
- ✅ *(fixed Oct 24: chat and all API text now use `textContent` / `esc()`)* ~~Chat messages are inserted into the page as raw HTML~~ (`innerHTML += \`…${text}…\``). Typing `<b>hi</b>` shows bold text, and a Gemini reply containing HTML would be rendered too. Use `textContent` for the message text.
- ✅ *(fixed Oct 24: now `log.debug`)* It logged the **full Gemini response** on every chat (`Gemini raw response: …`). That's useful while debugging, but noisy. Lower it to `log.debug`.
- `debug=False`, because the app gets shared through ngrok.
- `load_dotenv=False` in `app.run()` was a workaround for the empty `dotenv.py` file (now deleted). It's harmless, because the script loads `.env` itself.
- The file is about 1,950 lines, mostly HTML/CSS/JS in one big string (now a raw string served as-is, not a Jinja template). Moving the page into `templates/index.html` and `static/` would make it much easier to edit.

## To-do
- [x] Escape chat text (use `textContent` instead of `innerHTML`).
- [x] Change the "raw response" log line to debug level.
- [ ] Optional: split HTML/CSS/JS into `templates/` and `static/`.
- [x] More birds (73 now).
- [x] Real recorded bird calls (from iNaturalist) instead of the made-up ones.
- [x] New logo: the **Pip Badge** (Pip's face in a mint circle), also used as the browser-tab icon (`/favicon.svg`). The "Bird Map Pin" idea became the map's sighting pins. Runner-up idea: "Lone Star Lookout" (a cardinal on the Texas star).
- [ ] Optional: link it to the Arduino/ESP32 bird projects, for example a button on the ESP32 that plays a bird call when a bird is ticked off.
