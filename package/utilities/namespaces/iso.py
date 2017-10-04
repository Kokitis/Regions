import os


from pony.orm import db_session

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
		'regionName': region_name,
		'regionType': 'country',
		'identifiers': [region_code_iso2, region_code_iso3]
	}

	if str(region_code_num) != 'nan':
		result['identifiers'].append("{:>03}".format(int(region_code_num)))

	return result


@db_session
def importIsoNamespace(dataset):
	""" Imports the identifiers and regions defined in the
		ISO2, ISO3, and numeric ISO namespace into the provided
		database.
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

	namespace = dataset.access('insert', 'namespace', **iso_namespace)

	for index, row in enumerate(table):
		result = isoParser(row)

		if result is None: 
			message = "Could not parse the row with index ({})".format(index)
			print(message)
			for k, v in sorted(row.items()):
				print("\t{}:\t{}".format(k, v))
			continue

		region_type = result['regionType']
		region_name = result['regionName']
		if isinstance(region_name, float) or region_name == 'nan':
			continue

		region = dataset.getRegion([region_name] + result['identifiers'], namespace)

		if region is None:
			region = dataset.access('insert', 'region', name = region_name, regionType = region_type)


		if region is None:
			message = "Could not create the region: "
			print(message)
			print("\t", region_name)
			print("\t", region_type)
			continue


		for identifier_string in result['identifiers']:
			_identifier_is_nan = isinstance(identifier_string, float) or str(identifier_string) == 'nan'
			if identifier_string is None or _identifier_is_nan:
				continue
			identifier_config = {
				'namespace': namespace,
				'region': region,
				'value': identifier_string
			}

			dataset.access('insert', 'identifier', **identifier_config)
	return namespace
