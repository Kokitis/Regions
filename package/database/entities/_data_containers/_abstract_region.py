from typing import List, Dict, Any
class DataRegion:
	""" Abstract class that implements the required properties that
		all other Region entities must have. It also implements convienience
		methods for handling and displaying Region Entities.
		Input Keys:
		* 'entityType':        'region',
		* 'entityKey':         self.key,
		* 'regionType':        self.regionType,
		* 'regionName':        self.name,

		# Relations

		* 'regionIdentifiers': region_identifiers,
		* 'regionParent':      parent_region,
		* 'regionSubregions':  subregions,
		* 'regionSeries':      region_series,
		* 'regionTags':        list()
	"""
	def __init__(self, data):
		self.data = data

	def __getitem__(self, item):
		return self.data.get(item)

	def _showIdentifiers(self, indent:int = 0)->None:
		indent = "\t" * indent if indent > 0 else ""
		print("{}Available Identifiers [{}]".format(indent, len(self.identifiers)))

		for identifier in self.identifiers:
			print("{0}{0}{1:<10} ({2})".format(
				indent,
				"'{}'".format(identifier.value),
				identifier.namespace.name)
			)

	def _showSeries(self, indent:int = 0)->None:
		indent = "\t" * indent if indent > 0 else ""
		print("{}Available Series [{}]".format(indent, len(self.series)))
		for i in self.series:
			print("{0}{0}{1}s".format(indent, i))

	def _showSubRegions(self, indent:int = 0)->None:
		indent = "\t" * indent if indent > 0 else ""
		print("{}Subregions [{}]".format(indent, len(self.subRegions)))
		for s in self.subRegions:
			print("{0}{0}{1}".format(indent, s))


	def toTable(self)->List[Dict[str,Any]]:
		return [i.toTable() for i in self.series]

	# Properties

	@property
	def identifiers(self)->List[str]:
		return self.data['identifiers']

	@property
	def subRegions(self):
		return self.data['regionSubregions']

	@property
	def series(self):
		return self.data['regionSeries']

