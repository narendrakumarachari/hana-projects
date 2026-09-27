# 01_Python_Basics

<!-- circuit-card --> 🔌 **Circuit cards:** [Python Basics (13 lessons)](https://narendrakumarachari.github.io/hana-projects/cards/py-basics.html)

13 small lessons, numbered in the order they were written (July 17 to August 27, 2026). Run any of them in the terminal:
```bat
cd C:\Users\narendra\HanaProjects\python
venv\Scripts\activate
python 01_Python_Basics\05_calculator.py
```
No packages needed, only standard Python.

| # | File | Concept | Try typing | Review notes / to-do |
|---|---|---|---|---|
| 01 | `01_hello_print.py` | `print()` | — | — |
| 02 | `02_variables.py` | variables, printing several values | — | — |
| 03 | `03_input_greeting.py` | `input()`, joining strings with `+` | your name | — |
| 04 | `04_if_elif_else.py` | `if / elif / else` | `yes`, `no`, `maybe` | Typing `Yes` (capital Y) counts as invalid. Try `.lower()` |
| 05 | `05_calculator.py` | `int()`, arithmetic operators | `8`, `2`, `/` | ⚠️ Dividing by `0` crashes. Add a check. Typing letters instead of a number crashes too; `13_try_except` shows the fix |
| 06 | `06_string_indexing.py` | `text[0]`, `text[-1]`, `text[1:3]` | — | — |
| 07 | `07_friendly_chat.py` | f-strings, a small conversation | your name, `yes` / `no` | — |
| 08 | `08_compare_numbers.py` | `>`, `<`, `elif` | `5`, `5` | ⚠️ Equal numbers print nothing. Add an `else: print("They are equal")` |
| 09 | `09_string_slicing.py` | slicing `[start:stop:step]`, reversing `[::-1]` | — | The first 16 lines run. The rest is a commented-out reference guide |
| 10 | `10_loops.py` | `for`, `while`, `range()`, `break` | — | Every line is commented out (notes). Several examples print `i` while the loop variable has another name (`t`, `r`, `w`…), so un-commenting them gives `NameError`. Rename to match |
| 11 | `11_functions_pet_agents.py` | defining and calling functions | `1`–`4` | Grew into the Pet Care Agent (`02_Mini_Projects/PetCareAgent`) |
| 12 | `12_data_types.py` | str, int, float, bool, list, tuple, dict, set; mutable vs immutable | — | Only the string-replace example is active. The comment says "changing the value of a string", but strings are immutable: `replace()` makes a **new** string |
| 13 | `13_try_except.py` | `try / except` | `abc`, then `5` | ⚠️ If the second answer is also not a number, it crashes. Put the question in a `while True:` loop. Prefer `except ValueError:` over a bare `except:` |
