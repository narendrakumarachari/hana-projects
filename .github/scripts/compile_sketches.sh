#!/usr/bin/env bash
# Compiles every Arduino sketch in arduino/ for one board family.
#   usage: compile_sketches.sh uno|esp32
# Which board a sketch belongs to is decided by its folder name (see board_for).
# Used by .github/workflows/build.yml, and can also be run locally in Git Bash.
set -u

FAMILY="${1:?usage: compile_sketches.sh uno|esp32}"
ARDUINO_CLI="${ARDUINO_CLI:-arduino-cli}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/arduino"

# Sketches that are intentionally not compiled (keep the reason next to each).
SKIP="WIP_Bird_Empty"   # empty placeholder, no code yet

board_for() {
  case "$1" in
    ESP32_*|Aug16a_*|SkyGuardTFT|Tool_ST7789_*) echo esp32 ;;
    *) echo uno ;;
  esac
}

case "$FAMILY" in
  uno)   FQBN="arduino:avr:uno" ;;
  esp32) FQBN="esp32:esp32:esp32" ;;
  *) echo "unknown board family: $FAMILY"; exit 2 ;;
esac

passed=0; failed=0; failed_list=""
while IFS= read -r ino; do
  dir="$(dirname "$ino")"; name="$(basename "$dir")"
  [ "$(basename "$ino" .ino)" = "$name" ] || continue          # only a sketch's main .ino
  case " $SKIP " in *" $name "*) echo "::notice::Skipped $dir (no code yet)"; continue ;; esac
  [ "$(board_for "$name")" = "$FAMILY" ] || continue

  # Wi-Fi sketches need arduino_secrets.h, which is never committed: build with the template.
  if [ -f "$dir/arduino_secrets.example.h" ] && [ ! -f "$dir/arduino_secrets.h" ]; then
    cp "$dir/arduino_secrets.example.h" "$dir/arduino_secrets.h"
  fi

  echo "::group::$dir  ($FQBN)"
  if "$ARDUINO_CLI" compile --fqbn "$FQBN" --libraries libraries --warnings none "$dir"; then
    passed=$((passed + 1))
  else
    failed=$((failed + 1)); failed_list="$failed_list $dir"
    echo "::error title=Build failed::$dir"
  fi
  echo "::endgroup::"
done < <(find . -path ./libraries -prune -o -name '*.ino' -print | sort)

echo "==================================================="
echo "$FAMILY: $passed passed, $failed failed"
[ -n "$failed_list" ] && echo "failed:$failed_list"
if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  {
    echo "### $FAMILY sketches: $passed passed, $failed failed"
    for d in $failed_list; do echo "- ❌ \`$d\`"; done
  } >> "$GITHUB_STEP_SUMMARY"
fi
[ "$failed" -eq 0 ]
