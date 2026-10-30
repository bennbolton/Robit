# Spotify Connect setup

Robit uses [go-librespot](https://github.com/devgianlu/go-librespot) to appear as a Spotify Connect speaker.
go-librespot runs as its own program and plays the audio. The Music app (`apps/music.py`) only reads what
it's doing and sends play/pause/skip through its local API on `localhost:3678`.

Anyone on the same network can pick **Robit** from the devices list in the Spotify app.
They need Spotify Premium, because free accounts can't use Connect speakers.

Everything lives in `spotify/`:

| File | What it's for |
| --- | --- |
| `config.yml` | go-librespot settings (name, audio, API port), shared by both scripts |
| `run-mac.sh` | run it on a Mac for testing |
| `setup-pi.sh` | one-time install on the Pi as a service that starts on boot |

## Testing on a Mac

```bash
./spotify/run-mac.sh
```

The first run installs go-librespot with Homebrew. It then runs in that terminal until you press Ctrl+C.
Audio plays through the Mac's speakers. In another terminal, start the UI:

```bash
.venv/bin/python main.py
```

Open the Music app and pick **Robit** in Spotify on your phone or computer.
Login state is kept in `~/Library/Application Support/Robit/go-librespot`, outside the repo.

## Setting up the Pi

On the Pi, from the repo folder, as your normal user (it asks for sudo itself):

```bash
./spotify/setup-pi.sh
```

This:
- downloads the go-librespot release that matches the Pi
- copies `spotify/config.yml` to `~/.config/go-librespot/`
- installs and starts a `go-librespot` systemd service
- checks the API responds

Run it again after changing `config.yml`, or with `GO_LIBRESPOT_VERSION=vX.Y.Z` to change version.

If the speaker isn't the Pi's default audio device, set `audio_device` in `config.yml`.
`aplay -L` lists the devices.

Useful commands:

```bash
journalctl -u go-librespot -f          # logs
sudo systemctl restart go-librespot
curl -i http://localhost:3678/status   # 204 until someone connects, then JSON
```

## Notes

- If Robit doesn't show up in Spotify, check both devices are on the same network and mDNS isn't blocked.
  go-librespot can use avahi instead: add `zeroconf_backend: avahi` to `config.yml`.
- Volume, shuffle, repeat, album art and the queue are all available from the same API for later.
  See `api-spec.yml` in the go-librespot repo.
