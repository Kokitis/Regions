class AbstractRegion:
	""" Abstract class that implements the required properties that
		all other Region entities must have. It also implements convienience
		methods for handling and displaying Region Entities. 
	"""
	def getSeries(self, string):
		""" Retrieves a specific series for this region.
			If more than one series is found, raises a ValueError.
			Parameters
			----------
				string: str
					The name or code of a series to retrieve.

			Returns
			-------
				series: Series
		"""

		result = self.series.select(lambda s: s.code == string or s.name == string).first()
		return result

	def show(self, section = 'all'):
		""" Displays information related to the region.

		"""

		print(self.name)
		print("\tParent Region:", self.parentRegion)
		
		if section in {'all', 'identifiers'}:
			self._showIdentifiers(1)

		if section in {'all', 'subregions'}:
			self._showSubRegions(1)

		if section in {'all', 'subjects', 'series'}:
			self._showSeries(1)

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
