import unittest
import pyregions
import os
from .setup_tests import importTestData
DATA_FOLDER = os.path.join(os.getenv('USERPROFILE'), 'Google Drive', 'Region Data', 'Global')

class TestImports(unittest.TestCase):
	def setUp(self):
		self.database_filename = os.path.join(os.path.dirname(__file__), 'test_data', 'test_database.sqlite')
		self.database = pyregions.RegionDatabase(self.database_filename, True, replace = False)
		self.database.addNamespace('ISO')
		self.database.addNamespace('USPS')
		self.database.addFromApi(importTestData())
	def test_weo_import(self):
		configuration = pyregions.widgets.getWorldEconomicOutlookConfiguration()

		filename = os.path.join(DATA_FOLDER, "WEOApr2017all.xlsx")
		response = pyregions.widgets.TableApi(filename, **configuration).data
		self.database.addFromApi(response)


if __name__ == "__main__":
	#unittest.main()
	TestImports.test_weo_import(None)