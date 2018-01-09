class AbstractRegion:
	""" Abstract class that implements the required properties that
		all other Region entities must have. It also implements convienience
		methods for handling and displaying Region Entities. 
	"""


	def _showIdentifiers(self, indent = 0):
		indent = "\t" * indent if indent > 0 else ""
		print("{}Available Identifiers [{}]".format(indent, len(self.identifiers)))
		for identifier in self.identifiers:
			print("{0}{0}{1:<10} ({2})".format(
				indent,
				"'{}'".format(identifier.value),
				identifier.namespace.name)
			)

	def _showSeries(self, indent = 0):
		indent = "\t" * indent if indent > 0 else ""
		print("{}Available Series [{}]".format(indent, len(self.series)))
		for i in self.series:
			print("{0}{0}{1}s".format(indent, i))

	def _showSubRegions(self, indent = 0):
		indent = "\t" * indent if indent > 0 else ""
		print("{}Subregions [{}]".format(indent, len(self.subRegions)))
		for s in self.subRegions:
			print("{0}{0}{1}".format(indent, s))

	def getSeries(self, string, report = None):
		""" Retrieves a specific series for this region.
			If more than one series is found, raises a ValueError.
			Parameters
			----------
				string: str
					The name or code of a series to retrieve.
				report: str; default None
					The name or code of a report in the database. If not provided,
					the first series found will be returned.

			Returns
			-------
				series: Series
		"""

		result = self.series.select(lambda s: s.code == string or s.name == string)
		if report:
			result = result.filter(lambda s: s.report.name == report or s.report.code == report)
		result = result.first()
		return result

	@property
	def series(self):
		raise NotImplementedError

	@property
	def name(self):
		raise NotImplementedError

	@property
	def identifiers(self):
		raise NotImplementedError

	@property
	def subRegions(self):
		raise NotImplementedError

	@property
	def parentRegion(self):
		raise NotImplementedError

	def toTable(self):
		return [i.toTable() for i in self.series]

