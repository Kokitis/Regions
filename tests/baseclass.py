
import pyregions
from .setup_tests import importTestData
import os
class BaseClass:

	def setUp(self):
		self.database_filename = os.path.join(os.path.dirname(__file__), 'test_data', 'test_database.sqlite')
		self.database = pyregions.RegionDatabase(self.database_filename, True, replace = False)
		self.database.addNamespace('ISO')
		self.database.addNamespace('USPS')
		self.database.addFromApi(importTestData())

