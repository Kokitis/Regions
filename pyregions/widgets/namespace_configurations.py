
from .configuration_tools import *
from ..data import configuration
from typing import *

ISO_NAMESPACE_FILENAME: str = configuration.files['ISO Namespace']
import pandas

def isoParser(row: Mapping)->Dict[str,str]:
	""" Returns a list of the identifiers contained in the row. """
	region_name = row["official_name_en"]
	region_code_iso2 = row['ISO3166-1-Alpha-2']
	region_code_iso3 = row['ISO3166-1-Alpha-3']
	region_code_num = row['M49']  # "{:>03}".format(row['M49'])

	result = {
		'name':        region_name,
		'type':        'country',
		'identifiers': [region_code_iso2, region_code_iso3]
	}

	if str(region_code_num) != 'nan':
		result['identifiers'].append("{:>03}".format(int(region_code_num)))
	result['identifiers'] = [i for i in result['identifiers'] if isinstance(i, str)]
	standard_code = [i for i in result['identifiers'] if (len(i) == 3 and i.isalpha())]

	if len(standard_code) == 1:
		standard_code = standard_code[0]
	else:
		standard_code = None
	result['code'] = standard_code

	return result


def importIsoNamespace():
	""" Imports the identifiers and regions defined in the
		ISO2, ISO3, and numeric ISO namespace into the provided
		database.
		Returns
		-------
		dict<>
		* 'namespace': dict<>
			* 'code': str
			* 'name': str
			* 'subtypes': str
			* 'regex': str
			* 'url': str
		* 'regions': list<dict<>>
			* 'regionName': str
			* 'regionCode': str
			* 'regionType': str
			* 'identifiers': list<str>
	"""

	configuration_filename:str = getFilename('iso_namespace')
	iso_configuration = loadConfiguration('iso_namespace')

	if not iso_configuration:
		filename:str = ISO_NAMESPACE_FILENAME
		table = pandas.read_excel(filename)

		iso_namespace:Dict[str,str] = {
			'code':     'ISO',
			'name':     "International Organization for Standardization",
			'subtypes': "iso2|iso3|numeric",
			'regex':    "(?P<iso2>[A-Z]{2})|(?P<iso3>[A-Z]{3})|(?P<numeric>[0-9]{3})",
			'url':      "https://www.iso.org/iso-3166-country-codes.html",
		}
		iso_regions = list()
		for index, row in table.iterrows():
			region_data = isoParser(row)
			if not isinstance(region_data['name'], str) or not isinstance(region_data['code'], str):
				continue
			iso_regions.append(region_data)

		iso_configuration = {
			'namespace': iso_namespace,
			'regions':   iso_regions
		}
		saveConfiguration(iso_configuration, configuration_filename)
	return iso_configuration

def importNutsNamespace():
	raise NotImplementedError

def importFipsNamespace():
	fips_namespace = {
		'code':   'FIPS',
		'name':   "Federal Information Processing Standards",
		'regex':  "(?P<state>[\d]{2})(?P<county>[\d]{3})",
		'url':    "https://www.census.gov/geo/reference/codes/cou.html"
	}
	fips_configuration = {
		'namespace': fips_namespace,
		'regions': ''
	}
def importUSPSNamespace():
	configuration_filename = getFilename('usps_namespace')
	usps_configuration = loadConfiguration(configuration_filename)
	if not usps_configuration:
		filename = configuration.files['USPS Namespace']
		print("Filename: ", filename)
		table = pandas.read_excel(filename)
		regions = [
			{
				'name': 'United States',
				'type': 'country',
				'identifiers': ['US'],
				'code': 'USA'
			}
		]
		for index, row in table.iterrows():
			region_code = row['Official United States Postal Service (USPS) Code']
			standard_code = 'USA-' + region_code
			region_data = {
				'name': row['Name'],
				'type': 'state',
				'identifiers': [region_code],
				'code': standard_code
			}
			regions.append(region_data)

		usps_namespace = {
			'code': 'USPS',
			'name': 'United States Postal Service',
			'subtypes': "N/A",
			'regex': '[A-Z]{2}',
			'url': 'https://en.wikipedia.org/wiki/List_of_U.S._state_abbreviations'
		}

		usps_configuration = {
			'namespace': usps_namespace,
			'regions': regions
		}
		return usps_configuration

