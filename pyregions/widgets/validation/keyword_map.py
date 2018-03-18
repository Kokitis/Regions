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
	return {k: v for k, v in values.items() if v is not None and str(v) != 'nan'}


def entityKeywordMap(entity_type, entity_args = None, **kwargs):
	"""
		Parameters
		----------
			entity_type: {'agency', 'identifier', 'namespace', 'observation', 'region', 'report', 'series'}
			entity_args: dict<str:scalar>

	"""
	# print("Before parsing:")
	# for k, v in sorted(entity_args.items()):
	#	print("\t{}:\t{}".format(k, v))
	if entity_args is None:
		result = kwargs
	else:
		result = entity_args

	entity_type = entity_type.lower()

	if entity_type == 'agency':
		args = {
			'code':    parseKeywords(result, ['agencyCode', 'code']),
			'name':    parseKeywords(result, ['agencyName', 'name']),
			'url':     parseKeywords(result, ['agencyUrl', 'url']),
			'wiki':    parseKeywords(result, ['agencyWiki', 'wiki']),
			'address': parseKeywords(result, ['agencyAddress', 'address'])
		}
	elif entity_type == 'attribute':
		args = {
			'region':   parseKeywords(result, ['region']),  # , getRegion),
			'variable': parseKeywords(result, ['variable', 'attribute', 'key', 'subject'], str),
			'value':    parseKeywords(result, ['value'], str),
			'source':   parseKeywords(result, ['source', 'url', 'wiki', 'link'], str)
		}
	elif entity_type == 'identifier':
		args = {
			'string':    parseKeywords(result,
									   ['identifierCode', 'code', 'regionCode', 'identifier', 'string', 'value']),
			'namespace': parseKeywords(result, ['namespace', 'identifierNamespace']),  # , getNamespace),
			'subtype':   parseKeywords(result, ['identifierSubtype', 'subtype', 'type']),
			'region':    parseKeywords(result, ['region'])  # s, getRegion)
		}
	elif entity_type == 'namespace':
		args = {
			'code':     parseKeywords(result, ['namespaceCode', 'code']),
			'name':     parseKeywords(result, ['name']),
			'subtypes': parseKeywords(result, ['subtypes']),
			'regex':    parseKeywords(result, ['regex', 'format']),
			'url':      parseKeywords(result, ['namespaceUrl', 'url']),
			'wiki':     parseKeywords(result, ['namespaceWiki'])
		}
	elif entity_type == 'observation':
		args = {
			'x':      parseKeywords(result, ['x', 'year']),
			'y':      parseKeywords(result, ['y', 'value']),
			'series': parseKeywords(result, ['series'])
		}

	elif entity_type == 'region':
		args = {
			'type':   parseKeywords(result, ['regionType', 'type', 'kind', 'subtype', 'subType']),
			'name':   parseKeywords(result, ['regionName', 'countryName', 'state', 'name', 'city', 'cityName']),
			'parent': parseKeywords(result, ['parentRegion', 'parent']),  # , getRegion)
			'code':   parseKeywords(result, ['code', 'standardCode', 'regionCode'])
		}

	elif entity_type == 'report':
		args = {
			'name':      parseKeywords(result, ['reportName', 'name'], str),
			'code':      parseKeywords(result, ['reportCode', 'code']),
			'url':       parseKeywords(result, ['reportUrl', 'url', 'link', 'reportWebsite'], str),
			'namespace': parseKeywords(result, ['reportNamespace', 'namespace']),  # , getNamespace),
			'agency':    parseKeywords(result, ['reportAgency', 'agency']),  # , getAgency),
			'date':      parseKeywords(result, ['publishDate', 'date', 'reportDate'], str)
		}

	elif entity_type == 'series':
		args = {
			'code':        parseKeywords(result, ['seriesCode', 'subjectCode', 'code']),
			'region':      parseKeywords(result, ['region', 'seriesRegion']),  # , getRegion),
			'report':      parseKeywords(result, ['report', 'seriesReport']),  # , getReport),
			'name':        parseKeywords(result, ['seriesName', 'subjectName', 'name']),
			'notes':       parseKeywords(result, ['subjectNotes', 'seriesNotes', 'notes']),
			'units':       parseKeywords(result, ['unit', 'units', 'Units', 'subjectUnits', 'seriesUnits']),
			'scale':       parseKeywords(result, ['scale', 'Scale', 'seriesScale', 'subjectScale']),
			# 'strvalues': parseKeywords(result, ['strvalues']),
			'strvalues':   parseKeywords(result, ['values', 'seriesValues', 'strvalues']),
			'tags':        parseKeywords(result, ['tags', 'attributes']),
			'description': parseKeywords(result, ['seriesDescription', 'description', 'subjectDescription'])
		}
	elif entity_type == 'unit':
		args = {
			'code':   parseKeywords(result, ['code', 'unitCode']),
			'string': parseKeywords(result, [
				'units', 'unit', 'seriesUnits', 'subjectUnits', 'seriesUnit', 'subjectUnit', 'name', 'string',
				'unitString'
			]
									)
		}
	elif entity_type == 'scale':
		args = {
			'string':     parseKeywords(result, ['seriesScale', 'scale', 'string', 'value', 'scaleString']),
			'multiplier': parseKeywords(result, ['seriesMultiplier', 'multiplier', 'scaleMultiplier'])
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
