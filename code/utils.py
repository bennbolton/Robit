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
    config.add_section('SETTINGS')
    with open(CONFIGPATH, 'w') as configFile:
        config.write(configFile)



def getConfig(*keys):
    for key in keys:
        if key in config['DEFAULT']:
            return eval(config['SETTINGS'][str(key)])
        

