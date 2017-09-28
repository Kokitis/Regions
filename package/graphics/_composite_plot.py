""" Generates a catagorical heatmap for a specif subject that highlights which subregions have values for each year."""

class CompositePlot:
	def __init__(self, series_map):
		series_list = self._convertSeries(series_map)
		for i in series_list:
			self._convertSeries(i)
	@staticmethod
	def _convertSeries(series_map):
		""" """
		series_list = list()
		for i in series_map:
			series_list += i.toTable()
		
		return series_list



	