"""Adds (or refreshes) a 'Circuit card' link near the top of each project README."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from data import PROJECTS, LEARNING, PYTHON  # noqa: E402

SITE = "https://narendrakumarachari.github.io/hana-projects"
MARK = "<!-- circuit-card -->"


def put(readme, line):
    p = os.path.join(ROOT, readme.replace("/", os.sep))
    if not os.path.exists(p):
        print("missing", readme)
        return
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"\n?" + re.escape(MARK) + r"[^\n]*\n", "\n", s)
    lines = s.split("\n")
    i = next(k for k, l in enumerate(lines) if l.startswith("# ")) + 1
    lines.insert(i, "\n" + MARK + " " + line)
    s = "\n".join(lines).replace("\n\n\n", "\n\n")
    open(p, "w", encoding="utf-8", newline="\n").write(s)


for p in PROJECTS + LEARNING:
    put(p["folder"] + "/README.md",
        f"🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist]({SITE}/cards/{p['slug']}.html)")

py_links = {}
for q in PYTHON:
    folder = (q["file"] if q["file"].endswith("/") else os.path.dirname(q["file"])).rstrip("/")
    while not os.path.exists(os.path.join(ROOT, folder, "README.md")):   # e.g. RoseLibrary -> 02_Mini_Projects
        folder = os.path.dirname(folder)
    py_links.setdefault(folder, []).append(q)
for folder, qs in py_links.items():
    links = " · ".join(f"[{q['title']}]({SITE}/cards/{q['slug']}.html)" for q in qs)
    put(folder + "/README.md", f"🔌 **Circuit cards:** {links}")

put("README.md", f"🔌 **Circuit cards for every project** (wiring pictures, parts, checklists): **{SITE}/**")
put("arduino/README.md", f"🔌 **Circuit cards for every sketch:** {SITE}/")
put("python/README.md", f"🔌 **Circuit cards for the Python programs:** {SITE}/")
print("README links updated")
