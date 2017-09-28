from fuzzywuzzy import process
from pony.orm import select, db_session
import re

@db_session
def searchRegions(regions, dataset, namespace = 'ISO', subtype = 'iso3'):
	""" Attempts to match each region name given in `regions` with those present in the database.
		Parameters
		----------
		regions: list<str>	
			The region names to match.
		dataset: RegionDataset
			The dataset to search through. Required to load the requested namespace.
		namespace: str; default 'ISO'
			The namespace to search through. 
	"""
	namespace = dataset.access('get', 'namespace', code = namespace)
	print(namespace.regex)
	regex = re.compile(namespace.regex)
	regex = re.compile("(?P<iso3>[A-Z]{3})|(?P<iso2>[A-Z]{2})|(?P<numeric>[0-9]{3})")
	region_names = select(s.name for s in dataset.Region)
	table = list()
	for region_name in regions:
		best_match = region_name
		if best_match not in region_names:
			best_match, score = process.extractOne(region_name, region_names)
			if score < 90:
				best_match = None
			else:
				#print(best_match)
				best_match = dataset.access('search', 'region', best_match)
		else:
			best_match = dataset.access('get', 'region', name = region_name)
		
		if best_match:
			ids = list(best_match.identifiers.string)
			#print(ids)
			#for i in ids:
				#print(regex.findall(i).groupdict())
			identifier = [i for i in ids if regex.search(i).groupdict(subtype)]
			if len(identifier) == 1:
				identifier = identifier[0]
			else:
				print(best_match.name, '\t', identifier)
			best_match = best_match.name
		else:
			identifier = ""


		#print(identifier, '\t', region_name, '\t', identifier)
		line = {
			'tableRegionName': region_name,
			'bestMatch': best_match,
			'regionCode': identifier
		}
		table.append(line)
	return table


