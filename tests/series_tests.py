import unittest

from pony.orm import db_session

from package import *

subject_code = 'LP'
database = RegionDatabase('test')

def _applyArithmetic(y, other_y, operation):
	# Basic operations
	if operation == '+':
		new_y = y + other_y
	elif operation == '-':
		new_y = y - other_y
	elif operation == '*':
		new_y = y * other_y
	elif operation == '/':
		new_y = y / other_y

	# Relational operations
	elif operation == '==':
		new_y = y == other_y
	elif operation == '>=':
		new_y = y >= other_y
	elif operation == '>':
		new_y = y > other_y
	elif operation == '<':
		new_y = y < other_y
	elif operation == '<=':
		new_y = y <= other_y 
	elif operation == '!=':
		new_y = y != other_y

	elif operation == '%':
		# Relative change
		new_y = (other_y - y) / y 
	else:
		message = "Invalid operation: '{}'".format(operation)
		raise ValueError(message)

	return new_y
@db_session
def testSeriesArithmetic(series, other_series, operation):
	""" Assume series 1 is USA and series 2 is Canada"""
	results = list()
	actual_values = {a[0]: _applyArithmetic(a[1], b[1], operation) for a, b in zip(series.values, other_series.values)}
	
	addition = _applyArithmetic(series, other_series, operation)

	for y, v in addition:
		results.append(v == actual_values[y])
	
	return all(results)

def testScalarArithmetic(series, scalar, operation):
	new_series = _applyArithmetic(series, scalar, operation)

	bool_series = list()

	for a, b in zip(series, new_series):
		
		left = _applyArithmetic(a[1], 5, operation) 
		right= b[1]

		bool_series.append(left == right)
		bool_series.append(a[0] == b[0])
	return all(bool_series)



class TestSeries(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		print('Setting Up')

		region = database.getRegion('USA')
		series = region.getSeries(subject_code)

		other_region = database.getRegion('CAN')
		other_series = other_region.getSeries(subject_code)

		cls.series = series
		cls.other_series = other_series
		cls.scalar = 5
		print(cls.series)
		print(cls.other_series)
	
	################### Series Arithmetic #######################
	@db_session
	def testSeriesAddition(self):
		self.assertTrue(testSeriesArithmetic(self.series, self.other_series, '+'))
		self.assertTrue(testScalarArithmetic(self.series, self.scalar, '+'))
	@db_session
	def testSeriesSubtraction(self):
		self.assertTrue(testSeriesArithmetic(self.series, self.other_series, '-'))
		#self.assertTrue(testScalarArithmetic(self.series, self.scalar, '-'))
	@db_session
	def testSeriesMultiplication(self):
		self.assertTrue(testSeriesArithmetic(self.series, self.other_series, '*'))
		self.assertTrue(testScalarArithmetic(self.series, self.scalar, '*'))
	@db_session
	def testSeriesDivision(self):
		self.assertTrue(testSeriesArithmetic(self.series, self.other_series, '/'))
		#self.assertTrue(testScalarArithmetic(self.series, self.scalar, '/'))

	def testSeriesPercentChange(self):
		self.assertTrue(testSeriesArithmetic(self.series, self.other_series, '%'))
		#self.assertTrue(testScalarArithmetic(self.series, self.scalar, '%'))

	################## Series Methods ##############################
	def testSeriesYearlyChangeGrowth(self):
		pass

def runSeriesTests():
	with db_session:
		unittest.main()
