from apps.app import App, PlaceholderApp
from apps.settings import SettingsApp
from apps.music import MusicApp


# Every app that can be put on the home screen, by the name used in the homescreen config list
APPS = {cls.name: cls for cls in [SettingsApp, MusicApp]}


def createApp(name, ui):
    '''Builds the app with this name, or a placeholder icon if there isn't one yet'''
    if name in APPS:
        return APPS[name](ui)
    return PlaceholderApp(ui, name)
