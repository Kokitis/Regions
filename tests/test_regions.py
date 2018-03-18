import unittest
from pony.orm import db_session

series_code = 'POP'
region_code = 'USA-NY'
import os
import pyregions
from .setup_tests import importTestData


class TestRegion(unittest.TestCase):
	def setUp(self):
		self.database_filename = os.path.join(os.path.dirname(__file__), 'test_data', 'test_database.sqlite')
		self.database = pyregions.RegionDatabase(self.database_filename, True, replace = False)
		self.database.addNamespace('ISO')
		self.database.addNamespace('USPS')
		self.database.addFromApi(importTestData())

	@db_session
	def test_parent_region(self):
		tparent = self.database.getRegion('USA')
		tchild = self.database.getRegion('USA-NY')

		self.assertTrue(tchild in tparent.subregions)
		self.assertTrue(tchild.parent == tparent)

	@db_session
	def test_region_to_dict(self):
		region_entity = self.database.getRegion('USA-NY')

		region_data = region_entity.toDict()

		self.assertTrue(region_data['regionName'] == region_entity.name)
		self.assertTrue(region_data['regionCode'] == region_entity.code)
		self.assertTrue(region_data['regionType'] == region_entity.type)

	class TestIdentifiers(unittest.TestCase):
		def setUp(self):
			self.database = None

		def test_find_region_when_multiple_identifiers_exist(self):
			identifierA = ''
			identifierB = ''

			regionA = self.database.getRegion(identifierA)
			regionB = self.database.getRegion(identifierB)


if __name__ == "__main__":
	unittest.main()
