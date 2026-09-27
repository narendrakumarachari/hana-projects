# 02_Mini_Projects

Bigger terminal programs that combine the basics. No packages needed.

---

## RoseLibrary: library checkout system
**Run:** `cd 02_Mini_Projects\RoseLibrary` then `python library_checkout.py`. Run it **from inside the folder**, because it imports `books.py`.

| File | Old name | What it holds |
|---|---|---|
| `library_checkout.py` | `megaprogect.py` | the program |
| `books.py` | `megaprobook.py` | the catalogue: a dictionary of 7 books (code → title), e.g. `"BOP": "Birds of Paradise"` |

**How it works**
1. `Welcome to Rose Library`, then it asks for an ID. `123` = Alice, `456` = Tom. You get 5 tries, then `Access DENIED`.
2. It shows all titles, then asks which one to check out. Type the **exact title**, e.g. `Coding Kitty`.
3. The book is removed from the catalogue (you have it now). Type `done` to finish.

**Concepts used:** importing your own module, dictionaries (`.items()`, `.values()`, `del`), `while` loops with `break`, a generator with `next()`, `try / except`.

**Review notes / to-do**
- [ ] Titles must match exactly, capitals included (`coding kitty` fails). Compare with `.lower()`.
- [ ] Letting people type the short code (`CK`) as well as the title would be easier.
- [ ] Typing letters as the ID jumps straight to "Something went wrong" and ends. Catch `ValueError` inside the loop instead.
- [ ] Member IDs and names are hard-coded. A `members` dictionary (like `books.py`) would allow more members.
- [ ] Checked-out books aren't saved, so they come back when the program restarts. A next step could save to a file.

---

## PetCareAgent: phone-line pet clinic assistant
**Run:** `python 02_Mini_Projects\PetCareAgent\pet_care_agent_v2.py`, then type `123 4567` as the number to call.

| File | Old name | Version |
|---|---|---|
| `pet_care_agent_v1.py` | `vetagent1.py` (plus its exact copy `vetagent copy.py`, deleted) | **v1**: one question per agent, then it ends. Four near-identical `if/elif` functions |
| `pet_care_agent_v2.py` | `vetagent.py` | **v2 (current)**: a main menu loop; Cat / Dog / Fish / Bird agents, each with 7 topics (treatment, grooming, diet, price…); an "other" menu with business hours, today's walk-in window and random open checkup slots; `back` / `exit` everywhere |

**Concepts used in v2:** dictionaries of dictionaries (`CAT_OPTIONS` …), **one shared function** `run_care_menu()` driving all four agents (no repeated code), `random.sample` / `random.choice`, `if __name__ == "__main__":`.

**Review notes / to-do**
- [ ] v2 is well structured. A good next step is to move the `*_OPTIONS` data into a JSON file so new animals can be added without touching code.
- [ ] Idea: add a "book appointment" option that remembers the chosen slot.
