
from .test_regions import *
from .test_series import *
from .test_widgets import *
from pony.orm import db_session
import unittest

with db_session:
	unittest.main()