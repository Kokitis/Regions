import geopandas
from dataclasses import dataclass

def importCensusTract(filename):
	metadata = {
		'url': '',
		'type': 'census tract',
		'length': ''
	}

	df = geopandas.read_file()

