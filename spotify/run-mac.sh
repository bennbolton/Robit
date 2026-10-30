#!/usr/bin/env bash
# Runs go-librespot on this Mac so the Music app can be tested without the Pi.
# Robit shows up as a Spotify Connect speaker on your network until you press Ctrl+C.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# Kept outside the repo because go-librespot stores login state here
CONFIG_DIR="$HOME/Library/Application Support/Robit/go-librespot"

if ! command -v go-librespot >/dev/null; then
    if ! command -v brew >/dev/null; then
        echo "Homebrew is needed to install go-librespot: https://brew.sh" >&2
        exit 1
    fi
    echo "Installing go-librespot with Homebrew..."
    brew install go-librespot
fi

mkdir -p "$CONFIG_DIR"
# Copied fresh every run so edits to spotify/config.yml are picked up
sed 's/^audio_backend: .*/audio_backend: audio-toolbox/' "$HERE/config.yml" > "$CONFIG_DIR/config.yml"

echo "Starting go-librespot. Pick 'Robit' from the devices list in Spotify. Ctrl+C to stop."
exec go-librespot --config_dir "$CONFIG_DIR"
