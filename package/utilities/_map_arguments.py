class MapArguments:
	def __init__(self):
		self.entity_argument_map = {
			'agency':     {
				'code':    ['agencyCode'],
				'name':    ['agencyName'],
				'url':     ['agencyUrl'],
				'address': ['agencyAddress']
			},
			'identifier': {
				'string':    ['identifierString'],
				'namespace': ['identifierNamespace'],
				'region':    ['identifierRegion']
			},
			'namespace':  {
				'code':  ['namespaceCode'],
				'name':  ['namespaceName'],
				'regex': ['namespaceRegex'],
				'url':   ['namespaceUrl']
			},
			'region':     {
				'name':           ['regionName'],
				'code':           ['regionCode'],
				'classification': ['regionClassification', 'regionType'],
				'parent':         ['parentRegion'],
				'subregions':     ['children']
			},
			'report':     {
				'name':       ['reportName'],
				'code':       ['reportCode'],
				'url':        ['reportUrl'],
				'namespace':  ['reportNamespace'],
				'agency':     ['reportAgency'],
				'reportDate': ['reportDate']
			},
			'series':     {
				'code':        ['seriesCode'],
				'name':        ['seriesName'],
				'report':      ['seriesReport'],
				'region':      ['seriesRegion'],
				'notes':       ['seriesNotes'],
				'description': ['seriesDescription'],
				'units':       ['seriesUnits'],
				'scale':       ['seriesScale'],
				'strvalues':   ['seriesValues', 'seriesStrvalues', 'values'],
				'tags':        ['seriesTags']
			},
			'unit':       {
				'string': ['unitString'],
				'code':   ['unitCode']
			},
			'scale':      {
				'string':     ['scaleString'],
				'multiplier': ['scaleMultiplier']
			}

		}


