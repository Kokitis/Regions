from series_tests import TestSeriesMethods
from entity_tests import VerifyEntityData
from database_tests import TestDataset
from widget_tests import TestWidgets
from pony.orm import db_session
import unittest

with db_session:
	unittest.main()