import os
from random import randint, uniform

import pygame

import utils as ut
from utils import now, lerp, Animation
from apps import createApp


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

        # 'face', 'opening', 'closing' or 'menu'. While in the menu, _activeApp is the open app, or None for home
        self._screen = 'face'
        self._activeApp = None
        self._blink = None
        self._winking = False
        self._smiling = False
        self._nextRandomBlink = now() + uniform(3, 30)
        self._menuAnim = None

        # Menu frame
        self.taskbarIconSize = self.width / 20
        self.appIconSize = self.width / 10
        self.titleFont = pygame.font.Font(ut.FONTPATH, 40)
        self.labelFont = pygame.font.Font(ut.FONTPATH, 30)

        p, lw = self.padding, self.lineWidth
        self._frameInside = 2 * p + lw
        self._dividerY = self._frameInside + self.taskbarIconSize + p
        # The area below the taskbar that an app is given to draw in
        contentTop = self._dividerY + 2 * lw
        self.contentRect = pygame.Rect(self._frameInside, contentTop,
                                       self.width - 2 * self._frameInside, self.height - contentTop - self._frameInside)

        taskbarDir = os.path.join(ut.IMGDIR, 'taskbar')
        self._taskbarIcons = {name[:-4]: ut.loadIcon(os.path.join(taskbarDir, name), self.taskbarIconSize, self.accent)
                              for name in os.listdir(taskbarDir) if name.endswith('.png')}
        self._homeTitle = self.titleFont.render('Robit Home', True, self.accent)
        self.homeButton = pygame.Rect(self._frameInside, self._frameInside, self.taskbarIconSize, self.taskbarIconSize)

        # Apps, laid out in a 4x2 grid on the home screen
        self.apps = [createApp(name, self) for name in ut.getConfig('homescreen')]

        gapX = (self.width - 2 * (p + lw) - 4 * self.appIconSize) / 5
        gapY = (self.height - 4 * p - 4 * lw - self.taskbarIconSize - 2 * self.appIconSize) / 3
        startX = p + lw + gapX
        startY = 3 * (p + lw) + self.taskbarIconSize + gapY
        self.appButtons = {}
        for n, app in enumerate(self.apps):
            x = startX + (n % 4) * (gapX + self.appIconSize)
            y = startY + (n // 4) * (gapY + self.appIconSize)
            self.appButtons[app] = pygame.Rect(x, y, self.appIconSize, self.appIconSize * 1.25)

    # ----- Public controls -----

    def changeColour(self, colour, save=True):
        '''Use to change the main colour of all aspects of the display. save=False skips writing it to the config'''
        colour = tuple(colour[:3])
        if colour != self.accent:
            self.accent = colour
            # colourise keeps the alpha, so the already rendered surfaces can be recoloured in place
            for key in self._taskbarIcons:
                self._taskbarIcons[key] = ut.colourise(self._taskbarIcons[key], colour)
            self._homeTitle = ut.colourise(self._homeTitle, colour)
            for app in self.apps:
                app.onAccentChange(colour)
        if save:
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
        elif self._screen == 'menu':
            if self._activeApp is not None:
                self._activeApp.onClose()
            self._screen = 'closing'
            self._menuAnim = Animation(duration)

    def openApp(self, app):
        '''Switches the menu to app, or back to the home screen if app is None'''
        if app is self._activeApp:
            return
        if self._activeApp is not None:
            self._activeApp.onClose()
        self._activeApp = app
        if app is not None:
            app.onOpen()

    def handleEvent(self, event):
        '''Pass every pygame event in here'''
        if self._screen != 'menu':
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.homeButton.collidepoint(event.pos):
            self.openApp(None)

        elif self._activeApp is not None:
            self._activeApp.handleEvent(event)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for app, button in self.appButtons.items():
                if app.openable and button.collidepoint(event.pos):
                    self.openApp(app)
                    break

    def update(self):
        '''Updates the display. To be called at the end of every game loop'''
        if ut.getConfig('ambientblink'):
            self._randomBlink()

        self.display.fill(ut.getConfig('backgroundcolour'))

        if self._screen == 'face':
            self._drawFace()
        elif self._screen == 'opening':
            self._drawMenuOpening()
        elif self._screen == 'closing':
            self._drawMenuClosing()
        else:
            self._drawMenu()

        pygame.display.update()
        self.clock.tick(self.fps)

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
        '''Draws the current menu screen revealed through a box of the given height, centred vertically'''
        self._drawMenu()
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
            self._screen = 'menu'
            self._drawMenu()
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
            # Already closed when the animation started, so the menu reopens to home
            self._activeApp = None
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

    # ----- Menu -----

    def _drawMenu(self):
        '''Draws the frame and taskbar, then the open app or the home screen inside it'''
        app = self._activeApp
        self._drawMenuFrame(self._homeTitle if app is None else app.titleSurface)
        if app is None:
            self._drawHome()
        else:
            app.draw(self.display, self.contentRect)

    def _drawMenuFrame(self, title):
        '''Draws the border, taskbar and title shared by every menu screen'''
        p, lw = self.padding, self.lineWidth
        inside = self._frameInside
        iconSize = self.taskbarIconSize
        pygame.draw.rect(self.display, self.accent, [p, p, self.width - 2 * p, self.height - 2 * p], lw)
        pygame.draw.rect(self.display, self.accent, [inside, self._dividerY, self.width - 2 * inside, 2 * lw], lw)

        self.display.blit(self._taskbarIcons['home'], self.homeButton)
        self.display.blit(title, (inside + iconSize + p, inside))
        self.display.blit(self._taskbarIcons[f'battery{self.batteryPercent}'], (self.width - inside - iconSize, inside))

        # With no signal the internet icon flashes
        flashOn = now() % 1.6 < 0.8
        if self.internetPercent > 0 or flashOn:
            self.display.blit(self._taskbarIcons[f'internet{self.internetPercent}'],
                              (self.width - inside - 2 * iconSize - p, inside))

    def _drawHome(self):
        for app, button in self.appButtons.items():
            self.display.blit(app.iconSurface, button)
            label = app.labelSurface.get_rect(centerx=button.centerx, top=button.top + self.appIconSize)
            self.display.blit(app.labelSurface, label)
