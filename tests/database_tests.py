import unittest

from common import DATASET, TEST_IDENTIFIER, TEST_REGION, TEST_SERIES, TEST_REPORT

region_code = TEST_IDENTIFIER['string']
series_code = TEST_SERIES['code']

class TestDataset(unittest.TestCase):

	def testRegionLookup(self):
		region = DATASET.getRegion(region_code)

		assert region.name == TEST_REGION['name']
		assert region.parentRegion == TEST_REGION['parentRegion']
		assert region.regionType == TEST_REGION['regionType']

	def testSeriesLookup(self):

		series = DATASET.getSeries(region_code, series_code).first()

		assert series.name == TEST_SERIES['name']
		assert series.code == TEST_SERIES['code']

	def testDatasetAccess(self):
		invalid_code = 'BLAH'
		valid_code = TEST_REPORT['name']
		valid_report =DATASET.access('get', 'report', valid_code)
		invalid_report = DATASET.access('get', 'report', invalid_code)

		assert valid_report.code == TEST_REPORT['code']
		assert invalid_report is None 
