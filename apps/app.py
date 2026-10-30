import os

import utils as ut


class App():
    '''Base class for every app on the home screen.

        To make a new app, subclass this, set the class attributes, override the hooks you need,
        then add it to APPS in apps/__init__.py and put its name in the homescreen config list.

        Hooks (all optional apart from draw):
            draw(surface, rect)     draw the app inside rect, below the taskbar. Called every frame while open
            handleEvent(event)      pygame events while the app is open. Mouse positions are screen coordinates
            onOpen()                the app has just been opened from the home screen
            onClose()               the app is being left, either back to home or by the menu closing
            onAccentChange(colour)  the accent colour changed. Call super() to keep the icon and text in sync'''

    name = None         # id used in the homescreen config list
    title = None        # shown in the taskbar while open. Defaults to name
    label = None        # shown under the icon on the home screen. Defaults to name
    icon = None         # png in data/imgs/icons/apps, without the extension. Defaults to name
    openable = True

    def __init__(self, ui):
        self.ui = ui
        self.title = self.title or self.name
        self.label = self.label or self.name
        self.icon = self.icon or self.name

        iconPath = os.path.join(ut.IMGDIR, 'apps', self.icon + '.png')
        if not os.path.exists(iconPath):
            iconPath = os.path.join(ut.IMGDIR, 'apps', 'settings.png')

        # Rendered once here rather than every frame, and recoloured in onAccentChange
        self.iconSurface = ut.loadIcon(iconPath, ui.appIconSize, ui.accent)
        self.labelSurface = ui.labelFont.render(self.label, True, ui.accent)
        self.titleSurface = ui.titleFont.render(self.title, True, ui.accent)

    def draw(self, surface, rect):
        raise NotImplementedError

    def handleEvent(self, event):
        pass

    def onOpen(self):
        pass

    def onClose(self):
        pass

    def onAccentChange(self, colour):
        self.iconSurface = ut.colourise(self.iconSurface, colour)
        self.labelSurface = ut.colourise(self.labelSurface, colour)
        self.titleSurface = ut.colourise(self.titleSurface, colour)


class PlaceholderApp(App):
    '''Shows an icon on the home screen for an app that doesn't exist yet'''

    icon = 'settings'
    openable = False

    def __init__(self, ui, name):
        self.name = name
        super().__init__(ui)

    def draw(self, surface, rect):
        pass
