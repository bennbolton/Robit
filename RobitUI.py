import os
from random import randint, uniform

import pygame

import utils as ut


BASEDIR = os.path.dirname(os.path.abspath(__file__))
IMGDIR = os.path.join(BASEDIR, 'data', 'imgs', 'icons')
FONTPATH = os.path.join(BASEDIR, 'data', 'pixel.otf')

SLIDERX = 50
SLIDERY = 175
SLIDERGAP = 50
SLIDERWIDTH = 256  # one pixel per colour value, 0-255
SLIDERHEIGHT = 10


def now():
    '''Seconds since pygame.init()'''
    return pygame.time.get_ticks() / 1000


def lerp(start, end, t):
    return start + (end - start) * t


def colourise(image, colour):
    '''Returns a copy of image with every pixel set to colour, keeping the alpha'''
    image = image.copy()
    image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    image.fill(tuple(colour[:3]) + (0,), None, pygame.BLEND_RGBA_ADD)
    return image


def loadIcons(folder, size, colour):
    icons = {}
    for name in os.listdir(folder):
        if name.endswith('.png'):
            img = pygame.image.load(os.path.join(folder, name))
            img = pygame.transform.scale(img, (size, size))
            icons[name[:-4]] = colourise(img, colour)
    return icons


class Animation():
    '''Tracks progress through a fixed length of real time, independent of frame rate'''

    def __init__(self, duration):
        self.start = now()
        self.duration = duration

    @property
    def progress(self):
        '''0 at the start, 1 once the duration has passed'''
        return min(1, (now() - self.start) / self.duration)

    @property
    def done(self):
        return self.progress >= 1

    def phase(self, count):
        '''Splits the animation into equal phases. Returns (phase index, progress within that phase)'''
        scaled = self.progress * count
        index = min(int(scaled), count - 1)
        return index, scaled - index


