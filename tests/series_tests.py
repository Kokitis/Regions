import unittest
import math
from pony.orm import db_session

from common import *

subject_code = 'LP'
database = DATASET

def checkSeriesValues(series, key):
	truthset = TRUTHSET('subjectName', key)
	scale = series.scale 
	if scale is None:
		scale = 1.0
	values = sorted([(y,v) for y, v in truthset.items() if isinstance(y, int)])
	values = [(y, v*scale) for y, v in values]

	checked = [(l[0] == r[0] and math.isclose(l[0], r[0])) for l, r in zip(values, sorted(series.values))]
	result = all(checked)
	if not result:
		for left, right in zip(values, series.values):
			print("{} != {}".format(left, right))
	
	return result

class TestSeriesMethods(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		print('Setting Up')

		region = database.getRegion('USA')
		series = region.getSeries(subject_code)

		other_region = database.getRegion('CAN')
		other_series = other_region.getSeries(subject_code)

		cls.left = series
		cls.right = other_series
		cls.scalar = 5
	
	################### Series Arithmetic #######################
	@db_session
	def testSeriesAddition(self):
		addition_series = self.left + self.right 
		assert checkSeriesValues(addition_series, 'addition')
	def testSeriesSubtraction(self):
		subtraction_series = self.left - self.right
		assert checkSeriesValues(subtraction_series, 'subtraction')
	def testSeriesMultiplication(self):
		multiplication_series = self.left * self.right 
		assert checkSeriesValues(multiplication_series, 'multiplication')
	def testSeriesDivision(self):
		division_series = self.left / self.right 

		assert checkSeriesValues(division_series, 'division')
	def testSeriesInterpolation(self):
		pass

	def testYearlyChange(self):
		change_series = self.left.timeChange('yearlyChange')
		growth_series = self.left.timeChange('yearlyGrowth')
		dtime_series  = self.left.timeChange('doublingTime')
		dyear_series  = self.left.timeChange('doublingYear')
		cumulative_series = self.left.timeChange('cumulative')

		assert checkSeriesValues(change_series, 'yearlyChange')
		assert checkSeriesValues(growth_series, 'yearlyGrowth')
		assert checkSeriesValues(dtime_series, 'doublingTime')
		assert checkSeriesValues(dyear_series, 'doublingYear')
		assert checkSeriesValues(cumulative_series, 'cumulative')
	
	def testIndexYear(self):
		year = 2000
		index_series = self.left.indexYear(year)
		assert checkSeriesValues(index_series, 'indexYear')

	def testSeriesCall(self):
		valid_year = 


def runSeriesTests():
	with db_session:
		unittest.main()
