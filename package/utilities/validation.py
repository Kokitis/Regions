import math

def debugEntity(label, entity):
	""" Convientience method to display the arguments
		used in a failed attempt to create a new entity 
	"""
	print("Entity: {}".format(label))
	print("\tType: ", type(entity))
	if isinstance(entity, dict):
		for k, v in sorted(entity.items()):
			print("\t{}:\t{}".format(k, v))
	else:
		print("\t", entity)

def isNull(value):
	""" Checks if a value should be considered null.
		Returns True if the value is None or has a value of nan 
	"""
	is_null = value is None
	if not is_null and isinstance(value, float):
		is_null = math.isnan(value)
	return is_null

def isNumber(value):
	""" Checks if a value is a numeric type or if all characters in the string are digits.
		Parameters
		----------
			value: int, float, str
	"""
	is_numeric_type = isinstance(value, (int, float))
	is_all_digit = is_numeric_type or (isinstance(value, str) and value.isdigit())
	return is_all_digit

def parseKeywords(columns, keys, cls = None, return_type = 'values'):
	"""
		Parameters
		----------
			columns: list<str>
				A list of the columns in the table.
			keys: list<str>
				A list of the possible column names that hold the
				desired information.
				Ex. 'country', 'regionName', 'countryName' to 
				extract the column with the region's name
			return_type: {'columns', 'values'}; default 'values'
				* 'columns': returns the column in the table that was found.
				* 'values': returns the value contained in the column that was found.
			cls: class(obj); default None
				A function or class to convert the resulting values to.
	"""

	if hasattr(columns, 'keys'):
		data = columns
		columns = data.keys()
	elif hasattr(columns, 'columns'):
		data = columns
		columns = data.columns
	else:
		# Assume a list of str
		data = dict()
		return_type = 'columns'

	candidates = [col for col in columns if col in keys]
	if len(candidates) == 0:
		value = None
	elif return_type == 'columns':
		value = candidates[0]
	elif return_type == 'values':
		value = candidates[0]
		value = data[value]
	else:
		message = "Invalid return type: '{}'".format(return_type)
		raise ValueError(message)
	if cls:
		try:
			value = cls(value)
		except ValueError:
			value = None

	return value


def _removeMissingVars(values):
	return {k:v for k,v in values.items() if v is not None and str(v) != 'nan'}


