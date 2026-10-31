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

### 👑 Main password (for the ChirpQuest team only)
**👪 Manage Accounts** (grown-ups only) has two kinds of passwords: each family's own parent password (see 👨‍👩‍👧 Families below), and the **main password** for the ChirpQuest team, which unlocks everything (👪 Manage Accounts → 👑 For the ChirpQuest team only). The first time, ChirpQuest asks the team to **make** the main password, right on the website. Rules that keep it safe:
- It can only be made when there isn't one yet, and only on **the computer running ChirpQuest** (never through a shared ngrok link), so a stranger can't grab it first.
- Changing it (🔑 Change main password, inside Manage Accounts) needs the current one.
- It's stored as a salted hash in `chirpquest_accounts.db`, never as the password itself. (In the code it's called the "owner" or "parent" password.)

**Forgot it?** Add a line `PARENT_PASSWORD=a-new-password` to `.env` and restart ChirpQuest. That password always works too, so you can get back in and change the main password.

## Features (the tabs in the app)
| Tab | What it does | How |
|---|---|---|
| 🏠 Welcome | Pip mascot (click it to hear a whistle). **Bird Facts** are pulled live from Wikipedia and rewritten for kids by Gemini, each with a link to Cornell's *All About Birds*. **Bird of the Day**: a random bird from *all* ~300 wild species seen around North Texas (not just the Bird Book). Introduced birds count only if they really live wild here (House Sparrow, European Starling, Rock Pigeon, Eurasian Collared-Dove, Mallard, Monk Parakeet: `WILD_INTRODUCED_OK`), so escaped pets and farm birds like budgies, chickens, peafowl and Muscovy Ducks are left out, with a real photo, its sighting count, and an "Ask Pip about it" button. **Bird Sounds**: real recordings with a scrolling spectrogram, like Merlin's. **Birding Weather**: a 0–100 "birding score" plus sunrise and sunset. **Live Bird Map** of real bird sightings within 50 km over the last day, week or month (Bird Book birds get a teal map pin with their cartoon face; other birds get a smaller gray **?** pin; tap any pin for the photo). While the Welcome page is open, the map checks for new sightings **every 10 seconds** (it only redraws when something changed, and never while a pin's popup is open). Besides the newest 200 sightings, every Bird Book bird seen in the chosen time gets at least one pin (its latest sighting), collected slowly in the background and refreshed every 10 minutes, with a "Most-seen birds" chart and a 📍 Near me button | `/api/facts` (Wikipedia → Gemini, cached 12 h), `/api/bird_of_the_day?mode=` (iNaturalist species with ≥ 25 sightings within 150 km of DFW, cached 1 day), `/api/sightings` (iNaturalist, cached 10 s), Open-Meteo weather (browser), Leaflet + OpenStreetMap map |
| 💬 Ask Pip | Chat with Pip: kid-friendly, 2–4 sentence answers, plus quick-question buttons. Pip knows exactly which 95 birds are in the Bird Book (and says so kindly when a bird isn't). In 💾 Normal mode Pip also knows your sightings and badges, so you can ask "Which birds haven't I seen yet?" | `/api/chat` → Gemini (see the models below); Pip's instructions come from `pip_instructions()` |
| 🔎 Research this bird | A **🔎 Research this bird** button under every Bird Book bird (and on Bird of the Day and Photo ID results) opens a research page: real photos, 🔊 call, what it is, how to recognize it, how big it is (compared with a robin, sparrow, pigeon or crow), what it eats, where it nests, how it's doing in the wild (IUCN Red List), when to see it in Texas (season chart), and a map of sightings near DFW from the last 30 days. **Every fact says its source** with a link (Wikipedia, iNaturalist, or the ChirpQuest season chart); Pip only uses what those sources say. Also Pip's tips for finding one, "Ask Pip more" questions, and links to All About Birds, Audubon, Wikipedia and iNaturalist. **✍️ My report:** write your own report (saved on this computer) and press 🧐 *Pip, give me tips*: Pip says what's good, what's missing, which facts need a source and how to say things more clearly, but **helps with the draft, never the final**. Ask Pip won't write reports either | `/api/research` (Wikipedia + iNaturalist + season data → Gemini, cached 6 h), `/api/research/tips` (one every 10 s) |
| 📖 Bird Book | **95 species** (only 4 non-native ones, all very common: European Starling, House Sparrow, Rock Pigeon and Eurasian Collared-Dove), each with a **cartoon drawing made by code**. Tap it to see a real Creative-Commons photo. Each card also has 2 field marks, a 🔊 call, a 📅 chart of when the bird is easiest to spot in Texas, a ✏️ Draw it button, and an All About Birds link. Search box plus habitat filters (🏡 Backyard, 💧 Water, 🌾 Fields & Sky, 🌙 Night). The birds people see most in Texas **this month** come first (the Checklist uses the same order), and the order changes by itself every month (`/api/this_month`) | `/api/birds`, `/api/photo`, `/api/season` (iNaturalist sightings by month ÷ all Texas bird sightings, so busy months don't skew it) |
| 📷 Photo ID | First pick **📷 A real bird**, **✏️ My drawing** or **❓ Something else**, then upload a picture (or try a sample). *Real bird:* Pip names **any** bird (not only Bird Book birds; it gets the ~320 North Texas species as a hint), says how sure it is and what clues it used, says whether the bird lives in North Texas, and offers to tick it off the checklist. *Drawing:* Pip says which species it looks like, gives a 0–100 looks-like score, what you got right and one tip. *Something else:* Pip describes the picture, and still spots any bird in it. Sample photos and drawings don't count toward badges | `/api/identify` (`kind` = bird / drawing / other) → Gemini vision (JSON answer); `/api/sample_photo` |
| 🎯 Bird Quiz | 3 modes: 📸 real photos (10 questions), 🎨 cartoons (10), 🔊 sounds (8 real recordings). Shows score, streak and best score. Every perfect 8/8 Sound quiz counts toward the 👂 Owl Ears badge | `/api/quiz_photo` (CC-licensed Texas photos) |
| ✏️ Draw Birds | Beginner step-by-step drawing guide for any Bird Book bird, made from its cartoon: 1 body → 2 head → 3 tail & wing → 4 eye & beak → 5 legs → 6 colors & markings. Each step is a pencil sketch with the new part in **blue**, and the last one is in full color. "Check my drawing" jumps to Photo ID | browser only (each part of a cartoon is tagged `data-step`) |
| 🧩 Bird Puzzle | A mystery bird picture (real photo or cartoon) is cut into 3×3, 4×4 or 5×5 scrambled tiles. Tap two tiles to swap them; tiles in the right spot get a ✅. "Hold to peek" shows the whole picture. When it's solved, the bird is revealed. Counts swaps and time | browser `<canvas>`; photos from `/api/quiz_photo` |
| ✅ Checklist | 🎬 Demo: tick off birds you've spotted. 💾 Normal: tap **👀 I saw one!** for every sighting (counts like "Seen 3×"), saved to your account. Progress bar plus "different birds spotted" and "sightings in all" | `/api/sighting`, `/api/sighting/undo` (Normal only) |
| 🐦 Bird Count | A **live birding event** a parent starts in 👪 Manage Accounts (30 minutes up to a weekend; one at a time; a parent can end it early). While it's on, every 💾 Normal-mode player's sightings count (from this tab or ✅ Checklist). **Score = different birds** logged during the count, more sightings breaks a tie, and kids with the same score share a place. A live leaderboard and a **chat about birds**: 🧐 Pip checks every message before anyone sees it, sends only bird messages, makes them kid-friendly in the kid's own voice, and takes out names, schools, streets, links and phone numbers (a message asking to call or meet up isn't sent). Messages Pip didn't send are explained only to the sender, and the text stays in the box to fix. When it ends: 🥇🥈🥉 badges for the top 3 and 📋 Bird Counter for everyone who logged a bird. The menu shows a red **LIVE** tag; results stay up for a week. 🎬 Demo visitors can watch but not join | `/api/count` (checked every 4 s while the tab is open), `/api/count/chat` (one message every 4 s; Pip uses the fast `FAST_MODELS`), `/api/parent/count/start`, `/api/parent/count/end` |
| 📰 Events & News | **Real bird events near you**, soonest first, up to 3 months ahead: bird walks, bird counts (like the Christmas Bird Count), Bird Bingo and family programs at the **Trinity River Audubon Center** (Dallas) and **Dogwood Canyon Audubon Center** (Cedar Hill), read live from audubon.org (yoga and tree walks are left out), plus the **Heard Museum's Second Saturday Bird Walks** (McKinney, Sep–Jun, 8 AM, worked out from its schedule, marked "check the page before you go"). Pick a town (Plano, Allen, Frisco, Dallas… 18 towns) or 📍 Near me, a distance, and "Family & kids only". Each event shows when, where, how far away, and a link to its real page. **🗞️ Bird news:** Google News headlines about birds around DFW from the last 30 days; Pip keeps only kid-friendly stories about real birds (no Eagles football or Larry Bird!) and adds a one-sentence kid summary | `/api/events` (cached 6 h), `/api/news` (cached 3 h). Distances are worked out in the browser, so 📍 Near me never leaves your computer |
| 📺 Showtime | **1 live bird cam + 6 random clips**, picked from 29 Cornell Lab / Nat Geo Kids videos and a new mix on every refresh. Deleted or non-embeddable videos are hidden automatically | `/api/videos` (YouTube oEmbed check) |
| 🏆 Prizes | 14 badges, easiest first: Hatchling Spotter (1 bird) · **Photo Detective** (1 Photo ID) · Fledgling Birder (5 birds) · **Puzzle Pro** (5 puzzles) · **👂 Owl Ears** (5 perfect 8/8 Sound quizzes) · **Quiz Whiz** (a best score of 8+) · **🎨 Master Artist** (10 *different* Bird Book birds drawn with a looks-like score of 60+) · Flock Leader (15) · Master Birder (30) · ChirpQuest Legend (all 95), plus 4 🐦 Bird Count badges (💾 Normal): 📋 Bird Counter (logged a bird in a count) · 🥉 Bronze · 🥈 Silver · 🥇 Gold Spotter (3rd, 2nd, 1st place) | `/api/prizes` |

**Menu order** (Hana's): Welcome, Ask Pip, Bird Book, Checklist, Photo ID, Bird Quiz, Bird Puzzle, Draw Birds, Showtime, Events & News, Bird Count, Prizes. 🔎 Research has no menu button; it opens from the Bird Book.

Tabs have their own links, for example `http://127.0.0.1:5000/#quiz`.

**🎬 Demo / 💾 Normal switch** (small, at the top right of every page; remembered by each browser; starts in Demo):

| | 🎬 Demo (for showing people) | 💾 Normal |
|---|---|---|
| Account | Not needed | **Username + password** (👤 button at the top right) |
| Checklist, quiz, Photo ID and puzzle progress, so the badges | Kept only in the open page: reset every time you **refresh** | Saved to your account on the ChirpQuest server |
| ✅ Checklist | Tick and untick boxes freely | **👀 I saw one!** Every tap is one more sighting ("Seen 3×"), so you can log the same bird again and again. A wrong tap can be undone for 2 minutes |
| Bird Book & Checklist order | Most seen in Texas this month | Same, **plus the birds you saw most this month** (see below) |
| 💬 Pip knows | The Bird Book (which 95 birds are in it) | The Bird Book **and** your sightings and badges ("Which birds haven't I seen yet?") |
| Bird of the Day (random, any North Texas bird) | A new random bird on every refresh | A random bird that stays the same all day (the date is the random seed) |
| ⏱️ Daily time limit | None | Whatever a parent set in Manage Accounts |
| Live bird sightings, facts, videos | Live in both modes | Live in both modes |

**Accounts** (`/api/account/*`): sign up, log in, log out, change username, change password. Usernames are 3–20 letters, numbers or `_`; passwords are 6+ characters. Passwords are stored only as salted hashes (Werkzeug's scrypt), 5 wrong passwords in 5 minutes make that username wait, and changing a password logs that account out everywhere else. Everything is saved in `chirpquest_accounts.db` (SQLite, next to `chirpquest.py`, git-ignored). Kids can't delete accounts; only the ChirpQuest team can.

**👨‍👩‍👧 Families** (so parental controls work when ChirpQuest is shared through ngrok): any grown-up can make a family in 👪 Manage Accounts → 🏠 New family? (a family name + its own parent password). They get a **6-character family code** (like `G4DA2L`), and kids join by typing it when they sign up, or later in 👤 → 👨‍👩‍👧 Join a family. A kid can be in one family and can't leave by themselves. Each family's parent unlocks Manage Accounts with their family name + parent password and **only sees their own kids** (`/api/family/*`, `/api/account/join_family`).

| In 👪 Manage Accounts | 👨‍👩‍👧 Family parent (own kids only) | 👑 ChirpQuest team (main password) |
|---|---|---|
| See accounts | Their kids | Every account and family |
| ⏱️ Time limit, 🚫 Sections, 🏅 Badges, 🔒 Lock screen, 🔑 New password | ✅ | ✅ |
| 🚪 Take a kid out of a family | ✅ | ✅ |
| 🗑️ Delete an account | ❌ | ✅ |
| 🐦 Start or end a Bird Count | ❌ | ✅ |
| Give a family a new parent password, or delete a family (its kids keep their accounts) | ❌ | ✅ |

**👪 Manage Accounts** (grown-ups only; the link is in the 👤 window) lists the accounts (birds, sightings, minutes played today) and lets a grown-up:
- set a **⏱️ daily time limit**: type the minutes (anything under 30 becomes 30, the most is 24 hours), or pick **Unlimited**;
- **🐦 Bird Count** (ChirpQuest team only): start one for every player (name + how long), or end it early;
- **🚫 Sections:** turn off parts of ChirpQuest for one kid (Ask Pip, Bird Book, 🔎 Research, Checklist, Photo ID, Quiz, Puzzle, Draw, Showtime, Events & News, Bird Count, Prizes). They show a 🔒 in the menu and won't open, and the server blocks them too. 🏠 Welcome always stays on;
- **🏅 Badges:** take away a badge a kid didn't really earn (only badges they've reached can be ticked), or give it back. A taken-away badge shows "🚫 Taken away by a grown-up" and stays locked, even if the kid keeps logging birds, until a parent gives it back. Pip knows about it too;
- **🔒 Lock screen:** pause one kid's ChirpQuest with a message (up to 200 characters, like "Dinner time! 🍝"). Their page checks every 10 seconds, so the lock shows up quickly, and it stays until a parent presses 🔓 Unlock screen;
- give a new password to a kid who forgot theirs;
- delete an account and all of its progress (ChirpQuest team only; it asks once more first).
It locks again when you close it, or after 15 minutes.

Parent rules (sections, lock, badges) and time limits only count in **💾 Normal mode**, for **the account they were set for**. 🎬 Demo mode and every other kid's account work like normal (`/api/my_controls`, `/api/parent/controls`).

**🧐 Pip checks every sighting:** if a kid logs a bird that's almost never in Texas this month (this month *and* the months just before and after have under 2% of the sightings of its best month, like a Painted Bunting in January), Pip looks up iNaturalist sightings near DFW from the last 30 days. If at least 3 people reported one, it counts, with a "Wow, rare find!" note. If not, Pip blocks it and says when that bird is usually seen, and suggests 📷 Photo ID. Birds arriving or leaving (like Harris's Sparrows in late October) are never blocked. Works for 🎬 Demo ticks and 💾 Normal sightings (`/api/sighting_check`, `pip_sighting_check()`).

**⏱️ Time limits:** while someone is logged in and the page is showing, each minute counts toward today's limit (`/api/playtime`; two open tabs still count only once). The top bar shows "⏱️ 25 min left today", with a warning at 5 minutes. When time's up, a "Time's up for today" screen covers that kid's 💾 Normal mode until tomorrow or until a parent gives more time (then press 🔄 Check again). Sightings, saving progress, Pip and the Bird Count chat are blocked on the server too. 🎬 Demo mode isn't timed.

**Order in 💾 Normal mode:** each bird gets its Texas season score for this month (0 to 1; 1 = the most-seen bird in Texas) plus up to **0.5** for how often *you* logged it in this month (`KID_SIGHTING_WEIGHT`). So the very common birds stay on top, but in the rest of the list, where season scores are close together, the birds you really see move up. A bird that's common in Texas this month but never shows up near you slowly gets passed by birds you do see. Example from testing: a Cattle Egret ranked #61 by season, logged 6 times, moved to #7. The order updates when you open the Bird Book or Checklist.

**Pip** is drawn in the same cartoon style as the Bird Book birds: a gray cockatiel with a swaying yellow crest (a triangle with a straight front edge and a notched back edge), a yellow face, orange cheeks and a white wing patch. Click Pip on the Welcome page to jump to 💬 Ask Pip, where Pip introduces himself and suggests things to try.

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

**The 95 birds:** Northern Cardinal, Blue Jay, Northern Mockingbird (Texas state bird), Scissor-tailed Flycatcher, Mourning Dove, Carolina Chickadee, Eastern Bluebird, Greater Roadrunner, Red-tailed Hawk, Red-bellied Woodpecker, Great Blue Heron, Great-tailed Grackle, American Robin, Tufted Titmouse, Ruby-throated Hummingbird, Barred Owl, Painted Bunting, American Goldfinch, House Finch, Carolina Wren, Cedar Waxwing, American Crow, Red-winged Blackbird, Eastern Phoebe, Killdeer, Mallard, Great Egret, Belted Kingfisher, Turkey Vulture, Eastern Screech-Owl, Purple Martin, Yellow-rumped Warbler, European Starling, House Sparrow, White-winged Dove, Downy Woodpecker, Northern Flicker, Great Horned Owl, Cooper's Hawk, Red-shouldered Hawk, American Kestrel, Snowy Egret, Green Heron, Wood Duck, Northern Shoveler, Canada Goose, American Coot, Double-crested Cormorant, Ring-billed Gull, Barn Swallow, Eastern Meadowlark, Brown Thrasher, Dark-eyed Junco, Western Kingbird, Indigo Bunting, Brown-headed Cowbird, Chipping Sparrow, White-crowned Sparrow, Harris's Sparrow, Song Sparrow, White-throated Sparrow, Lark Sparrow, Savannah Sparrow, Dickcissel, Loggerhead Shrike, Northern Bobwhite, Upland Sandpiper, Spotted Sandpiper, Least Sandpiper, Greater Yellowlegs, Black-necked Stilt, American Avocet, Wilson's Snipe, Rock Pigeon (Rock Dove), Black-bellied Whistling-Duck, American White Pelican, Pied-billed Grebe, Blue-winged Teal, Bufflehead, Ruddy Duck, Cattle Egret, Yellow-crowned Night Heron, Mississippi Kite, Black Vulture, Osprey, Northern Harrier, Eurasian Collared-Dove, Blue-gray Gnatcatcher, Ruby-crowned Kinglet, Bewick's Wren, Yellow-bellied Sapsucker, Hermit Thrush, Summer Tanager, Cliff Swallow, Great Crested Flycatcher.

To add a bird, add one entry to `TEXAS_BIRDS`: its iNaturalist scientific name, colors for the cartoon (`art`) and a backup made-up call (`call`). The photos, real sounds, facts, season chart, map pins, drawing guide and quiz all work for it automatically.

**About the sounds:** every 🔊 button plays a **real recording**, picked at random from the bird's 6 best-rated Creative-Commons recordings on iNaturalist (`/api/sound`). The server passes the audio through (`/api/sound_file`), because a browser may only analyze audio from its own website, and the spectrogram analyzes exactly what's playing. Playback is capped at 10 seconds and loudness is evened out, and the recordist is credited under the spectrogram and in a small corner note. In the quiz's Sound mode the note doesn't name the bird. If a recording can't load (for example offline), ChirpQuest falls back to its old made-up Web Audio call for that bird. Pip's whistle is still made-up.

**Gemini models** (`GEMINI_MODELS`) are tried in order: `gemini-3.8-flash` (the newest, about 20 s), then `gemini-3.6-flash` (about 3 s), then `gemini-3.1-flash-lite` (about 2 s). If one is busy (503), gone (404) or slow, the next one is tried. Pip's chat and Photo ID use these (with `gemini-3.5-flash-lite` as the last backup). Quick jobs (checking a Bird Count message, picking news, the background fact writer) use the fast `FAST_MODELS` (`gemini-3.1-flash-lite`, `gemini-3.5-flash-lite`, `gemini-flash-lite-latest`, then `gemini-3.6-flash`; each model has its own free limit). For about a minute after ChirpQuest starts, the fact writer uses up the free per-minute limit, so Pip may say "try again in a minute".

**Being polite to iNaturalist:** every iNaturalist request goes through `inat_get()`, which sends at most one request per second (iNaturalist asks apps to stay around 60 a minute) and waits and retries if iNaturalist answers "429 too many requests". Background jobs pause 1.5 s between calls so the map stays fast. Season data is saved to `season_cache.json` (git-ignored) for 30 days, so restarting the website doesn't download it all again.

**Data sources (all free, no extra keys):** iNaturalist API (photos, sightings, seasons), Wikipedia API (facts), Open-Meteo (weather), OpenStreetMap tiles, YouTube embeds (`youtube-nocookie.com`), audubon.org's Texas events calendar, the Heard Museum's bird-walk page, Google News search (RSS).

## Versions
| File | Date | What changed |
|---|---|---|
| `old_versions/chirpquest_v1.py` *(was `app.py`)* | Aug 27 | First version. 10–50-word answers, 400-token limit |
| `old_versions/chirpquest_v2_demo.py` *(was `demo chirpquest.py`)* | Sep 5, 8:33 pm | New Pip personality (patient expert, 2–4 complete sentences, says "still learning" instead of guessing), 800 tokens, mascot eye-blink fix |
| **`chirpquest.py`** *(was `Chirpquestbrd.py`)* | Oct 24 | **Current.** 95 birds, Owl Ears badge, live map refresh, with cartoon art, real recorded calls, Draw Birds guides, Photo ID for photos/drawings/anything, live map, Wikipedia facts, Photo ID, Bird Quiz, spectrogram, birding weather, season charts, shuffled videos + live cam, Gemini model fallback list. *From the Sep 5, 9:59 pm version:* Retries on server/network errors (500/502/503/504, timeouts), detects cut-off replies (`MAX_TOKENS`), 2048 tokens, 30 s timeout, fallback replies match whole words only (so "this" no longer matches "hi") |

All three share the same `.env`.

## Code review notes
- Good: clear numbered sections, API key rotation, photo caching, safe fallbacks when Gemini fails, and kid-safe instructions in the system prompt.
- ✅ *(fixed Oct 24: chat and all API text now use `textContent` / `esc()`)* ~~Chat messages are inserted into the page as raw HTML~~ (`innerHTML += \`…${text}…\``). Typing `<b>hi</b>` shows bold text, and a Gemini reply containing HTML would be rendered too. Use `textContent` for the message text.
- ✅ *(fixed Oct 24: now `log.debug`)* It logged the **full Gemini response** on every chat (`Gemini raw response: …`). That's useful while debugging, but noisy. Lower it to `log.debug`.
- `debug=False`, because the app gets shared through ngrok.
- `load_dotenv=False` in `app.run()` was a workaround for the empty `dotenv.py` file (now deleted). It's harmless, because the script loads `.env` itself.
- The file is about 3,300 lines, mostly HTML/CSS/JS in one big string (now a raw string served as-is, not a Jinja template). Moving the page into `templates/index.html` and `static/` would make it much easier to edit.

## To-do

### ✅ Before we start next time
1. Get the latest code: `git pull` (or clone the repo again).
2. Make sure `04_ChirpQuest/.env` exists and has a working `GEMINI_API_KEY`. Test the key first; if it's broken, get a new one at <https://aistudio.google.com/apikey> and change it **only in `.env`**, never in the code.
3. Run it: `python 04_ChirpQuest\chirpquest.py` and open <http://127.0.0.1:5000>.

### 🎯 Next up (planned Oct 24, 2026)

**1. 🐦 More birds**
- Keep adding common North Texas birds (95 now). Check each one's sighting count near DFW first, and only add non-native birds if they're *extremely* common.
  - Already checked, but seen less often: Inca Dove (~440 sightings near DFW), Chimney Swift (~340), Horned Lark (~70).
  - Ideas to check: Gadwall, American Wigeon, Northern Pintail, Lesser Scaup, Snow Goose, Little Blue Heron, Black-crowned Night Heron, White Ibis, Neotropic Cormorant, Franklin's Gull, Forster's Tern, Red-headed Woodpecker, Ladder-backed Woodpecker, Eastern & Spotted Towhee, Orange-crowned Warbler, Common Yellowthroat, Barn Owl, Wild Turkey.
- **Maybe:** a "My Research Notebook" where kids save facts and notes from 🔎 Research, then print them as a one-page report for school.

**2. 🏅 More badges** *(added Oct 28, 2026)*
- The 4 Bird Count badges are done. More ideas: seasons (spotted a winter-only bird, a summer-only bird), habitats (5 water birds, 3 night birds), streaks (logged birds 7 days in a row), and research (finished a "Research this bird" page).

**3. 🔎 Small Bird Book upgrades for real birders** *(added Oct 30, 2026)*
- Tiny things that make a big difference: the **scientific name** on every card (like *Cardinalis cardinalis*), and **identification details**: size ("a bit smaller than a robin"), male vs. female vs. young, look-alike birds and how to tell them apart, and where to look (treetops, ground, water).

**4. 🤖 Train our own AI model** *(added Oct 30, 2026)*
- Make ChirpQuest's own AI, so it needs less (or no) Gemini key. Ideas: a **bird photo or bird sound recognizer** for the Bird Book birds (start with Google's Teachable Machine, no code), or a tiny model written from scratch in Python. Small models train on this PC; bigger ones can use a rented GPU (Google Colab, RunPod), set up by a grown-up.

**5. 📖 Bird Book pages** *(added Oct 30, 2026)*
- Add pagination to the website for the bird book. This is going to make it easier for navigation and more kid-friendly. Also useful for quickly flipping through pages when you find a bird that might fly away.

**6. 🔒 Keep the main password off ngrok** *(added Oct 30, 2026)*
- Make sure that ngrok users can't even see the login screen for the main password and stuff. This is going to make sure that the privacy of the website stays in the main computer's hands. And it also prevents people from touching other people's badges and bird sightings, which could make them very worried.

**7. 🗺️ ChirpQuest for more places** *(added Oct 30, 2026)*
- Make ChirpQuest for all of Texas, not just North Texas. This could help kids all Texas-wide.
- OR make it for all states, and you can select your state, which helps kids all across the United States.

### 💭 Maybe later
- **3. Demo tour** *(probably not)*: in 🎬 Demo mode, every refresh shows a short "how to use ChirpQuest" walkthrough with Pip pointing at each part, plus a Skip button.
- **Season data by place:** the season charts and the "most seen this month" order use all of Texas right now. They could use North Texas only, or wherever 📍 Near me is.
- **Code cleanup:** split the HTML/CSS/JS out of `chirpquest.py` into `templates/` and `static/` files.
