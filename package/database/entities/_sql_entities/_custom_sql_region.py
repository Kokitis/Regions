

class CustomSqlRegion:
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
	def report(self):
		raise NotImplementedError


