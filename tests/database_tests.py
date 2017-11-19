
from .. import *

def loadDatabase():
	database = RegionDatabase('global')
	return database

def testRegionLookup():
	database = loadDatabase()
	sample_region_key = 'USA'

	region = database.getRegion(sample_region_key)

	assert 'United States' in region.name 