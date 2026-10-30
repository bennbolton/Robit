# Spotify Connect setup (Raspberry Pi)

Robit uses [go-librespot](https://github.com/devgianlu/go-librespot) to appear as a Spotify Connect speaker.
go-librespot runs as its own background service and plays the audio. The Music app (`apps/music.py`) only
reads what it's doing and sends play/pause/skip through its local API on port 3678.

Anyone on the same network can then pick **Robit** from the devices list in the Spotify app.
They need Spotify Premium, because free accounts can't use Connect speakers.

## 1. Install go-librespot

Download the Linux build for the Pi from the
[latest release](https://github.com/devgianlu/go-librespot/releases/latest). Use arm64 on a 64-bit
Raspberry Pi OS, and check `uname -m` if you're not sure. Then put the binary on the path:

```bash
sudo install -m 755 go-librespot /usr/local/bin/go-librespot
```

If there's no build for your Pi, build it from source. That needs Go 1.25 or newer, plus:

```bash
sudo apt-get install libogg-dev libvorbis-dev libflac-dev libmpg123-dev libasound2-dev
```

## 2. Config

Create `~/.config/go-librespot/config.yml`:

```yaml
device_name: Robit          # must match DEVICENAME in apps/music.py
device_type: speaker
audio_backend: alsa
audio_device: default       # change if the speaker isn't the default ALSA device (see `aplay -L`)
bitrate: 320

# Anyone on the network can connect from their own Spotify account
credentials:
  type: zeroconf

# Local API the Music app talks to. Keep it on localhost so only the Pi can control it
server:
  enabled: true
  address: localhost
  port: 3678                # must match spotifyapi in config.cfg
```

## 3. Run it as a service

Create `/etc/systemd/system/go-librespot.service`, replacing `YOURUSER` with the Pi's username:

```ini
[Unit]
Description=go-librespot Spotify Connect
After=network-online.target sound.target
Wants=network-online.target

[Service]
User=YOURUSER
ExecStart=/usr/local/bin/go-librespot -config_dir /home/YOURUSER/.config/go-librespot
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now go-librespot
```

## 4. Check it

```bash
systemctl status go-librespot
curl -i http://localhost:3678/status
```

`/status` returns `204 No Content` until someone connects, then JSON with the current track.
After that, the Music app should change from "Spotify is off" to "Waiting for Spotify".

## Notes

- If Robit doesn't show up in Spotify, check the Pi and the phone are on the same network and that mDNS
  isn't blocked. go-librespot can also use avahi for discovery: `zeroconf_backend: avahi` in config.yml.
- Volume, shuffle, repeat, album art and the queue are all available from the same API for later.
  See the API spec in the go-librespot repo.
