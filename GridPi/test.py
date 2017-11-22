from configparser import ConfigParser
from pprint import pprint

parser = ConfigParser()

parser.read('asset_cfg.ini')

for cfg in parser.sections():
    for key, val in parser[cfg].items():
        print(key, val)