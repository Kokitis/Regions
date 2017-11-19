import unittests
from pony.orm import db_session


class TestRegions(unittest.TestCase):
	def testRegionGetSeries(self):
		pass

def runRegionTests():
	with db_session:
		unittest.main()


