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

### 👪 Parent password
**👪 Manage Accounts** (parents only) is locked with a parent password. The first time someone opens Manage Accounts, ChirpQuest asks a parent to **make** one, right on the website. Rules that keep it safe:
- It can only be made when there isn't one yet, and only on **the computer running ChirpQuest** (never through a shared ngrok link), so a stranger can't grab it first.
- Changing it (🔑 Change parent password, inside Manage Accounts) needs the current one.
- It's stored as a salted hash in `chirpquest_accounts.db`, never as the password itself.

**Forgot it?** Add a line `PARENT_PASSWORD=a-new-password` to `.env` and restart ChirpQuest. That password always works too, so you can get back in and change the parent password.

## Features (the tabs in the app)
| Tab | What it does | How |
|---|---|---|
| 🏠 Welcome | Pip mascot (click it to hear a whistle). **Bird Facts** are pulled live from Wikipedia and rewritten for kids by Gemini, each with a link to Cornell's *All About Birds*. **Bird of the Day**: a random bird from *all* ~300 wild species seen around North Texas (not just the Bird Book). Introduced birds count only if they really live wild here (House Sparrow, European Starling, Rock Pigeon, Eurasian Collared-Dove, Mallard, Monk Parakeet: `WILD_INTRODUCED_OK`), so escaped pets and farm birds like budgies, chickens, peafowl and Muscovy Ducks are left out, with a real photo, its sighting count, and an "Ask Pip about it" button. **Bird Sounds**: real recordings with a scrolling spectrogram, like Merlin's. **Birding Weather**: a 0–100 "birding score" plus sunrise and sunset. **Live Bird Map** of real bird sightings within 50 km over the last day, week or month (Bird Book birds get a teal map pin with their cartoon face; other birds get a smaller gray **?** pin; tap any pin for the photo). While the Welcome page is open, the map checks for new sightings **every 10 seconds** (it only redraws when something changed, and never while a pin's popup is open). Besides the newest 200 sightings, every Bird Book bird seen in the chosen time gets at least one pin (its latest sighting), collected slowly in the background and refreshed every 10 minutes, with a "Most-seen birds" chart and a 📍 Near me button | `/api/facts` (Wikipedia → Gemini, cached 12 h), `/api/bird_of_the_day?mode=` (iNaturalist species with ≥ 25 sightings within 150 km of DFW, cached 1 day), `/api/sightings` (iNaturalist, cached 10 s), Open-Meteo weather (browser), Leaflet + OpenStreetMap map |
| 💬 Ask Pip | Chat with Pip: kid-friendly, 2–4 sentence answers, plus quick-question buttons. Pip knows exactly which 95 birds are in the Bird Book (and says so kindly when a bird isn't). In 💾 Normal mode Pip also knows your sightings and badges, so you can ask "Which birds haven't I seen yet?" | `/api/chat` → Gemini (see the models below); Pip's instructions come from `pip_instructions()` |
| 📖 Bird Book | **95 species** (only 4 non-native ones, all very common: European Starling, House Sparrow, Rock Pigeon and Eurasian Collared-Dove), each with a **cartoon drawing made by code**. Tap it to see a real Creative-Commons photo. Each card also has 2 field marks, a 🔊 call, a 📅 chart of when the bird is easiest to spot in Texas, a ✏️ Draw it button, and an All About Birds link. Search box plus habitat filters (🏡 Backyard, 💧 Water, 🌾 Fields & Sky, 🌙 Night). The birds people see most in Texas **this month** come first (the Checklist uses the same order), and the order changes by itself every month (`/api/this_month`) | `/api/birds`, `/api/photo`, `/api/season` (iNaturalist sightings by month ÷ all Texas bird sightings, so busy months don't skew it) |
| 📷 Photo ID | First pick **📷 A real bird**, **✏️ My drawing** or **❓ Something else**, then upload a picture (or try a sample). *Real bird:* Pip names **any** bird (not only Bird Book birds; it gets the ~320 North Texas species as a hint), says how sure it is and what clues it used, says whether the bird lives in North Texas, and offers to tick it off the checklist. *Drawing:* Pip says which species it looks like, gives a 0–100 looks-like score, what you got right and one tip. *Something else:* Pip describes the picture, and still spots any bird in it. Sample photos and drawings don't count toward badges | `/api/identify` (`kind` = bird / drawing / other) → Gemini vision (JSON answer); `/api/sample_photo` |
| 🎯 Bird Quiz | 3 modes: 📸 real photos (10 questions), 🎨 cartoons (10), 🔊 sounds (8 real recordings). Shows score, streak and best score. Every perfect 8/8 Sound quiz counts toward the 👂 Owl Ears badge | `/api/quiz_photo` (CC-licensed Texas photos) |
| ✏️ Draw Birds | Beginner step-by-step drawing guide for any Bird Book bird, made from its cartoon: 1 body → 2 head → 3 tail & wing → 4 eye & beak → 5 legs → 6 colors & markings. Each step is a pencil sketch with the new part in **blue**, and the last one is in full color. "Check my drawing" jumps to Photo ID | browser only (each part of a cartoon is tagged `data-step`) |
| 🧩 Bird Puzzle | A mystery bird picture (real photo or cartoon) is cut into 3×3, 4×4 or 5×5 scrambled tiles. Tap two tiles to swap them; tiles in the right spot get a ✅. "Hold to peek" shows the whole picture. When it's solved, the bird is revealed. Counts swaps and time | browser `<canvas>`; photos from `/api/quiz_photo` |
| ✅ Checklist | 🎬 Demo: tick off birds you've spotted. 💾 Normal: tap **👀 I saw one!** for every sighting (counts like "Seen 3×"), saved to your account. Progress bar plus "different birds spotted" and "sightings in all" | `/api/sighting`, `/api/sighting/undo` (Normal only) |
| 📺 Showtime | **1 live bird cam + 6 random clips**, picked from 29 Cornell Lab / Nat Geo Kids videos and a new mix on every refresh. Deleted or non-embeddable videos are hidden automatically | `/api/videos` (YouTube oEmbed check) |
| 🏆 Prizes | 10 badges, easiest first: Hatchling Spotter (1 bird) · **Photo Detective** (1 Photo ID) · Fledgling Birder (5 birds) · **Puzzle Pro** (5 puzzles) · **👂 Owl Ears** (5 perfect 8/8 Sound quizzes) · **Quiz Whiz** (a best score of 8+) · **🎨 Master Artist** (10 *different* Bird Book birds drawn with a looks-like score of 60+) · Flock Leader (15) · Master Birder (30) · ChirpQuest Legend (all 95) | `/api/prizes` |

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

**Accounts** (`/api/account/*`): sign up, log in, log out, change username, change password. Usernames are 3–20 letters, numbers or `_`; passwords are 6+ characters. Passwords are stored only as salted hashes (Werkzeug's scrypt), 5 wrong passwords in 5 minutes make that username wait, and changing a password logs that account out everywhere else. Everything is saved in `chirpquest_accounts.db` (SQLite, next to `chirpquest.py`, git-ignored). Kids can't delete accounts; only a parent can.

**👪 Manage Accounts** (parents only; the link is in the 👤 window): unlock it with the parent password (see 👪 Parent password above). It lists every account (birds, sightings, minutes played today) and lets a parent:
- set a **⏱️ daily time limit**: type the minutes (anything under 30 becomes 30, the most is 24 hours), or pick **Unlimited**;
- **🚫 Sections:** turn off parts of ChirpQuest for one kid (Ask Pip, Bird Book, Photo ID, Quiz, Puzzle, Draw, Checklist, Showtime, Prizes). They show a 🔒 in the menu and won't open, and the server blocks them too. 🏠 Welcome always stays on;
- **🏅 Badges:** take away a badge a kid didn't really earn (only badges they've reached can be ticked), or give it back. A taken-away badge shows "🚫 Taken away by a grown-up" and stays locked, even if the kid keeps logging birds, until a parent gives it back. Pip knows about it too;
- **🔒 Lock screen:** pause one kid's ChirpQuest with a message (up to 200 characters, like "Dinner time! 🍝"). Their page checks every 10 seconds, so the lock shows up quickly, and it stays until a parent presses 🔓 Unlock screen;
- give a new password to a kid who forgot theirs;
- delete an account and all of its progress (it asks once more first).
It locks again when you close it, or after 15 minutes.

Parent rules (sections, lock, badges) count whenever that kid is logged in, in 🎬 Demo too, and the page remembers the sections and the lock after logging out (like "Time's up") until a parent unlocks Manage Accounts on that computer (`/api/my_controls`, `/api/parent/controls`).

**🧐 Pip checks every sighting:** if a kid logs a bird that's almost never in Texas this month (this month *and* the months just before and after have under 2% of the sightings of its best month, like a Painted Bunting in January), Pip looks up iNaturalist sightings near DFW from the last 30 days. If at least 3 people reported one, it counts, with a "Wow, rare find!" note. If not, Pip blocks it and says when that bird is usually seen, and suggests 📷 Photo ID. Birds arriving or leaving (like Harris's Sparrows in late October) are never blocked. Works for 🎬 Demo ticks and 💾 Normal sightings (`/api/sighting_check`, `pip_sighting_check()`).

**⏱️ Time limits:** while someone is logged in and the page is showing, each minute counts toward today's limit (`/api/playtime`; two open tabs still count only once). The top bar shows "⏱️ 25 min left today", with a warning at 5 minutes. When time's up, a "Time's up for today" screen covers the page, **in Demo mode too on that computer**, until tomorrow or until a parent gives more time (then press 🔄 Check again). Sightings, saving progress and Pip are blocked on the server too. (Someone who never logs in can still use Demo mode; there's no way to time a person without an account.)

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

**Gemini models** (`GEMINI_MODELS`) are tried in order: `gemini-3.1-flash-lite` (the fastest, about 1 s), then `gemini-3.5-flash-lite`, then `gemini-flash-lite-latest`. If one is busy (503), gone (404) or slow, the next one is tried.

**Being polite to iNaturalist:** every iNaturalist request goes through `inat_get()`, which sends at most one request per second (iNaturalist asks apps to stay around 60 a minute) and waits and retries if iNaturalist answers "429 too many requests". Background jobs pause 1.5 s between calls so the map stays fast. Season data is saved to `season_cache.json` (git-ignored) for 30 days, so restarting the website doesn't download it all again.

**Data sources (all free, no extra keys):** iNaturalist API (photos, sightings, seasons), Wikipedia API (facts), Open-Meteo (weather), OpenStreetMap tiles, YouTube embeds (`youtube-nocookie.com`).

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
2. Make sure `04_ChirpQuest/.env` exists and has a working `GEMINI_API_KEY`. Test the key first; if it's broken, get a new one at <https://aistudio.google.com/apikey> and change it **only in `.env`**, never in the code.3. Run it: `python 04_ChirpQuest\chirpquest.py` and open <http://127.0.0.1:5000>.

### 🎯 Next up (planned Oct 24, 2026)

**1. 📰 Local bird events & news near me**
- **Goal:** pick a place (type a city like *Plano*, or use 📍 Near me) and see bird-related things happening nearby.
- **What it could show:** upcoming events such as bird banding, guided bird walks, bird counts (like the Christmas Bird Count), nature-center programs and Audubon chapter meetings, plus short local news stories about bird conservation.
- **Each item shows:** what, when, where, how far away, and a link to the real event page.
- **To figure out first:**
  - Where to get the events: local Audubon chapter calendars, city nature centers and parks departments, Texas Parks & Wildlife, local news. Check which ones have a free feed or API, and which need a key.
  - How far to search (10 miles? 25?), and whether to show only free, kid-friendly events.
  - Keep it safe for kids: only trusted sources, no personal info, and always link to the original page. Gemini could turn long event pages into short kid-friendly summaries.

**2. 🐦 More birds + a "Research this bird" helper**
- **More birds:** keep adding common North Texas birds (95 now). Check each one's sighting count near DFW first, and only add non-native birds if they're *extremely* common.
  - Already checked, but seen less often: Inca Dove (~440 sightings near DFW), Chimney Swift (~340), Horned Lark (~70).
  - Ideas to check: Gadwall, American Wigeon, Northern Pintail, Lesser Scaup, Snow Goose, Little Blue Heron, Black-crowned Night Heron, White Ibis, Neotropic Cormorant, Franklin's Gull, Forster's Tern, Red-headed Woodpecker, Ladder-backed Woodpecker, Eastern & Spotted Towhee, Orange-crowned Warbler, Common Yellowthroat, Barn Owl, Wild Turkey.
- **Research helper:** a "🔎 Research this bird" button **below every bird in the Bird Book** (and on Bird of the Day and Photo ID results). It would open one page with:
  - a kid-friendly summary, plus what it eats, where it nests, and how big it is ("about the size of a robin")
  - when and where to find it in North Texas (season chart and map)
  - real photos and recordings
  - its conservation status (how it's doing in the wild)
  - **advice from Pip, and Pip always cites the evidence**: every fact says where it came from (like "Source: All About Birds"), with a link
  - "Ask Pip" follow-up questions
  - trusted links to study more: All About Birds, Audubon, Wikipedia, iNaturalist
- **Pip helps with the draft, not the final:** a kid can write their own report and Pip gives tips (what's missing, which facts need a source, how to say it more clearly), but Pip never writes the finished report for them.
- **Maybe:** a "My Research Notebook" where kids save facts and notes, then print them as a one-page report for school.

**3. 👨‍👩‍👧 Family accounts** *(added Oct 25, 2026)*
- **The problem:** there's only one parent password for the whole website, and it belongs to whoever runs ChirpQuest. When we share it through ngrok, other families can make kid accounts, but they can't set time limits for their own kids.
- **The idea:** a parent makes a **family** (family name + its own parent password), then adds their kids' accounts to it. Each family's parent only sees and manages *their own* kids: time limits, new passwords, deleting accounts.
- The website owner's parent password stays the "front office" key that can see every family.
- **To figure out first:**
  - How a kid joins a family: the parent makes the kid account, or the kid types a family code when signing up.
  - Keep it kid-safe: no emails or real names needed.
  - What happens to a family's kids if the family is deleted.

**4. 🐦 Bird Count: a live birding event with chat** *(added Oct 28, 2026)*
- **The idea:** a parent starts a **Bird Count** for a set amount of time (like 1 hour, or a whole weekend). While it's on, every ChirpQuest player can log the birds they see and **chat live with each other about birds**.
- **Pip checks every chat message first:** Pip "kidifies" it (keeps it friendly and kid-safe), and if a message isn't about birds, Pip doesn't send it.
- **Prizes:** when the count (or the season) ends, the players who spotted the most birds get special badges: 🥇 1st, 🥈 2nd and 🥉 3rd place.
- **To figure out first:** how messages show up live for everyone, no personal info in chat (Pip removes names, places and phone numbers), what Pip does with a message it blocks, and how a count ends.
- **Needs:** more badges (item 5) and accounts (done).

**5. 🏅 More badges** *(added Oct 28, 2026)*
- New badges for the Bird Count (🥇🥈🥉 top spotters, "Took part in a Bird Count"), and more ideas: seasons (spotted a winter-only bird, a summer-only bird), habitats (5 water birds, 3 night birds), streaks (logged birds 7 days in a row), and research (finished a "Research this bird" page).

### 💭 Maybe later
- **3. Demo tour** *(probably not)*: in 🎬 Demo mode, every refresh shows a short "how to use ChirpQuest" walkthrough with Pip pointing at each part, plus a Skip button.
- **Season data by place:** the season charts and the "most seen this month" order use all of Texas right now. They could use North Texas only, or wherever 📍 Near me is.
- **Code cleanup:** split the HTML/CSS/JS out of `chirpquest.py` into `templates/` and `static/` files.
