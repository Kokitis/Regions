import pony
from ...github import numbertools
from ._emulator_entities import EmulatorRegion, EmulatorSeries


class CompositeRegion(EmulatorRegion):
	""" A region composed of a number of smaller regions.
		Parameters
		----------
		regions: list<Region>, list<Identifier>
			A list of the subregions. 
		report: str
			Composite regions will only encapsulate data from a single report.
		interpolate: {'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'}; default 'linear'}
			Specifies the kind of interpolation as a string 

		Keyword Arguments
		-----------------
		name: str [Required]
			The name of the composite region
		
		Notes
		-----
			Composite Regions are only generated when requested.
		
			
	"""
	@pony.orm.db_session
	def __init__(self, regions, report = None, **kwargs):
		if report is None:
			message = "Must supply a valid report to load!"
			raise ValueError(message)

		#_series = self._parseSeries(regions, report)
		self._loaded_series = dict()
		configuration = {
			'name': kwargs['name'],
			'subRegions': regions,
			'regionType': 'union',
			'parentRegion': None,
			'series': []
		}


		super().__init__(None, **configuration)

	def __str__(self):
		string = "CompositeRegion({})".format(self.name)
		return string

	@pony.orm.db_session
	def _parseSeries(self, regions, report):
		_series = dict()
		for element in regions:
			if element.entity_type == 'identifier':
				region = element.region
			else:
				region = element
			#sprint(report,'\t',region)
			for series in region.series.select(lambda s: s.report.name == report or s.report.code == report):

				key = "{}|{}".format(str(series.report), series.code)
				if key not in _series:
					_series[key] = list()
				_series[key].append(series)
		
		_series = {k: CompositeSeries(s, region = self) for k, s in _series.items()}
		return _series


	def _parseInput(self, regions):
		#regions = [db.getRegion(code) for code in codes]
		_series = self._parseSeries(regions)

		return _series

	@property
	def series(self):
		return list(self._loaded_series.values())

	def _loadSeries(self, key, report):
		_series = CompositeSeries([i.getSeries(key, report) for i in self.subRegions], region = self)
		return _series

	def getSeries(self, key, report = None):
		""" Retrieves a series for the Composite Series
			Parameters
			----------
				key: str [CODE]
					A valid series key
				report: str; default None
					A valid report.
			
			Returns
			-------
				series: CompositeSeries
		"""

		if key not in self._loaded_series:
				self._loaded_series[key, report] = self._loadSeries(key, report)
		#pprint(self._loaded_series)
		return self._loaded_series[key, report]


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
		
		Attributes
		----------
		members: list<Series>
			The series used to create the CompositeSeries.
	"""
	def __init__(self, members, method = '+', bounds = 'nan', **kwargs):
		""" Parameters
			----------
			members: list<series>
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
		self.members = [i for i in members if i]
		template = kwargs.get('template', self.members[0])
		
		#print("Template: ", template)
		#arguments = self._parseAttributes(template, **kwargs)
		#arguments['region'] = kwargs.get('region')

		self._values = self._combineSeries(members, method)
		#pprint(arguments)
		super().__init__(template, self._values, **kwargs)
		self.setInterpolation(bounds)


	@staticmethod
	def _combineSeries(all_series, method):
		all_series = [i for i in all_series if i is not None]

		_min_x = min([min(i.x) for i in all_series])
		_max_x = max([max(i.x) for i in all_series])

		data = list()
		for year in range(_min_x, _max_x + 1):
			series_value = sum(i(year, 'inner') for i in all_series)
			data.append((year, series_value))
		
		#initial_series = EmulatorSeries(all_series[0], data)

		return  data

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
	
	def getComponents(self, method):
		""" Calculates the contribution for each subseries for the given year.
			Returns
			-------
				contributions: list<dict<>>
				* identifiers: list of the region identifiers
				* components: list of tuples -> (year, value, percent)

		"""
		components = list()
		for member in self.members:
			region_identifiers = member.region.identifiers 
			data = list()

			for year, value in self:
				other_value = member(year)
				ratio = other_value / value 
				data.append((year, other_value, value))

			element = {
				'identifiers': region_identifiers,
				'components': data
			}
			components.append(element)
		return components

	@staticmethod
	def emulate(template, values, **kwargs):

		return EmulatorSeries(template, values, **kwargs)

	def toTable(self):
		result = [t for s in self.members for t in s.toTable()]
		return result
