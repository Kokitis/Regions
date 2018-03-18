import pathlib
import pandas
from pprint import pprint
import pyregions
import yaml
import os
import json

def saveConfiguration(config, filename):
	"""

	Parameters
	----------
	config: dict<>
	filename: str

	Returns
	-------

	"""


	with open(filename + '.yaml', 'w') as file2:
		data = json.dumps(config)
		data = json.loads(data)
		file2.write(yaml.dump(data, default_flow_style = False, indent = 4))

def importTestData():
	"""
		Expected Format:
		* 'namespace": str, dict<>
		* 'report': dict<>
			* 'reportName': str
			* 'reportCode': str
			* 'reportAgency': dict<>
				* 'agencyName': str
				* 'agencyCode': str
				* 'agencyAddress': str
				* 'agencyUrl': str
			* 'reportDate': Timestamp
			* 'reportUrl': str
		* 'reportData': list<dict<>>
			* 'regionCode': str
			* 'regionName': str
			* 'regionType': str
			* 'regionIdentifiers': list<>
			* 'regionSeries': dict<>
				* 'seriesName': str
				* 'seriesCode': str
				* 'seriesDescription': str
				* 'seriesNotes': str
				* 'seriesTags: list<str>
				* 'seriesUnits': str, dict<>
				* 'seriesScale': str, dict<>

	"""

	state_codes_filename = os.path.join(os.path.dirname(__file__),'test_data', 'state_codes.xlsx')
	state_codes = pandas.read_excel(state_codes_filename)
	state_abr = state_codes['Official United States Postal Service (USPS) Code'].values
	state_names = state_codes['Name'].values
	state_codes = {k: v for k, v in zip(state_abr, state_names)}
	filename = os.path.join(os.path.dirname(__file__), 'test_data', 'Annual State Populations.xlsx')

	table = pandas.read_excel(filename)
	regions = list()

	for index, row in table.iterrows():

		region_code = row['ISO Code']
		state_code = row['State Code']

		if state_code == 'US':
			region_code = 'USA'
			region_name = 'United States'
			region_type = 'country'
			region_parent = None
		else:
			region_name = state_codes.get(str(region_code)[-2:])
			region_type = 'state'
			region_parent = 'USA'

		if region_name is None or isinstance(region_code, float): continue

		series_values = [(i, j) for i, j in row.items() if isinstance(i, int)]

		region_series = {
			'seriesName':        'Population',
			'seriesCode':        'POP',
			'seriesDescription': 'Population from 1900 to present.',
			'seriesTags':        ['states', 'population'],
			'seriesUnits':       'Persons',
			'seriesScale':       'unit',
			'seriesNotes':       'For testing purposes',
			'seriesValues':      series_values
		}

		region = {
			'regionCode':   region_code,
			'regionName':   region_name,
			'regionType':   region_type,
			'regionParent': region_parent,
			'regionSeries': [region_series]
		}
		regions.append(region)

	agency = {
		'agencyCode':    'CEN',
		'agencyName':    "United States Census Bureau",
		'agencyUrl':     "https://www.census.gov",
		# 'wiki': "https://en.wikipedia.org/wiki/United_States_Census_Bureau",
		'agencyAddress': "4600 Silver Hill Road, Washington, DC 20233"
	}
	report = {
		'reportCode': 'USPOP',
		'reportName': 'Population of US States',
		'reportDate': '2018-03-03',
		'reportUrl': 'No URL'
	}


	api_response = {
		'agency':    agency,
		'report':    report,
		'namespace': 'USPS',
		'regions':   regions
	}

	pyregions.utilities.ValidateApiResponse(api_response)

	return api_response
test_database_filename = os.path.join(os.path.dirname(__file__), 'test_data', 'test_database.sqlite')
test_database = pyregions.RegionDatabase(test_database_filename, True)
if __name__ == "__main__":
	response = importTestData()
	#saveConfiguration(response, os.path.join(os.path.dirname(__file__), 'test_response.yaml'))
	#pprint(response, width = 180)
	test_database_filename = os.path.join(os.path.dirname(__file__), 'test_data', 'test_database.sqlite')
	test_database = pyregions.RegionDatabase(test_database_filename, True, replace = True)
	test_database.addFromApi(response)
	#test_database.summary()