class RobitUI():

    def __init__(self, **kwargs):
        '''Initialise with kwargs to update settings from beginning.

            Key words available are:

            displayres ;
            displayfps ;
            fullscreen ;
            showmouse ;
            accentcolour ;
            backgroundcolour ;
            menupadding ;
            menulinewidth ;
            ambientblink'''

        ut.updateConfig(**kwargs)

        self.displayRes = ut.getConfig('displayres')
        self.width, self.height = self.displayRes
        self.padding = ut.getConfig('menupadding')
        self.lineWidth = ut.getConfig('menulinewidth')
        self.fps = ut.getConfig('displayfps')
        self.homescreen = ut.getConfig('homescreen')
        self.accent = ut.getConfig('accentcolour')

        flags = pygame.FULLSCREEN if ut.getConfig('fullscreen') else 0
        self.display = pygame.display.set_mode(self.displayRes, flags)
        pygame.display.set_caption('Robit')
        pygame.mouse.set_visible(ut.getConfig('showmouse'))
        self.clock = pygame.time.Clock()

        self.batteryPercent = 75
        self.internetPercent = 75

        # Face
        eyeWidth = 3 * self.width / 16
        self._eyeDim = (eyeWidth, 2 * eyeWidth)
        self._eyePosL = self.width / 8
        self._eyePosR = self.width - self._eyePosL - eyeWidth

        self._screen = 'face'
        self._blink = None
        self._winking = False
        self._smiling = False
        self._nextRandomBlink = now() + uniform(3, 30)
        self._menuAnim = None

        # Icons
        self._taskbarIconSize = self.width / 20
        self._appIconSize = self.width / 10

        self._taskbarIcons = loadIcons(os.path.join(IMGDIR, 'taskbar'), self._taskbarIconSize, self.accent)
        self._appIcons = loadIcons(os.path.join(IMGDIR, 'apps'), self._appIconSize, self.accent)
        for app in self.homescreen:
            # Placeholder icon for apps that don't have one yet
            self._appIcons.setdefault(app, self._appIcons['settings'])

        # Home screen buttons, in a 4x2 grid
        inner = self.padding + self.lineWidth
        gapX = (self.width - 2 * inner - 4 * self._appIconSize) / 5
        gapY = (self.height - 4 * self.padding - 4 * self.lineWidth - self._taskbarIconSize - 2 * self._appIconSize) / 3
        startX = inner + gapX
        startY = 3 * inner + self._taskbarIconSize + gapY

        self.appButtons = {}
        for n, app in enumerate(self.homescreen):
            x = startX + (n % 4) * (gapX + self._appIconSize)
            y = startY + (n // 4) * (gapY + self._appIconSize)
            self.appButtons[app] = pygame.Rect(x, y, self._appIconSize, self._appIconSize * 1.25)
        self.homeButton = pygame.Rect(2 * self.padding + self.lineWidth, 2 * self.padding + self.lineWidth,
                                      self._taskbarIconSize, self._taskbarIconSize)

        # Settings
        self._sliders = [pygame.Rect(SLIDERX, SLIDERY + i * SLIDERGAP, SLIDERWIDTH, SLIDERHEIGHT) for i in range(3)]
        self._resetButton = pygame.Rect(400, 175, 50, 50)
        self._sliderGradients = [None, None, None]
        self._sliderGradientKeys = [None, None, None]
        self._draggingSlider = None

        # Text
        titleFont = pygame.font.Font(FONTPATH, 40)
        appFont = pygame.font.Font(FONTPATH, 30)
        self._menuTitles = {title: titleFont.render(title, True, self.accent) for title in ['Robit Home', 'Settings']}
        self._appTitles = {app: appFont.render(app, True, self.accent) for app in self.homescreen}

        # Every screen that can be shown, and the method that draws it
        self._screens = {
            'face': self._drawFace,
            'opening': self._drawMenuOpening,
            'closing': self._drawMenuClosing,
            'home': self._drawHome,
            'settings': self._drawSettings,
        }

    # ----- Public controls -----

    def changeColour(self, colour):
        '''Use to change the main colour of all aspects of the display'''
        self._setAccent(colour)
        ut.updateConfig(accentcolour=self.accent)

    def changeBackground(self, background):
        '''Use to change the background colour of the display'''
        ut.updateConfig(backgroundcolour=background)

    def blink(self, duration=0.25, wink=False):
        '''Triggers a simple blink of the eyes, duration in seconds. Set wink=True to make the blink a wink instead'''
        if self._blink is None and self._screen == 'face':
            self._blink = Animation(duration)
            self._winking = wink

    def toggleSmile(self):
        '''Toggles whether the mouth is visible or not. (Not Currently available)'''
        if self._screen == 'face':
            self._smiling = not self._smiling

    def toggleMenu(self, duration=1.0):
        '''Opens the menu from the face, or closes it back to the face. duration in seconds'''
        if self._screen == 'face':
            self._screen = 'opening'
            self._menuAnim = Animation(duration)
        elif self._screen in ('home', 'settings'):
            self._screen = 'closing'
            self._menuAnim = Animation(duration)

    def handleEvent(self, event):
        '''Pass every pygame mouse event in here'''
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handleClick(*event.pos)
        elif event.type == pygame.MOUSEMOTION and self._draggingSlider is not None:
            self._dragSlider(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self._draggingSlider is not None:
            self._draggingSlider = None
            # Only save once the drag ends, rather than writing the file on every movement
            ut.updateConfig(accentcolour=self.accent)

    def update(self):
        '''Updates the display. To be called at the end of every game loop'''
        if ut.getConfig('ambientblink'):
            self._randomBlink()

        self.display.fill(ut.getConfig('backgroundcolour'))
        self._screens[self._screen]()

        pygame.display.update()
        self.clock.tick(self.fps)

    # ----- Input -----

    def _handleClick(self, mx, my):
        if self._screen in ('home', 'settings') and self.homeButton.collidepoint(mx, my):
            self._screen = 'home'

        elif self._screen == 'home':
            for app, button in self.appButtons.items():
                # Only apps with a screen to draw can be opened
                if button.collidepoint(mx, my) and app in self._screens:
                    self._screen = app

        elif self._screen == 'settings':
            for i, slider in enumerate(self._sliders):
                if slider.inflate(0, 30).collidepoint(mx, my):
                    self._draggingSlider = i
                    self._dragSlider(mx)
                    return
            if self._resetButton.collidepoint(mx, my):
                self.changeColour(ut.getDefaultConfig('accentcolour'))

    def _dragSlider(self, mx):
        slider = self._sliders[self._draggingSlider]
        value = max(0, min(255, mx - slider.left))
        colour = list(self.accent)
        colour[self._draggingSlider] = value
        self._setAccent(colour)

    def _setAccent(self, colour):
        colour = tuple(colour[:3])
        if colour == self.accent:
            return
        self.accent = colour
        # colourise keeps the alpha, so the already rendered surfaces can be recoloured in place
        for surfaces in (self._appIcons, self._taskbarIcons, self._menuTitles, self._appTitles):
            for key in surfaces:
                surfaces[key] = colourise(surfaces[key], colour)

    # ----- Face -----

    def _randomBlink(self):
        if now() >= self._nextRandomBlink:
            self.blink(wink=(randint(0, 19) == 0))
            self._nextRandomBlink = now() + uniform(3, 30)

    def _drawEyes(self, leftHeight, rightHeight=None):
        '''Draws both eyes vertically centred, at the given heights'''
        if rightHeight is None:
            rightHeight = leftHeight
        for x, h in ((self._eyePosL, leftHeight), (self._eyePosR, rightHeight)):
            pygame.draw.ellipse(self.display, self.accent, [x, (self.height - h) / 2, self._eyeDim[0], h], 0)

    def _drawFace(self):
        eyeHeight = self._eyeDim[1]
        height = eyeHeight

        if self._blink is not None:
            # Closes over the first half, opens over the second
            height = abs(1 - 2 * self._blink.progress) * eyeHeight
            if self._blink.done:
                self._blink = None

        self._drawEyes(height, eyeHeight if self._winking else height)

        if self._smiling:
            pass  # TODO: draw a smile here

    # ----- Menu transitions -----

    def _drawMenuBox(self, height):
        '''Draws the home screen revealed through a box of the given height, centred vertically'''
        self._drawHome()
        background = ut.getConfig('backgroundcolour')
        top = (self.height - height) / 2
        pygame.draw.rect(self.display, background, [0, 0, self.width, top], 0)
        pygame.draw.rect(self.display, background, [0, top + height, self.width, top], 0)
        pygame.draw.rect(self.display, self.accent, [self.padding, top, self.width - 2 * self.padding, height], self.lineWidth)

    def _drawBar(self, x, length):
        y = (self.height - 2 * self.lineWidth) / 2
        pygame.draw.rect(self.display, self.accent, [x, y, length, 2 * self.lineWidth], self.lineWidth)

    def _drawMenuOpening(self):
        if self._menuAnim.done:
            self._screen = 'home'
            self._drawHome()
            return

        phase, t = self._menuAnim.phase(3)
        lineHeight = 2 * self.lineWidth
        boxHeight = self.height - 2 * self.padding

        if phase == 0:
            # Eyes squash down into flat lines
            self._drawEyes(lerp(self._eyeDim[1], lineHeight, t))

        elif phase == 1:
            # Lines stretch out from the eyes until they meet in the middle
            length = lerp(self._eyeDim[0], self.width / 2 - self.padding, t)
            leftX = lerp(self._eyePosL, self.padding, t)
            self._drawBar(leftX, length)
            self._drawBar(self.width - leftX - length, length)

        else:
            # Box opens up to reveal the menu
            self._drawMenuBox(lerp(lineHeight, boxHeight, t))

    def _drawMenuClosing(self):
        if self._menuAnim.done:
            self._screen = 'face'
            self._drawFace()
            return

        phase, t = self._menuAnim.phase(3)
        lineHeight = 2 * self.lineWidth
        boxHeight = self.height - 2 * self.padding

        if phase == 0:
            # Box squashes down into a line
            self._drawMenuBox(lerp(boxHeight, lineHeight, t))

        elif phase == 1:
            # Line shrinks into the centre
            length = lerp(self.width - 2 * self.padding, 0, t)
            self._drawBar((self.width - length) / 2, length)

        else:
            # Eyes grow back
            self._drawEyes(lerp(0, self._eyeDim[1], t))

    # ----- Menus -----

    def _drawMenuFrame(self, title):
        '''Draws the border, taskbar and title shared by every menu screen'''
        p, lw = self.padding, self.lineWidth
        iconSize = self._taskbarIconSize
        pygame.draw.rect(self.display, self.accent, [p, p, self.width - 2 * p, self.height - 2 * p], lw)

        inside = 2 * p + lw
        dividerY = inside + iconSize + p
        pygame.draw.rect(self.display, self.accent, [inside, dividerY, self.width - 2 * inside, 2 * lw], lw)

        self.display.blit(self._taskbarIcons['home'], (inside, inside))
        self.display.blit(self._menuTitles[title], (inside + iconSize + p, inside))
        self.display.blit(self._taskbarIcons[f'battery{self.batteryPercent}'], (self.width - inside - iconSize, inside))

        # With no signal the internet icon flashes
        flashOn = now() % 1.6 < 0.8
        if self.internetPercent > 0 or flashOn:
            self.display.blit(self._taskbarIcons[f'internet{self.internetPercent}'],
                              (self.width - inside - 2 * iconSize - p, inside))

    def _drawHome(self):
        self._drawMenuFrame('Robit Home')

        for app in self.homescreen:
            button = self.appButtons[app]
            self.display.blit(self._appIcons[app], button)
            label = self._appTitles[app].get_rect(centerx=button.centerx, top=button.top + self._appIconSize)
            self.display.blit(self._appTitles[app], label)

    def _drawSettings(self):
        self._drawMenuFrame('Settings')

        for i, slider in enumerate(self._sliders):
            self.display.blit(self._getSliderGradient(i), slider)
            knob = (slider.left + self.accent[i], slider.centery)
            pygame.draw.circle(self.display, self.accent, knob, 12, 0)
            pygame.draw.circle(self.display, 'grey', knob, 9, 0)

        pygame.draw.rect(self.display, 'red', self._resetButton, width=0)

    def _getSliderGradient(self, channel):
        '''Gradient for one colour channel, with the other two channels held at their current values.
            Cached until those other channels change.'''
        key = tuple(c for i, c in enumerate(self.accent) if i != channel)

        if self._sliderGradientKeys[channel] != key:
            surf = pygame.Surface((SLIDERWIDTH, SLIDERHEIGHT)).convert()
            colour = list(self.accent)
            for x in range(SLIDERWIDTH):
                colour[channel] = x
                pygame.draw.line(surf, colour, (x, 0), (x, SLIDERHEIGHT - 1))
            self._sliderGradients[channel] = surf
            self._sliderGradientKeys[channel] = key

        return self._sliderGradients[channel]
