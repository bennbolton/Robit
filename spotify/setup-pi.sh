#!/usr/bin/env bash
# One-time setup of the Spotify Connect backend on the Raspberry Pi.
# Installs go-librespot, copies in spotify/config.yml and runs it as a service that starts on boot.
# Safe to run again, e.g. to update go-librespot or apply config changes.
#
#   ./spotify/setup-pi.sh                     install the pinned version
#   GO_LIBRESPOT_VERSION=v0.11.0 ./spotify/setup-pi.sh
set -euo pipefail

VERSION="${GO_LIBRESPOT_VERSION:-v0.10.5}"
HERE="$(cd "$(dirname "$0")" && pwd)"

if [ "$(id -u)" -eq 0 ]; then
    echo "Run this as your normal user, not with sudo. It asks for sudo when it needs it." >&2
    exit 1
fi

case "$(uname -m)" in
    aarch64) ASSET=linux_arm64 ;;           # 64-bit Raspberry Pi OS
    armv7l)  ASSET=linux_armv6 ;;           # 32-bit Raspberry Pi OS on a Pi 2/3/4/5
    armv6l)  ASSET=linux_armv6_rpi ;;       # Pi Zero / Pi 1
    x86_64)  ASSET=linux_x86_64 ;;
    *) echo "No go-librespot build for $(uname -m)" >&2; exit 1 ;;
esac

CONFIG_DIR="$HOME/.config/go-librespot"
SERVICE=/etc/systemd/system/go-librespot.service

echo "==> Installing go-librespot $VERSION ($ASSET)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
curl -fsSL "https://github.com/devgianlu/go-librespot/releases/download/$VERSION/go-librespot_$ASSET.tar.gz" -o "$TMP/go-librespot.tar.gz"
tar -xzf "$TMP/go-librespot.tar.gz" -C "$TMP"
sudo install -m 755 "$TMP/go-librespot" /usr/local/bin/go-librespot

# The release binary only links against ALSA, which Raspberry Pi OS normally already has
if ! ldconfig -p | grep -q 'libasound.so.2'; then
    echo "==> Installing ALSA"
    sudo apt-get update
    sudo apt-get install -y libasound2t64 || sudo apt-get install -y libasound2
fi

echo "==> Writing $CONFIG_DIR/config.yml"
mkdir -p "$CONFIG_DIR"
cp "$HERE/config.yml" "$CONFIG_DIR/config.yml"

echo "==> Installing service"
sudo tee "$SERVICE" >/dev/null <<EOF
[Unit]
Description=go-librespot Spotify Connect
After=network-online.target sound.target
Wants=network-online.target

[Service]
User=$USER
ExecStart=/usr/local/bin/go-librespot --config_dir $CONFIG_DIR
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable go-librespot
sudo systemctl restart go-librespot

echo "==> Checking the API"
for _ in $(seq 1 10); do
    if curl -fs -o /dev/null http://localhost:3678/; then
        echo "Done. Pick 'Robit' from the devices list in Spotify."
        echo "Logs: journalctl -u go-librespot -f"
        exit 0
    fi
    sleep 1
done
echo "go-librespot didn't come up. Check: journalctl -u go-librespot -e" >&2
exit 1
