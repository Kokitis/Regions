
import unittest

from pony.orm import db_session

from common import *

subject_code = 'LP'
database = DATASET

class VerifyEntityData(unittest.TestCase):
	"""Verifies the integrity of the data in each object."""
	@classmethod
	def setUpClass(cls):
		print('Setting Up')

		region = database.getRegion('USA')
		series = region.getSeries(subject_code)

		cls.region = region
		cls.series = series

	def testRegionData(self):
		""" Verifies that the data contained in an extracted region
			matches a truthest 
		"""

		assert self.region.name == TEST_REGION['name'] 
		assert self.region.parentRegion == TEST_REGION['parentRegion']
		assert self.region.regionType == TEST_REGION['regionType']

	def testSeriesData(self):

		assert self.series.code == TEST_SERIES['code']
		assert self.series.description == TEST_SERIES['description']
		assert self.series.name == TEST_SERIES['name']
		assert self.series.notes == TEST_SERIES['notes']
		assert self.series.region.name == TEST_SERIES['region']
		assert self.series.report.name == TEST_SERIES['report']
		assert self.series.scale.string == TEST_SERIES['scale']
		assert self.series.unit.string == TEST_SERIES['unit']
		assert self.series.strvalues == TEST_SERIES['strvalues']

		assert all([i==j] for i, j in zip(self.series.values, TEST_SERIES['values']))

	def testReportData(self):

		report = self.series.report 

		assert report.agency.name == TEST_REPORT['agency']
		assert report.code == TEST_REPORT['code']
		assert report.name == TEST_REPORT['name']
		assert report.publishDate == TEST_REPORT['publishDate']
		assert report.retrievedDate == TEST_REPORT['retrievedDate']
		assert report.url == TEST_REPORT['url']

	def testIdentifierData(self):
		identifier = [ i for i in self.region.identifiers if i.string == 'USA'][0]

		assert identifier.namespace.name == TEST_IDENTIFIER['namespace']
		assert identifier.region.name == TEST_IDENTIFIER['region']
		assert identifier.string == TEST_IDENTIFIER['string']

	def testAgencyData(self):
		agency = self.series.report.agency
		assert agency.address == TEST_AGENCY['address']
		assert agency.code == TEST_AGENCY['code']
		assert agency.name == TEST_AGENCY['name']
		assert agency.url == TEST_AGENCY['url']

	def testNamespaceData(self):
		pass
	
	def testTagData(self):
		pass

	def testUnitData(self):
		unit = self.series.unit 
		assert unit.code == TEST_UNIT['code']
		assert unit.string == TEST_UNIT['string']
	
	def testScaleData(self):
		scale = self.series.scale 
		assert scale.multiplier == TEST_SCALE['multiplier']
		assert scale.string == TEST_SCALE['string']
