import configparser
import os

config = configparser.RawConfigParser()

CONFIGPATH = os.path.join(os.path.dirname(__file__), 'config.cfg')
config.read(CONFIGPATH)



def updateConfig(**kwargs):
    for key in kwargs:
        if key in config['DEFAULT']:
            config['SETTINGS'][str(key)] = str(kwargs[key])
    with open(CONFIGPATH, 'w') as configFile:
        config.write(configFile)


def resetConfig():
    config.clear()
    with open(CONFIGPATH, 'w') as configFile:
        config.write(configFile)

