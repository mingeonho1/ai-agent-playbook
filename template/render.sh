#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUTPUT_DIR="$ROOT_DIR/output"
CHROME_PROFILE_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/weekly-economy-render.XXXXXX")"

cleanup() {
  rm -rf "$CHROME_PROFILE_ROOT"
}
trap cleanup EXIT

if [[ ! -x "$CHROME_BIN" ]]; then
  echo "Chrome executable not found: $CHROME_BIN" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

for SLIDE in 1 2 3; do
  PAGE_URL="file://$ROOT_DIR/index.html?slide=$SLIDE"
  OUTPUT_FILE="$OUTPUT_DIR/weekly-economy-0$SLIDE.png"
  if ! DOM_OUTPUT="$("$CHROME_BIN" \
    --headless=new \
    --incognito \
    --user-data-dir="$CHROME_PROFILE_ROOT/dom-$SLIDE" \
    --disable-gpu \
    --allow-file-access-from-files \
    --virtual-time-budget=1000 \
    --dump-dom \
    "$PAGE_URL" 2>&1)"; then
    echo "Chrome failed while preparing slide $SLIDE:" >&2
    echo "$DOM_OUTPUT" >&2
    exit 1
  fi

  if [[ "$DOM_OUTPUT" != *'data-render-ready="true"'* ]]; then
    echo "Slide $SLIDE did not reach a render-ready state." >&2
    exit 1
  fi

  if [[ "$DOM_OUTPUT" == *'data-overflow="true"'* ]]; then
    OVERFLOW_TARGETS="${DOM_OUTPUT#*data-overflow-targets=\"}"
    OVERFLOW_TARGETS="${OVERFLOW_TARGETS%%\"*}"
    echo "Slide $SLIDE text overflow: $OVERFLOW_TARGETS" >&2
    exit 1
  fi

  "$CHROME_BIN" \
    --headless=new \
    --incognito \
    --user-data-dir="$CHROME_PROFILE_ROOT/screenshot-$SLIDE" \
    --disable-gpu \
    --hide-scrollbars \
    --allow-file-access-from-files \
    --force-device-scale-factor=1 \
    --window-size=1080,1920 \
    --virtual-time-budget=1000 \
    --screenshot="$OUTPUT_FILE" \
    "$PAGE_URL" >/dev/null 2>&1

  DIMENSIONS="$(sips -g pixelWidth -g pixelHeight "$OUTPUT_FILE" | awk '/pixelWidth/{width=$2} /pixelHeight/{height=$2} END{print width "x" height}')"
  if [[ "$DIMENSIONS" != "1080x1920" ]]; then
    echo "Unexpected dimensions for slide $SLIDE: $DIMENSIONS" >&2
    exit 1
  fi
  echo "Rendered $OUTPUT_FILE ($DIMENSIONS)"
done
