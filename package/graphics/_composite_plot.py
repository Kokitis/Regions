import matplotlib.pyplot as plt

class ValuePlot:
	""" Generates a catagorical heatmap for a specific subject that highlights which subregions have values for each year."""
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

class CompositePlot:
	def __init__(self, composite_region, subject_code, **kwargs):
		self.setupPlot(**kwargs)
		composite_series = composite_region.getSeries(subject_code)
		self.addSeries(composite_series, **kwargs)
	
	def setupPlot(self, **kwargs):
		figsize = kwargs.get('figsize', (20, 10))

		self.fig, self.ax = plt.subplots(figsize = figsize)

	def addSeries(self, composite_series, **kwargs):
		pass

		

