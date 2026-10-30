import pygame

import utils as ut
from apps.app import App


SLIDERWIDTH = 256  # one pixel per colour value, 0-255
SLIDERHEIGHT = 10
SLIDERGAP = 50


class SettingsApp(App):
    '''Accent colour picker: one slider per RGB channel, plus a reset button'''

    name = 'settings'
    title = 'Settings'

    def __init__(self, ui):
        super().__init__(ui)

        content = ui.contentRect
        left = content.left + ui.padding
        top = content.top + 2 * ui.padding
        self._sliders = [pygame.Rect(left, top + i * SLIDERGAP, SLIDERWIDTH, SLIDERHEIGHT) for i in range(3)]
        self._resetButton = pygame.Rect(left + SLIDERWIDTH + 4 * ui.padding, top, 50, 50)

        self._gradients = [None, None, None]
        self._gradientKeys = [None, None, None]
        self._dragging = None

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, slider in enumerate(self._sliders):
                if slider.inflate(0, 30).collidepoint(event.pos):
                    self._dragging = i
                    self._dragTo(event.pos[0])
                    return
            if self._resetButton.collidepoint(event.pos):
                self.ui.changeColour(ut.getDefaultConfig('accentcolour'))

        elif event.type == pygame.MOUSEMOTION and self._dragging is not None:
            self._dragTo(event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._stopDragging()

    def onClose(self):
        self._stopDragging()

    def draw(self, surface, rect):
        accent = self.ui.accent
        for i, slider in enumerate(self._sliders):
            surface.blit(self._getGradient(i), slider)
            knob = (slider.left + accent[i], slider.centery)
            pygame.draw.circle(surface, accent, knob, 12, 0)
            pygame.draw.circle(surface, 'grey', knob, 9, 0)

        pygame.draw.rect(surface, 'red', self._resetButton, width=0)

    def _dragTo(self, mx):
        slider = self._sliders[self._dragging]
        colour = list(self.ui.accent)
        colour[self._dragging] = max(0, min(255, mx - slider.left))
        self.ui.changeColour(colour, save=False)

    def _stopDragging(self):
        if self._dragging is not None:
            self._dragging = None
            # Only save once the drag ends, rather than writing the file on every movement
            self.ui.changeColour(self.ui.accent)

    def _getGradient(self, channel):
        '''Gradient for one colour channel, with the other two channels held at their current values.
            Cached until those other channels change.'''
        accent = self.ui.accent
        key = tuple(c for i, c in enumerate(accent) if i != channel)

        if self._gradientKeys[channel] != key:
            surf = pygame.Surface((SLIDERWIDTH, SLIDERHEIGHT)).convert()
            colour = list(accent)
            for x in range(SLIDERWIDTH):
                colour[channel] = x
                pygame.draw.line(surf, colour, (x, 0), (x, SLIDERHEIGHT - 1))
            self._gradients[channel] = surf
            self._gradientKeys[channel] = key

        return self._gradients[channel]