def parseEntityArguments(entity_type, entity_args = None, **kwargs):
	"""
		Parameters
		----------
			entity_type: {'agency', 'identifier', 'namespace', 'observation', 'region', 'report', 'series'}
			entity_args: dict<str:scalar>

	"""
	#print("Before parsing:")
	#for k, v in sorted(entity_args.items()):
	#	print("\t{}:\t{}".format(k, v))
	if entity_args is None:
		result = kwargs
	else:
		result = entity_args

	if not isinstance(entity_type, str):
		entity_type = entity_type.entity_type
	entity_type = entity_type.lower()
	

	if entity_type == 'agency':
		args = {
			'code': 	parseKeywords(result, ['agencyCode', 'code']),
			'name': 	parseKeywords(result, ['agencyName', 'name']),
			'url': 		parseKeywords(result, ['agencyUrl', 'url']),
			'wiki': 	parseKeywords(result, ['agencyWiki', 'wiki']),
			'address': parseKeywords(result,  ['agencyAddress', 'address'])
		}
	elif entity_type == 'attribute':
		args = {
			'region': 	parseKeywords(result, ['region']),#, getRegion),
			'variable': parseKeywords(result, ['variable', 'attribute', 'key', 'subject'], str),
			'value': 	parseKeywords(result, ['value'], str),
			'source': 	parseKeywords(result, ['source', 'url', 'wiki', 'link'], str)
		}
	elif entity_type == 'identifier':
		args = {
			'string': 		parseKeywords(result, ['identifierCode', 'code', 'regionCode', 'identifier', 'string', 'value']),
			'namespace': 	parseKeywords(result, ['namespace', 'identifierNamespace']),#, getNamespace),
			'subtype': 		parseKeywords(result, ['identifierSubtype', 'subtype', 'type']),
			'region':  		parseKeywords(result, ['region'])#s, getRegion)
		}
	elif entity_type == 'namespace':
		args = {
			'code': 	parseKeywords(result, ['namespaceCode', 'code']),
			'name': 	parseKeywords(result, ['name']),
			'subtypes': parseKeywords(result, ['subtypes']),
			'regex': 	parseKeywords(result, ['regex', 'format']),
			'url': 		parseKeywords(result, ['namespaceUrl', 'url']),
			'wiki': 	parseKeywords(result, ['namespaceWiki'])
		}
	elif entity_type == 'observation':
		args = {
			'x': 		parseKeywords(result, ['x', 'year']),
			'y': 		parseKeywords(result, ['y', 'value']),
			'series': 	parseKeywords(result, ['series'])
		}	

	elif entity_type == 'region':
		args = {
			#'code': 		parseKeywords(['regionCode', 'code', 'isoCode'], result),
			'regionType': 	parseKeywords(result, ['regionType', 'type', 'kind', 'subtype', 'subType']),
			'name': 		parseKeywords(result, ['regionName', 'countryName', 'state', 'name', 'city', 'cityName']),
			'parentRegion': parseKeywords(result, ['parentRegion', 'parent'])#, getRegion)
		}

	elif entity_type == 'report':
		args = {
			'name': 		parseKeywords(result, ['reportName', 'name'], str),
			'code': 		parseKeywords(result, ['reportCode', 'code']),
			'url': 			parseKeywords(result, ['reportUrl', 'url', 'link'], str),
			'namespace': 	parseKeywords(result, ['reportNamespace', 'namespace']),#, getNamespace),
			'agency': 		parseKeywords(result, ['reportAgency', 'agency']),#, getAgency),
			'publishDate': 	parseKeywords(result, ['publishDate', 'date'], str)
		}

	elif entity_type == 'series':
		args = {
			'code':   parseKeywords(result, ['seriesCode', 'subjectCode', 'code']),
			'region': parseKeywords(result, ['region']),#, getRegion),
			'regionCode': parseKeywords(result, ['regionCode']),
			'report': parseKeywords(result, ['report', 'seriesReport']),#, getReport),
			'name':   parseKeywords(result, ['seriesName', 'subjectName', 'name']),
			'notes': parseKeywords(result,  ['subjectNotes', 'seriesNotes', 'notes']),
			'unit': parseKeywords( result,   ['unit', 'units', 'Units', 'subjectUnits', 'seriesUnits']),
			'scale': parseKeywords(result,  ['scale', 'Scale', 'seriesScale', 'subjectScale']),
			'strvalues': parseKeywords(result, ['strvalues']),
			'values': parseKeywords(result, ['values', 'seriesValues']),
			'tags': parseKeywords(result, ['tags', 'attributes']),
			'description': parseKeywords(result, ['seriesDescription', 'description', 'subjectDescription'])
		}
	elif entity_type == 'unit':
		args = {
			'code': parseKeywords(result, ['code', 'unitCode']),
			'string': parseKeywords(result, [
				'units', 'unit', 'seriesUnits', 'subjectUnits', 'seriesUnit', 'subjectUnit', 'name', 'string', 'unitString'
				]
			)
		}
	elif entity_type == 'scale':
		args ={
			'string': parseKeywords(result, ['seriesScale', 'scale', 'string', 'value']),
			'multiplier': parseKeywords(result, ['seriesMultiplier', 'multiplier'])
		}
	elif entity_type == 'tag':
		args = {
			'string': parseKeywords(result, ['string', 'tag', 'seriesTags', 'tags'])
		}
	else:
		message = "ParseEntityArguments: The requested entity type ('{}') does not exist!".format(entity_type)
		raise ValueError(message)

	args = _removeMissingVars(args)
	return args


