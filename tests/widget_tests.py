import unittest

from common import DATASET, widgets

region_list = ['United States of America', 'Canada']

class TestWidgets(unittest.TestCase):
	def testExtractRegion(self):
		candidates = widgets.extractRegion(DATASET, region_list)

		result = [(i in ['USA', 'CAN']) for i in candidates]
		assert result
	def testTableConversion(self):
		pass
