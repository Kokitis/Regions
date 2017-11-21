from series_tests import TestSeriesMethods
from entity_tests import VerifyEntityData
from pony.orm import db_session
import unittest

with db_session:
	unittest.main()