import json
import queue
import threading
import time
import urllib.error
import urllib.request


class SpotifyClient():
    '''Talks to the go-librespot daemon's local HTTP API from a background thread.

        go-librespot does the actual Spotify Connect work and audio playback. This only reads what it's doing
        and sends it commands, so the UI never waits on the network and music carries on if the UI restarts.

        Never touch pygame from here. State goes back to the main thread through getUpdate().'''

    def __init__(self, url='http://localhost:3678', pollInterval=1.0):
        self.url = url.rstrip('/')
        self.pollInterval = pollInterval
        self._updates = queue.Queue()
        self._commands = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def getUpdate(self):
        '''Latest state since the last call, or None if nothing new. Call from the main thread.

            State is a dict:
                running   go-librespot is reachable
                active    someone is connected
                deviceName
                track     None, or a dict with 'uri', 'title', 'artist', 'duration' (seconds)
                playing
                position  seconds'''
        latest = None
        while True:
            try:
                latest = self._updates.get_nowait()
            except queue.Empty:
                return latest

    # ----- Controls. These return straight away and are sent from the background thread -----

    def playPause(self):
        self._commands.put('/player/playpause')

    def next(self):
        self._commands.put('/player/next')

    def previous(self):
        self._commands.put('/player/prev')

    # ----- Background thread -----

    def _run(self):
        nextPoll = 0
        while True:
            try:
                path = self._commands.get(timeout=max(0, nextPoll - time.monotonic()))
            except queue.Empty:
                path = None
            if path is not None:
                try:
                    self._request('POST', path)
                except (OSError, ValueError):
                    pass  # Not running or nothing to control. The poll below will show that
            # Poll straight after a command too, so the screen catches up quickly
            self._updates.put(self._poll())
            nextPoll = time.monotonic() + self.pollInterval

    def _request(self, method, path):
        '''Returns the decoded JSON body, None for an empty body. Raises OSError if go-librespot can't be reached'''
        request = urllib.request.Request(self.url + path, method=method, data=b'' if method == 'POST' else None)
        with urllib.request.urlopen(request, timeout=2) as response:
            body = response.read()
        return json.loads(body) if body else None

    def _poll(self):
        try:
            status = self._request('GET', '/status')
        except (OSError, ValueError):
            return {'running': False, 'active': False, 'deviceName': None, 'track': None, 'playing': False, 'position': 0}

        # 204 with no body means nobody is connected
        if status is None:
            return {'running': True, 'active': False, 'deviceName': None, 'track': None, 'playing': False, 'position': 0}

        track = status.get('track')
        if track:
            track = {
                'uri': track['uri'],
                'title': track['name'],
                'artist': ', '.join(track['artist_names']),
                'duration': track['duration'] / 1000,
            }
            position = status['track']['position'] / 1000
        else:
            position = 0

        return {
            'running': True,
            'active': True,
            'deviceName': status.get('device_name'),
            'track': track,
            'playing': not (status['paused'] or status['stopped'] or status.get('buffering', False)),
            'position': position,
        }
