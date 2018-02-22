import os


from ...github import tabletools
from ._common import namespace_data_folder

FILENAME = os.path.join(namespace_data_folder, "country-codes.xlsx")

def isoParser(row):
	""" Returns a list of the identifiers contained in the row. """
	region_name 	 = row["official_name_en"]
	region_code_iso2 = row['ISO3166-1-Alpha-2']
	region_code_iso3 = row['ISO3166-1-Alpha-3']
	region_code_num  = row['M49']# "{:>03}".format(row['M49'])

	result = {
		'name': region_name,
		'regionType': 'country',
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
	result['standardCode'] = standard_code

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
	filename = FILENAME

	table = tabletools.Table(filename)

	iso_namespace = {
		'code': 'ISO',
		'name': "International Organization for Standardization",
		'subtypes': "iso2|iso3|numeric",
		'regex': "(?P<iso2>[A-Z]{2})|(?P<iso3>[A-Z]{3})|(?P<numeric>[0-9]{3})",
		'url': "https://www.iso.org/iso-3166-country-codes.html",
	}
	iso_regions = list()
	for index, row in enumerate(table):
		region_data = isoParser(row)
		#pprint(region_data)
		if not isinstance(region_data['name'], str) or not isinstance(region_data['standardCode'], str):
			continue
		iso_regions.append(region_data)

	namespace_data = {
		'namespace': iso_namespace,
		'regions': iso_regions
	}
	return namespace_data
