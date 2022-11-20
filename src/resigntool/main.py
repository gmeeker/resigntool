import configparser
import os
import sys
from . import sign

def run():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.expanduser("~"), '.resigntool.ini'))
    sys.exit(sign.sign(sys.argv, config=config))
