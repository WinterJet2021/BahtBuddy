#!/usr/bin/env bash
# ======================================================
#  BahtBuddy Deployment Package - Build Script (macOS/Linux)
#  Author: Pass & Tuey | Ported to bash
#  Description: Builds BahtBuddy GUI as a native bundle on macOS
#               and as a GUI executable on Linux.
#  Usage:
#     ./scripts/build_bahtbuddy.sh            # build only
#     ./scripts/build_bahtbuddy.sh --run      # build and launch
#     ./scripts/build_bahtbuddy.sh --clean    # clean build artifacts
#  Notes:
#   - Expects repo layout with `main/gui.py` and optional `assets/icon.icns`
#   - Creates/uses a local .venv at repo root
# ======================================================

set -euo pipefail

# ---------- helpers ----------
emoji_ok="✅"
emoji_fail="❌"
emoji_rocket="🚀"

die() { echo "$emoji_fail $*" >&2; exit 1; }
has() { command -v "$1" >/dev/null 2>&1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MAIN_DIR="$REPO_ROOT/main"
VENV_DIR="$REPO_ROOT/.venv"
DIST_DIR="$MAIN_DIR/dist"
BUILD_DIR="$MAIN_DIR/build"

RUN_AFTER=false
CLEAN_ONLY=false

for arg in "${@:-}"; do
  case "$arg" in
    --run) RUN_AFTER=true ;;
    --clean) CLEAN_ONLY=true ;;
    -h|--help) echo "Usage: $0 [--run] [--clean]"; exit 0 ;;
  esac
done

# ---------- clean only ----------
if $CLEAN_ONLY; then
  echo "$emoji_rocket Cleaning previous builds..."
  rm -rf "$BUILD_DIR" "$DIST_DIR"
  echo "$emoji_ok Clean complete."
  exit 0
fi

# ---------- check OS ----------
OS="$(uname -s)"
case "$OS" in
  Darwin) TARGET_OS="mac";;
  Linux)  TARGET_OS="linux";;
  *)      die "Unsupported OS: $OS";;
es case

echo "$emoji_rocket Detected OS: $TARGET_OS"

# ---------- python / pip ----------
PYBIN=""
if has python3; then PYBIN="python3"
elif has python; then PYBIN="python"
else die "Python is not installed. Install Python 3.10+ first."
fi

# Verify Tk on mac is good (optional but helpful)
if [[ "$TARGET_OS" == "mac" ]]; then
  if ! $PYBIN - <<'PY' >/dev/null 2>&1; then
import tkinter as tk
_ = tk.TkVersion
PY
  then
    echo "⚠️  Could not import tkinter. On macOS, install Python from python.org (universal2)."
  fi
fi

# ---------- venv ----------
if [[ ! -d "$VENV_DIR" ]]; then
  echo "$emoji_rocket Creating virtual environment at $VENV_DIR ..."
  $PYBIN -m venv "$VENV_DIR" || die "Failed to create venv."
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "$emoji_rocket Checking pip & PyInstaller..."
python -m pip install --upgrade pip >/dev/null
python -m pip install pyinstaller >/dev/null || die "Failed to install PyInstaller."

echo "$emoji_ok PyInstaller ready."

# ---------- paths & sanity ----------
[[ -f "$MAIN_DIR/gui.py" ]] || die "Could not find $MAIN_DIR/gui.py. Repo layout mismatch?"
cd "$MAIN_DIR"

# Clean old artifacts
rm -rf "$BUILD_DIR" "$DIST_DIR"

# Icon if present
ICON_FLAG=()
if [[ -f "$REPO_ROOT/assets/icon.icns" && "$TARGET_OS" == "mac" ]]; then
  ICON_FLAG=(--icon "$REPO_ROOT/assets/icon.icns")
fi

echo "$emoji_rocket Building BahtBuddy for $TARGET_OS ..."

if [[ "$TARGET_OS" == "mac" ]]; then
  # macOS: build an .app bundle (GUI, no console)
  pyinstaller \
    --name "BahtBuddy" \
    --windowed \
    --onedir \
    "${ICON_FLAG[@]}" \
    gui.py
  APP_PATH="$DIST_DIR/BahtBuddy.app"

  if [[ -d "$APP_PATH" ]]; then
    echo "$emoji_ok Build complete: $APP_PATH"
    echo "To launch: open \"$APP_PATH\""
    echo "If Gatekeeper blocks the app (unsigned), run once:"
    echo "  xattr -dr com.apple.quarantine \"$APP_PATH\""
    $RUN_AFTER && open "$APP_PATH" || true
  else
    die "Build failed — .app not found at $APP_PATH"
  fi

elif [[ "$TARGET_OS" == "linux" ]]; then
  # Linux: build a GUI executable (no console)
  # Use --noconsole to suppress terminal; --windowed is ignored on Linux
  pyinstaller \
    --name "BahtBuddy" \
    --noconsole \
    --onefile \
    gui.py
  BIN_PATH="$DIST_DIR/BahtBuddy"b

  if [[ -f "$BIN_PATH" ]]; then
    chmod +x "$BIN_PATH"
    echo "$emoji_ok Build complete: $BIN_PATH"
    echo "To launch: \"$BIN_PATH\""
    $RUN_AFTER && "$BIN_PATH" || true
  else
    die "Build failed — executable not found at $BIN_PATH"
  fi
fi

echo "$emoji_ok Done."