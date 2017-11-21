import os
import sys
sys.path.append(os.path.join(os.getenv('USERPROFILE'), 'Documents', 'Github'))

from Regions.package import *
from pytools import tabletools
from .test_objects import *

TRUTHSET = tabletools.Table(os.path.join(os.path.dirname(__file__), 'truthset.xlsx'))
