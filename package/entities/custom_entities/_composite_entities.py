from ._emulator_entities import EmulatorRegion, EmulatorSeries
from ...github import numbertools


class CompositeRegion(EmulatorRegion):
	""" A region composed of a number of smaller regions.
		Parameters
		----------
		regions: list<Region>
			A list of the subregions. 
		interpolate: {'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'}; default 'linear'}
			Specifies the kind of interpolation as a string 

		Keyword Arguments
		-----------------
		name: str [Required]
			The name of the composite region
		
			
	"""
	def __init__(self, regions, **kwargs):

		_series = self._parseSeries(regions)

		configuration = {
			'name': kwargs['name'],
			'subRegions': regions,
			'regionType': 'union',
			'parentRegion': None,
			'series': _series
		}
		super().__init__(None, **configuration)

	def __str__(self):
		string = "CompositeRegion({})".format(self.name)
		return string

	@staticmethod
	def _parseSeries(regions):
		_series = dict()
		for region in regions:
			for series in region.series:
				key = "{}|{}".format(str(series.report), series.code)
				if key not in _series:
					_series[key] = list()
				_series[key].append(series)
		
		_series = {k: CompositeSeries(s) for k, s in _series.items()}
		return _series


	def _parseInput(self, regions):
		#regions = [db.getRegion(code) for code in codes]
		_series = self._parseSeries(regions)

		return _series

	@property
	def series(self):
		return list(self._series.values())

	def getSeries(self, key):
		""" Retrieves a series for the Composite Series
			Parameters
			----------
				key: str [CODE]
					A valid series code. 
			
			Returns
			-------
				series: CompositeSeries
		"""

		for element, s in self._series.items():
			_, c = element.split('|')
			if c == key:
				return s


class CompositeSeries(EmulatorSeries):
	""" Combines several different series into a single entity for use with compound Regions.
		The first series in the list will be used as a template.
		Parameters
		----------
		series_list: list<Series>
			All the series objects to combine.
		method: {}; default 'add'
			The method by which to combine each Series
		Keyword Arguments
		-----------------
		Any valid series arguments. Will overwrite values taken from 'template'
		template: Series
			A template series to use. Defaults to the first element of the passed list.
	"""
	def __init__(self, series_list, method = 'add', bounds = 'nan', **kwargs):
		""" Parameters
			----------
			series_list: list<series>
				The full list of **Series** objects to combine.
			method: {'add'}; default 'add'
				The method to use when combineing the series.
			missing: {'nan', 'zero', 'fill'}; default 'nan'
			* 'nan': If a series is missing a `y` value for a given `x`, 
				that value will not be calculated for the composite series.
			* 'zero': Missing values will be counted as zeros when calculating
				the resulting **CompositeSeries**.
			* 'fill': Values will be interpolated from the closest values. 
			bounds: Same as `missing`
		"""
		template = kwargs.get('template', series_list[0])

		arguments = self._parseCompositeArguments(template, **kwargs)

		self._original, self._values = self._combineSeries(series_list, method)

		super().__init__(template, self._values, **arguments)
		self.setInterpolation(bounds)

	def _parseCompositeArguments(self, template, **kwargs):

		args = self._parseAttributes(template)
		args.pop('region')

		args = {**args, **kwargs}
		return args

	@staticmethod
	def _combineSeries(all_series, method):
		for s in all_series:
			s.setInterpolation(None)
		initial_series = EmulatorSeries(all_series[0])
		other_series = all_series[1:]
		original_series = [(i.region.name, i) for i in all_series]

		for other in other_series:
			initial_series = initial_series.compare(other, method)
		

		return original_series, initial_series

	def components(self, year):
		total = self(year)
		members = [(name, series(year)) for name, series in self._original]

		_base = numbertools.humanReadable([i[1] for i in members], to_string = False)
		_base = _base[0][1] 

		members = sorted(members, key = lambda s: s[1], reverse = True)
		
		print(
			"{:>10}\t100.0%\t{} {}".format(
				numbertools.humanReadable(total, base = _base), 
				"in the year", 
				year
			)
		)
		for member in members:
			name, value = member 
			ratio = value / total
			readable_value = numbertools.humanReadable(value, base = _base)
			print("{:>10}\t{:>6.2%}\t{}".format(readable_value, ratio, name)) 
	@staticmethod
	def emulate(template, values, **kwargs):

		return EmulatorSeries(template, values, **kwargs)

def toTable(self):
	result = [t for s in self._original for t in s.toTable()]
	return result
