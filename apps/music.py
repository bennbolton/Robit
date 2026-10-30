import string

import pygame

import utils as ut
from apps.app import App
from apps.spotify import SpotifyClient


DEVICENAME = 'Robit'  # should match device_name in go-librespot's config.yml
BARHEIGHT = 10
BUTTONSIZE = 60
BUTTONGAP = 120

# The pixel font only has letters, so anything else (numbers, punctuation, accents) uses pygame's built in font
PIXELCHARS = set(string.ascii_letters + ' ')


class MusicApp(App):
    '''Now playing screen for Robit acting as a Spotify Connect speaker.

        go-librespot runs separately and does the playing. SpotifyClient checks on it in the background,
        and update() copies whatever it reports into this screen.'''

    name = 'music'
    title = 'Music'

    def __init__(self, ui):
        super().__init__(ui)
        self.running = False    # go-librespot reachable
        self.deviceName = DEVICENAME
        self.track = None       # dict with 'uri', 'title', 'artist' and 'duration' (seconds), or None
        self.playing = False

        # Position is stored as where playback was at a moment in time, so the progress bar can move
        # smoothly every frame between status updates
        self._position = 0
        self._positionTime = ut.now()

        self._fallbackFonts = {ui.titleFont: pygame.font.Font(None, 44), ui.labelFont: pygame.font.Font(None, 32)}
        self._buttons = {}
        self._layoutButtons(ui.contentRect)
        self._renderText()

        self.client = SpotifyClient(ut.getConfig('spotifyapi'))
        self.client.start()

    # ----- State -----

    def setTrack(self, track):
        '''track is a dict as described on self.track, or None'''
        self.track = track
        self._renderText()

    def setPlayback(self, playing, position):
        '''Playback started, paused or seeked. position in seconds'''
        self.playing = playing
        self._position = position
        self._positionTime = ut.now()

    @property
    def position(self):
        '''Current position through the track in seconds'''
        if not self.playing:
            return self._position
        position = self._position + ut.now() - self._positionTime
        return min(position, self.track['duration']) if self.track else position

    # ----- Hooks -----

    def update(self):
        state = self.client.getUpdate()
        if state is None:
            return

        deviceName = state['deviceName'] or DEVICENAME
        if state['running'] != self.running or deviceName != self.deviceName:
            self.running = state['running']
            self.deviceName = deviceName
            self._renderText()

        newUri = state['track']['uri'] if state['track'] else None
        oldUri = self.track['uri'] if self.track else None
        if newUri != oldUri:
            self.setTrack(state['track'])

        self.setPlayback(state['playing'], state['position'])

    def handleEvent(self, event):
        if self.track is None or event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        if self._buttons['playpause'].collidepoint(event.pos):
            self.client.playPause()
            # Show the change straight away rather than waiting for the next status update
            self.setPlayback(not self.playing, self.position)
        elif self._buttons['next'].collidepoint(event.pos):
            self.client.next()
        elif self._buttons['previous'].collidepoint(event.pos):
            self.client.previous()

    def onAccentChange(self, colour):
        super().onAccentChange(colour)
        self._renderText()

    def draw(self, surface, rect):
        if self.track is None:
            for text, offset in zip(self._lines, (-25, 25)):
                surface.blit(text, text.get_rect(center=(rect.centerx, rect.centery + offset)))
            return

        accent = self.ui.accent
        left = rect.left + 2 * self.ui.padding
        width = rect.width - 4 * self.ui.padding

        # Long names are cut off at the edge rather than running over the border
        titleText, artistText = self._lines
        surface.blit(titleText, (left, rect.top + 2 * self.ui.padding), (0, 0, width, titleText.get_height()))
        surface.blit(artistText, (left, rect.top + 2 * self.ui.padding + 50), (0, 0, width, artistText.get_height()))

        self._drawPrevious(surface, self._buttons['previous'].center)
        if self.playing:
            self._drawPause(surface, self._buttons['playpause'].center)
        else:
            self._drawPlay(surface, self._buttons['playpause'].center)
        self._drawNext(surface, self._buttons['next'].center)

        bar = pygame.Rect(left, rect.bottom - 3 * self.ui.padding, width, BARHEIGHT)
        fraction = self.position / self.track['duration'] if self.track['duration'] else 0
        pygame.draw.rect(surface, accent, bar, self.ui.lineWidth)
        pygame.draw.rect(surface, accent, (bar.left, bar.top, bar.width * fraction, bar.height), 0)

    # ----- Drawing -----

    def _renderText(self):
        '''Text only changes with the track, connection or colour, so it's rendered then rather than every frame'''
        if self.track is not None:
            lines = [self.track['title'], self.track['artist']]
        elif self.running:
            lines = ['Waiting for Spotify', f'Connect to {self.deviceName} in the Spotify app']
        else:
            lines = ['Spotify is off', 'The Spotify service is not running']

        self._lines = []
        for font, line in zip([self.ui.titleFont, self.ui.labelFont], lines):
            if not set(line) <= PIXELCHARS:
                font = self._fallbackFonts[font]
            self._lines.append(font.render(line, True, self.ui.accent))

    def _layoutButtons(self, rect):
        centreY = rect.top + 190
        for name, offset in (('previous', -BUTTONGAP), ('playpause', 0), ('next', BUTTONGAP)):
            button = pygame.Rect(0, 0, BUTTONSIZE, BUTTONSIZE)
            button.center = (rect.centerx + offset, centreY)
            self._buttons[name] = button

    def _drawPlay(self, surface, centre):
        x, y = centre
        pygame.draw.polygon(surface, self.ui.accent, [(x - 15, y - 20), (x - 15, y + 20), (x + 20, y)])

    def _drawPause(self, surface, centre):
        x, y = centre
        pygame.draw.rect(surface, self.ui.accent, (x - 15, y - 20, 10, 40))
        pygame.draw.rect(surface, self.ui.accent, (x + 5, y - 20, 10, 40))

    def _drawNext(self, surface, centre):
        x, y = centre
        pygame.draw.polygon(surface, self.ui.accent, [(x - 18, y - 18), (x - 18, y + 18), (x + 10, y)])
        pygame.draw.rect(surface, self.ui.accent, (x + 10, y - 18, 8, 36))

    def _drawPrevious(self, surface, centre):
        x, y = centre
        pygame.draw.polygon(surface, self.ui.accent, [(x + 18, y - 18), (x + 18, y + 18), (x - 10, y)])
        pygame.draw.rect(surface, self.ui.accent, (x - 18, y - 18, 8, 36))
