import unittest
import pyregions
from .setup_tests import importTestData
import os
from pony.orm import db_session
import datetime

series_code = 'POP'
region_code = 'USA-NY'
DATABASE_FILENAME = os.path.join(os.path.dirname(__file__), 'test_data', 'test_database.sqlite')
TEST_DATABASE = pyregions.RegionDatabase(DATABASE_FILENAME, True)
TEST_DATABASE.addNamespace('ISO')
TEST_DATABASE.addNamespace('USPS')
TEST_DATABASE.addFromApi(importTestData())


class TestRegionDatabase(unittest.TestCase):
	def setUp(self):
		self.database_filename = ''
		self.database = TEST_DATABASE

	def test_get_entity_class_for_region(self):
		self.assertTrue(self.database._getEntityClass('region').entity_type == 'region')

	def test_get_entity_class_for_identifier(self):
		self.assertTrue(self.database._getEntityClass('identifier').entity_type == 'identifier')

	def test_get_entity_class_for_namespace(self):
		self.assertTrue(self.database._getEntityClass('namespace').entity_type == 'namespace')

	def test_get_entity_class_for_report(self):
		self.assertTrue(self.database._getEntityClass('report').entity_type == 'report')

	def test_get_entity_class_for_scale(self):
		self.assertTrue(self.database._getEntityClass('scale').entity_type == 'scale')

	def test_get_entity_class_for_unit(self):
		self.assertTrue(self.database._getEntityClass('unit').entity_type == 'unit')

	def test_get_entity_class_for_series(self):
		self.assertTrue(self.database._getEntityClass('series').entity_type == 'series')

	def test_get_entity_class_for_agency(self):
		self.assertTrue(self.database._getEntityClass('agency').entity_type == 'agency')

	def test_get_entity_key_for_region(self):
		self.assertTrue(self.database._getEntityKey('region') == 'code')

	def test_get_entity_key_for_namespace(self):
		self.assertTrue(self.database._getEntityKey('namespace') == 'code')

	def test_get_entity_key_for_agency(self):
		self.assertTrue(self.database._getEntityKey('agency') == 'name')

	def test_get_entity_key_for_report(self):
		self.assertTrue(self.database._getEntityKey('report') == 'name')

	def test_get_entity_key_for_scale(self):
		self.assertTrue(self.database._getEntityKey('scale') == 'string')

	def test_get_entity_key_for_unit(self):
		self.assertTrue(self.database._getEntityKey('unit') == 'string')

	def test_get_entity_key_for_tag(self):
		self.assertTrue(self.database._getEntityKey('tag') == 'string')

	def test_get_entity_key_for_identifier(self):
		self.assertTrue(self.database._getEntityKey('identifier') == 'string')

	def test_get_entity_key_for_series(self):
		a = self.database._getEntityKey('series')
		b = ('code', 'region', 'report')

		self.assertTrue(a == b)

	def test_get_primary_key_for_region(self):
		a = self.database._getEntityPrimaryKey('region', 'USA')
		self.assertTrue(a['code'] == 'USA')

	def test_get_primary_key_for_series(self):
		a = self.database._getEntityPrimaryKey('series', ('first', 'second', 'third'))
		self.assertTrue(a['code'] == 'first')
		self.assertTrue(a['region'] == 'second')
		self.assertTrue(a['report'] == 'third')

	def test_get_primary_key_for_report(self):
		a = self.database._getEntityPrimaryKey('report', 'report_name')
		self.assertTrue(a['name'] == 'report_name')

	def test_get_primary_key_for_scale(self):
		a = self.database._getEntityPrimaryKey('scale', 'string')
		self.assertTrue(a['string'] == 'string')

	def test_get_primary_key_for_unit(self):
		a = self.database._getEntityPrimaryKey('unit', 'unit_string')
		self.assertTrue(a['string'] == 'unit_string')

	def test_get_primary_key_for_agency(self):
		a = self.database._getEntityPrimaryKey('agency', 'agency_name')
		self.assertTrue(a['name'] == 'agency_name')

	def test_add_namespace_iso(self):
		iso_namespace = self.database.addNamespace('ISO')
		self.assertTrue(iso_namespace.code == 'ISO')

	def test_add_namespace_usps(self):
		usps_namespace = self.database.addNamespace('USPS')
		self.assertTrue(usps_namespace.code == 'USPS')

	@db_session
	def test_entity_exists(self):
		a = self.database.exists('region', 'USA')
		b = self.database.exists('region', 'ABC')

		self.assertTrue(a)
		self.assertFalse(b)

	@db_session
	def test_get_series_by_str(self):
		test_series = self.database.getSeries(region_code, series_code, to_entity = True)
		series_data = test_series.toDict()

		assert series_data
		assert series_data['entityType'] == 'series'
		# assert series_data['entityKey'] == series_code
		assert series_data['seriesCode'] == test_series.code
		assert series_data['seriesName'] == test_series.name
		assert series_data['seriesDescription'] == test_series.description
		assert series_data['seriesNotes'] == test_series.notes
		# assert test_series['seriesReport'] == test_series.report
		# assert test_series['seriesRegion']
		assert all(i == j for i, j in zip(series_data['seriesValues'], test_series.values))

	@db_session
	def test_get_series_by_region_entity_and_str(self):
		region_entity = self.database.getRegion('USA-NY')
		test_series = self.database.getSeries(region_entity, 'POP')
		assert test_series['seriesCode'] == 'POP'

	@db_session
	def test_get_region_by_region_code(self):
		region_entity = self.database.getRegion('USA-NY')

		assert region_entity.name == 'New York'
		assert region_entity.type == 'state'
		assert region_entity.code == 'USA-NY'

	@db_session
	def test_get_region_by_identifier(self):
		identifier = self.database.Identifier.get(string = 'NY')
		region_entity = self.database.getRegion(identifier)

		assert region_entity.name == 'New York'

	@db_session
	def test_get_region_by_region_entity(self):
		region = self.database.Region['USA-NY']
		region_entity = self.database.getRegion(region)

		assert region_entity.name == 'New York'

	@db_session
	def test_select_region(self):
		func = lambda s: s.code == 'USA'
		a = self.database.select('region', func)
		self.assertTrue(a.first().code == 'USA')

	def test_get_regions(self):
		region_codes = ['USA-NY', 'USA-PA', 'USA-NJ']

		regions = list(self.database.getRegions(region_codes))

		self.assertTrue(regions[0].code == region_codes[0])
		self.assertTrue(regions[1].code == region_codes[1])
		self.assertTrue(regions[2].code == region_codes[2])

	@db_session
	def test_insert_region_by_custom_method(self):
		test_namespace = self.database.Namespace.select(lambda s: s).first()
		test_region = {
			'regionName': 'testRegion',
			'regionCode': 'testRegionCode',
			'regionType': 'testRegionType'
		}

		test_entity = self.database._insertRegion('testRegionCode', test_region, test_namespace)

		self.assertTrue(test_entity.name == test_region['regionName'])
		self.assertTrue(test_entity.code == test_region['regionCode'])
		self.assertTrue(test_entity.type == test_region['regionType'])

		self.database._main_database.rollback()

	@db_session
	def test_insert_series(self):
		"""
					data = {
				'entityType':        'series',
				'entityKey':         self.key,
				'seriesRegion':      series_region,
				'seriesReport':      series_report,
				'seriesCode':        self.code,
				'seriesName':        self.name,
				'seriesDescription': self.description,
				'seriesNotes':       self.notes,
				'seriesUnits':       series_units,
				'seriesScale':       series_scale,
				'seriesValues':      series_values,
				'seriesTags':        list(),
			}
		Returns
		-------

		"""
		test_unit = self.database.Unit.get(string = 'Persons')
		test_scale = self.database.Scale.get(string = 'unit')
		test_region = self.database.Region['USA']

		test_report = self.database.Report['Population of US States']

		test_series = {
			'seriesName':        "Test Series Name",
			'seriesCode':        "testSeriesCode",
			'seriesDescription': "testDescription",
			'seriesNotes':       "testNotes",
			'seriesUnits':       test_unit,
			'seriesScale':       test_scale,
			'seriesRegion':      test_region,
			'seriesReport':      test_report,
			'seriesTags':        ["testTag1", "testTag2", "testTag3"],
			'seriesValues':      [("2015-01-01", 13), ("2018-02-03", 25)]
		}
		test_entity = self.database._insertSeries(test_series['seriesCode'], test_region, test_report, test_series)

		self.assertTrue(test_entity.name == test_series['seriesName'])
		self.database._main_database.rollback()

	@db_session
	def test_insert_unit(self):
		test_unit = {
			'string': 'testUnit',
			'code':   'testCode'
		}
		test_entity = self.database._insertEntity('unit', **test_unit)
		self.assertTrue(test_entity.code == test_unit['code'])
		self.assertTrue(test_entity.string == test_unit['string'])
		self.database._main_database.rollback()

	@db_session
	def test_insert_scale(self):
		test_scale = {
			'string':     'testScale',
			'multiplier': -1.0
		}
		test_entity = self.database._insertEntity('scale', **test_scale)
		self.assertTrue(test_entity.string == test_scale['string'])
		self.assertTrue(test_entity.multiplier == test_scale['multiplier'])
		self.database._main_database.rollback()

	@db_session
	def test_insert_agency(self):
		test_agency = {
			'name':    'Test Agency',
			'code':    'testCode',
			'address': 'test_address',
			'url':     'https:/test.url'
		}
		test_entity = self.database._insertEntity('agency', **test_agency)
		self.assertTrue(test_entity.name == test_agency['name'])
		self.assertTrue(test_entity.code == test_agency['code'])
		self.assertTrue(test_entity.address == test_agency['address'])
		self.database._main_database.rollback()

	@db_session
	def test_insert_report(self):
		test_agency = self.database.Agency.get(name = 'United States Census Bureau')

		test_report = {
			'name':   'Test Report',
			'code':   'testCase',
			'agency': test_agency,
			'date':   "2018-01-01",
			'url':    'https://test.url'
		}
		test_entity = self.database._insertEntity('report', **test_report)

		self.assertTrue(test_entity.name == test_report['name'])
		self.assertTrue(test_entity.code == test_report['code'])
		self.database._main_database.rollback()

	@db_session
	def test_get_data(self):
		data = self.database.getData('region', 'USA-NY')

		self.assertTrue(data['regionName'] == 'New York')
		self.assertTrue(data['regionCode'] == 'USA-NY')
		self.assertTrue(data['regionType'] == 'state')


if __name__ == "__main__":
	unittest.main()
