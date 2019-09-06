# encoding: UTF-8


import os
import sys


ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
print ROOT_PATH

sys.path.append(ROOT_PATH)
#import vnpy
from vnpy.event import EventEngine2
ee = EventEngine2()