def validateEntity(entity_type, **data):
	""" Validates that an entity is properly defined.
		Used to ensure the data can be used to create a new instance
		of an entity.
		Parameters
		----------
			entity_type: str
			data: dict
	"""
	
	# Agency
	entity_name 	= data.get('name')
	entity_code 	= data.get('code')
	entity_url  	= data.get('url')
	entity_address 	= data.get('address')

	# Identifier
	entity_namespace = data.get('namespace')
	entity_string = data.get('string')
	entity_region = data.get('region')

	# Namespace
	entity_regex 	= data.get('regex')

	# Observation
	entity_x 		= data.get('x')
	entity_y 		= data.get('y')

	# Region
	entity_region_type = data.get('regionType')

	# Report
	entity_publish_date = data.get('publishDate')
	entity_retrieved_date=data.get('retrievedDate')
	entity_agency = data.get('agency')

	# Series
	entity_report = data.get('report')
	entity_notes = data.get('notes')
	entity_units = data.get('units')
	entity_scale = data.get('scale')
	entity_description = data.get('description')

	entity_multiplier = data.get('multiplier')


	if entity_type == 'agency':
		entity_code_is_valid = isinstance(entity_code, str)
		entity_name_is_valid = isinstance(entity_name, str)
		entity_url_is_valid = not entity_url or isinstance(entity_url, str)
		entity_address_is_valid = not entity_address or isinstance(entity_address, str)
		_entity_validation_test = {
			'agencyCode': (entity_code, entity_code_is_valid),
			'agencyName': (entity_name, entity_name_is_valid),
			'agencyUrl': (entity_url, entity_url_is_valid),
			'agencyAddress': (entity_address, entity_address_is_valid)
		}

	elif entity_type == 'identifier':
		entity_string_is_valid = isinstance(entity_string, str)
		#entity_value_is_valid = isinstance(entity_value, str)
		entity_namespace_is_valid = entity_namespace and entity_namespace.entity_type == 'namespace'
		entity_region_is_valid = entity_region and entity_region.entity_type == 'region'
		#_is_valid = entity_value_is_valid and entity_namespace_is_valid and entity_region_is_valid
		_entity_validation_test = {
			'identifierValue': (entity_string, entity_string_is_valid),
			'identifierNamespace': (entity_namespace, entity_namespace_is_valid),
			'identifierRegion': (entity_region, entity_region_is_valid)
		}
	
	elif entity_type == 'namespace':
		entity_name_is_valid = isinstance(entity_name, str)
		entity_code_is_valid = isinstance(entity_code, str)
		entity_url_is_valid = not entity_url or isinstance(entity_url, str)
		entity_regex_is_valid = not entity_regex or isinstance(entity_regex, str)
		#_is_valid = entity_name_is_valid and entity_code_is_valid and entity_url_is_valid and entity_regex_is_valid
		_entity_validation_test = {
			'namespaceName': (entity_name, entity_name_is_valid),
			'namespaceCode': (entity_code, entity_code_is_valid),
			'namespaceUrl': (entity_url, entity_url_is_valid),
			'namespaceRegex': (entity_regex, entity_regex_is_valid)
		}
	
	elif entity_type == 'region':
		entity_name_is_valid = isinstance(entity_name, str)
		entity_region_type_is_valid = isinstance(entity_region_type, str)

		_entity_validation_test = {
			'regionName': (entity_name, entity_name_is_valid),
			'regionType': (entity_region_type, entity_region_type_is_valid)
		}

	elif entity_type == 'report':
		entity_name_is_valid = isinstance(entity_name, str)
		entity_url_is_valid = isinstance(entity_url, str)
		entity_publish_date_is_valid = isinstance(entity_publish_date, str)
		entity_retrieved_date_is_valid = not entity_retrieved_date or isinstance(entity_retrieved_date, str)
		entity_agency_is_valid = entity_agency and entity_agency.entity_type == 'report'

		#_is_valid = entity_name_is_valid and entity_url_is_valid and entity_publish_date_is_valid and entity_retrieved_date_is_valid and entity_agency_is_valid
		_entity_validation_test = {
			'reportName': (entity_name, entity_name_is_valid),
			'reportUrl': (entity_url, entity_url_is_valid),
			'reportPublishDate': (entity_publish_date, entity_publish_date_is_valid),
			'reportRetrievedDate': (entity_retrieved_date, entity_retrieved_date_is_valid),
			'reportAgency': (entity_agency, entity_agency_is_valid)
		}

	elif entity_type == 'series':
		entity_region_is_valid = entity_region and entity_region.entity_type == 'region'
		entity_report_is_valid = entity_report and entity_report.entity_type == 'report'
		entity_name_is_valid = isinstance(entity_name, str)
		entity_code_is_valid = isinstance(entity_code, str)
		entity_description_is_valid = not entity_description or isinstance(entity_description, str)
		entity_notes_is_valid = not entity_notes or isinstance(entity_notes, str)
		entity_units_is_valid = not entity_units or entity_units.entity_type == 'units'
		entity_scale_is_valid = not entity_scale or entity_scale.entity_type == 'scale'

		#_is_valid = entity_region_is_valid and entity_report_is_valid and entity_name_is_valid and entity_code_is_valid
		#_is_valid = _is_valid and entity_description_is_valid and entity_notes_is_valid and entity_units_is_valid and entity_scale_is_valid

		_entity_validation_test = {
			'seriesRegion': (entity_region, entity_region_is_valid),
			'seriesReport': (entity_report, entity_report_is_valid),
			'seriesName': (entity_name, entity_name_is_valid),
			'seriesCode': (entity_code, entity_code_is_valid),
			'seriesDescription': (entity_description, entity_description_is_valid),
			'seriesNotes': (entity_notes, entity_notes_is_valid),
			'seriesUnits': (entity_units, entity_units_is_valid),
			'seriesScale': (entity_scale, entity_scale_is_valid)
		}

	elif entity_type == 'observation':
		entity_x_is_valid = isinstance(entity_x, int)
		entity_y_is_valid = isinstance(entity_y, float)

		#_is_valid = entity_x_is_valid and entity_y_is_valid
		_entity_validation_test = {
			'observationX': (entity_x, entity_x_is_valid),
			'observationY': (entity_y, entity_y_is_valid)
		}
	elif entity_type == 'scale':
		entity_string_is_valid = isinstance(entity_string, str)
		entity_multiplier_is_valid = entity_multiplier is None or isinstance(entity_multiplier, float)
		_entity_validation_test = {
			'scaleString': (entity_string, entity_string_is_valid),
			'scaleMultiplier': (entity_multiplier, entity_multiplier_is_valid)
		}
	elif entity_type == 'unit':
		entity_name_is_valid = isinstance(entity_name, str)
		entity_code_is_valid = isinstance(entity_code, str)
		_entity_validation_test = {
			'unitName': (entity_name, entity_name_is_valid),
			'unitCode': (entity_code, entity_code_is_valid)
		}
	else:
		message = "Could not validate '{}'".format(entity_type)
		raise TypeError(message)

	_is_valid = all(_entity_validation_test.values())

	if not _is_valid:
		print("Entity Type: ", entity_type)
		for k, v in sorted(_entity_validation_test.items()):
			print("\t{}\t{}".format(k, v))
		raise ValueError

