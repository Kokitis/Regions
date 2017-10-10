
from pony.orm import db_session

from ...utilities import getDefinition
from ...github import tabletools


@db_session
def importNutsNamespace(dataset): 
	table = tabletools.Table(
		getDefinition('namespace', 'NUTS'),
		sheetname = "NUTS2013-NUTS2016", 
		skiprows = 1
	)
	
	namespace = getDefinition('namespace', 'NUTS')
	namespace = dataset.insertEntity('namespace', **namespace)

	current_regions = dict()

	for index, row in enumerate(table):

		nuts_code = row['Code 2016']
		if isinstance(nuts_code, float): 
			continue # The NUTS code was missing.
		nuts_level = len(nuts_code) - 2

		if nuts_level == 0:
			region_name = row['Country']
		elif nuts_level == 1:
			region_name = row['NUTS level 1']
		elif nuts_level == 2:
			region_name = row['NUTS level 2']
		elif nuts_level == 3:
			region_name = row['NUTS level 3']
		else:
			message = "Code '{}' with length '{}' is not a valid NUTS identifier.".format(nuts_code, nuts_level)
			raise ValueError(message)
		
		if region_name.lower().startswith('extra-regio'):
			region_name = "{} ({})".format(region_name, nuts_code)

		region_config = {
			'name': region_name,
			'regionType': "NUTS{}".format(nuts_level) if nuts_level != 0 else 'country'
		}

		if nuts_level > 0:
			region_config['parentRegion'] = current_regions[nuts_level - 1]
		
		region = dataset.Region.get(name = region_name)
		if region is None:
			region = dataset.insertEntity('region', **region_config)
		
		identifier_config = {
			'namespace': namespace,
			'region': region,
			'string': nuts_code
		}
		
		dataset.insertEntity('identifier', **identifier_config)
		current_regions[nuts_level] = region
	return namespace
