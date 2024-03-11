from configparser import ConfigParser

config = ConfigParser()
config.sections()
config.read('config.ini')

class Configurator():