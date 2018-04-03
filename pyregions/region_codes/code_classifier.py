import pathlib
import pandas
from fuzzywuzzy import process
import dataclasses

file_path = pathlib.Path(__file__)
country_codes_filename = pathlib.Path(file_path.parent, 'data', 'country-codes.xlsx')
from pprint import pprint
from typing import *


@dataclasses.dataclass
class Namespace:
	pass



def loadRegionCodesISO():
	pass


class RegionCodeClassifier:
	# http://www.unece.org/cefact/locode/welcome.html
	def __init__(self):
		country_table = pandas.read_excel(country_codes_filename)
		regions = list()
		# name	official_name_en	official_name_fr	ISO3166-1-Alpha-2	ISO3166-1-Alpha-3	M49	ITU	MARC
		## WMO	DS	Dial	FIFA	FIPS	GAUL	IOC	ISO4217-currency_alphabetic_code	ISO4217-currency_country_name
		# ISO4217-currency_minor_unit	ISO4217-currency_name	ISO4217-currency_numeric_code	is_independent	Capital	Continent
		# TLD	Languages	Geoname ID	EDGAR

		for index, row in country_table.iterrows():
			country_name = row['official_name_en']
			if isinstance(country_name, float): continue
			country_iso2 = row["ISO3166-1-Alpha-2"]
			country_iso3 = row['ISO3166-1-Alpha-3']

			region = {
				'name':      country_name,
				'type':      'country',
				'iso2':      country_iso2,
				'iso3':      country_iso3,
				'parent':    None,
				'm49':       row['M49'],
				'fips':      row['FIPS'],
				'currency':  row['ISO4217-currency_name'],
				'continent': row['Continent'],
				'languages': row['Languages'],
				'geoname':   '{:>07}'.format(row['Geoname ID'])
			}
			regions.append(region)
		self.regions = {i['name'].lower(): i for i in regions}

	def search(self, string, tolerance = 90):
		index, score = process.extractOne(string.lower(), self.regions.keys())
		if score >= tolerance:
			best_match = self.regions[index]
		else:
			best_match = None
		return best_match
	def definedRegions(self):
		pass


if __name__ == "__main__":
	classifier = RegionCodeClassifier()
	fname = pathlib.Path(
		pathlib.Path().home()) / 'Google Drive' / 'Region Data' / 'Global' / 'Historical Datasets' / 'horizontal-file_02-2010.xls'
	table = pandas.read_excel(fname, sheetname = 'Population')
	for index, row in table.iterrows():
		country_name = str(row[0])
		candidate = classifier.search(country_name)
		if candidate:
			print("{}|{}".format(candidate['name'], candidate['iso3']))
		else:
			print(country_name)

# pprint(classifier.search('United States of America'))
