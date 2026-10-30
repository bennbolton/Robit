import configparser
import os

import pygame

config = configparser.RawConfigParser()

BASEDIR = os.path.dirname(os.path.abspath(__file__))
CONFIGPATH = os.path.join(BASEDIR, 'config.cfg')
IMGDIR = os.path.join(BASEDIR, 'data', 'imgs', 'icons')
# Jersey 10, SIL Open Font License (data/fonts/Jersey10-OFL.txt)
FONTPATH = os.path.join(BASEDIR, 'data', 'fonts', 'Jersey10-Regular.ttf')
TITLEFONTSIZE = 50
LABELFONTSIZE = 38
config.read(CONFIGPATH)



def updateConfig(**kwargs):
    for key in kwargs:
        if key in config['DEFAULT']:
            config['SETTINGS'][str(key)] = str(kwargs[key])
    with open(CONFIGPATH, 'w') as configFile:
        config.write(configFile)


def resetConfig():
    config.clear()
    config.add_section('SETTINGS')
    with open(CONFIGPATH, 'w') as configFile:
        config.write(configFile)



def getConfig(*keys):
    for key in keys:
        if key in config['DEFAULT']:
            return eval(config['SETTINGS'][str(key)])
        

def getDefaultConfig(key):
    if key in config['DEFAULT']:
        return eval(config['DEFAULT'][str(key)])



# ----- Drawing helpers -----

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


def loadIcon(path, size, colour):
    img = pygame.image.load(path)
    img = pygame.transform.scale(img, (size, size))
    return colourise(img, colour)


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

