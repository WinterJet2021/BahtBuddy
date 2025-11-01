#!/usr/bin/env bash
# ======================================================
#  BahtBuddy Deployment Package - Build Script (macOS/Linux)
#  Author: Pass & Tuey | Ported to bash
#  Description: Builds BahtBuddy GUI as a native bundle on macOS
#               and as a GUI executable on Linux.
#  Usage:
#     ./build_bahtbuddy.sh             # build only
#     ./build_bahtbuddy.sh --run       # build and launch
#     ./build_bahtbuddy.sh --clean     # clean build artifacts
#  Notes:
#   - Expects repo layout with `main/gui.py` and optional `assets/icon.icns`
#   - Creates/uses a local .venv (on WSL it prefers ~/.venvs/bahtbuddy)
# ======================================================

set -euo pipefail

# ---- paths ----
SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"   # from main/deployment_package → repo root
MAIN_DIR="$REPO_ROOT/main"
DIST_DIR="$MAIN_DIR/dist"
BUILD_DIR="$MAIN_DIR/build"

# ---- flags ----
RUN_AFTER=false
CLEAN_ONLY=false
for arg in "$@"; do
  case "$arg" in
    --run) RUN_AFTER=true ;;
    --clean) CLEAN_ONLY=true ;;
    -h|--help) echo "Usage: $0 [--run] [--clean]"; exit 0 ;;
  esac
done

# ---- OS ----
OS="$(uname -s)"
if [ "$OS" = "Darwin" ]; then
  TARGET_OS="mac"
elif [ "$OS" = "Linux" ]; then
  TARGET_OS="linux"
else
  echo "Unsupported OS: $OS" >&2; exit 1
fi
echo "Detected OS: $TARGET_OS"

# ---- clean ----
if $CLEAN_ONLY; then
  rm -rf "$BUILD_DIR" "$DIST_DIR"
  echo "Cleaned build artifacts."
  exit 0
fi

# ---- python ----
if command -v python3 >/dev/null 2>&1; then PYBIN="python3"
elif command -v python >/dev/null 2>&1; then PYBIN="python"
else echo "Python 3 not found." >&2; exit 1
fi

# ---- venv (keep it super simple) ----
# On WSL (paths starting with /mnt/), put venv in home for speed; else local
if echo "$REPO_ROOT" | grep -q '^/mnt/'; then
  VENV_DIR="$HOME/.venvs/bahtbuddy"
else
  VENV_DIR="$REPO_ROOT/.venv"
fi

if [ -z "${VIRTUAL_ENV:-}" ]; then
  if [ ! -d "$VENV_DIR" ]; then
    echo "Creating venv at: $VENV_DIR"
    "$PYBIN" -m venv "$VENV_DIR"
  fi
  # shellcheck disable=SC1091
  . "$VENV_DIR/bin/activate"
else
  echo "Using active venv: $VIRTUAL_ENV"
fi

python -m pip install --upgrade pip >/dev/null
python -m pip install pyinstaller >/dev/null

# ---- build ----
[ -f "$MAIN_DIR/gui.py" ] || { echo "Missing $MAIN_DIR/gui.py"; exit 1; }
cd "$MAIN_DIR"
rm -rf "$BUILD_DIR" "$DIST_DIR"

if [ "$TARGET_OS" = "mac" ]; then
  # macOS app bundle
  pyinstaller --name "BahtBuddy" --windowed --onedir gui.py
  APP_PATH="$DIST_DIR/BahtBuddy.app"
  [ -d "$APP_PATH" ] || { echo "Build failed (no app)"; exit 1; }
  echo "Built: $APP_PATH"
  $RUN_AFTER && open "$APP_PATH" || true
else
  # Linux single-file GUI exe
  pyinstaller --name "BahtBuddy" --noconsole --onefile gui.py
  BIN_PATH="$DIST_DIR/BahtBuddy"
  [ -f "$BIN_PATH" ] || { echo "Build failed (no binary)"; exit 1; }
  chmod +x "$BIN_PATH"
  echo "Built: $BIN_PATH"
  $RUN_AFTER && "$BIN_PATH" || true
fi

echo "Done."