import math
import datetime
import pandas
from scipy.interpolate import interp1d
from ....github import timetools
from typing import *

Number = Union[int, float]
YearType = Union[int, float, timetools.Timestamp]


def _toScalar(x) -> float:
	""" Tries to convert the input to a float"""
	if not isinstance(x, (int, float)):
		x = timetools.Timestamp(x)
		value = x.toYear()
	else:
		value = x

	return value


class DataSeries:
	""" Sets up common operations on a Series instance. Defines all required properties that
		every subsequent Series entity must implement. 
	"""
	entity_type: str = 'series'

	def __init__(self, data: Dict, israw: bool = True):
		self._verifyData(data)

		multiplier: float = data['seriesScale']['scaleMultiplier']
		values: List[Tuple[YearType, float]] = [(i, j if not israw else j * multiplier) for i, j in
												data['seriesValues']]
		x, y = zip(*values)
		fx: List[float] = [i.toYear() for i in x]
		ix: List[int] = [int(i) for i in fx]

		region_key: str = data['seriesRegion']['entityKey']
		series = pandas.Series(index = x, data = y, name = region_key)

		self.series: pandas.Series = series
		self.data: Dict = data
		self.multiplier: float = multiplier
		self.values = values
		self.x, self.y = x, y
		self.fx: List[float] = fx
		self.ix: List[int] = ix

		self.fvalues: List[Tuple[float, float]] = [(i.toYear(), j) for i, j in self.data['seriesValues']]
		self._interpolation_cache: Optional[Callable] = None

	def __getattr__(self, item):

		return getattr(self.series, item)

	def __str__(self):
		region_name = self.data['seriesRegion']['regionName']

		series_code = self.data['seriesCode']
		min_year = int(min(self.x).toYear())
		max_year = int(max(self.x).toYear())

		string = "Series('{}', [{}, {}], '{}')".format(series_code, min_year, max_year, region_name)
		return string

	def __getitem__(self, item):
		return self.data.get(item)

	@staticmethod
	def _verifyData(data) -> None:
		_region_data = data['seriesRegion']
		_report_data = data['seriesReport']
		# _unit_data = data['seriesUnits']
		# _scale_data = data['seriesScale']

		assert 'regionName' in _region_data
		assert 'regionType' in _region_data

		assert 'reportName' in _report_data

	# Access Methods

	def getInterpolatedValue(self, x: Number, method: str = 'inner', default: Number = math.nan) -> float:

		fx = _toScalar(x)

		_minimum_x = min(self.fx)
		_maximum_x = max(self.fx)

		if self._interpolation_cache is None:

			if len(self.x) == 1:
				self._interpolation_cache = lambda s: self.y[0]
			else:
				self._interpolation_cache = interp1d(
					self.fx,
					self.y,
					bounds_error = False,
					fill_value = (self.y[0], self.y[-1])
				)

		if _minimum_x <= fx <= _maximum_x:
			value = self._interpolation_cache(fx)

		elif (x < _minimum_x or fx > _maximum_x) and method != 'inner':
			value = self._interpolation_cache(fx)
		else:
			value = default

		return value

	# Series Profiling methods.

	def coverage(self) -> pandas.Series:
		"""
			Information on which years have values in the series.
		Returns
		-------
		pandas.Series
		"""
		return self.series.isnull()

	def getCurrentValue(self) -> float:
		current_date = datetime.datetime.now()

		value = self.getValue(current_date, 'interpolate')

		return value

	def getValue(self, x: YearType, method: str = 'interpolate', default: Number = math.nan) -> float:
		""" Returns the `y` value at `x`. Interpolation is supported.
			Parameters
			----------
			x: int, float, datetime.date, Timestamp
				The x-value to use when calculating the y-value

			method: {'interpolate', 'inner', 'exact'}
				* 'interpolate': interpolates and extrapolates over all values of 'x'
				* 'inner': only interpolates the series between min(x) and max(x)
				* 'exact': returns the exact value saved for the given 'x' value.
			default: scalar; default math.nan
				Default value to return if the requested value cannot be found.
		"""

		x_value, value = self.getValueByIndex(x)

		if value is not None and math.isnan(value):
			value = None

		if value or method == 'exact':
			pass
		else:
			value = self.getInterpolatedValue(x, default = default)

		if value is None:
			value = default

		return value

	def getValueByIndex(self, date_value: Union[int, float, timetools.Timestamp]):
		""" Retrieves a single value for the timestamp indicated by 'date_value'"""
		if date_value in self.series.index:
			index = date_value
			value = self.series.get(index)
			point = (date_value, value)
		else:
			if isinstance(date_value, int):
				array = self.ix
			elif isinstance(date_value, float):
				array = self.fx
			else:
				array = self.x

			try:
				index = array.index(date_value)
				value = self.y[index]
				point = (date_value, value)
			except ValueError:
				point = (date_value, None)

		return point

	# Analysis Methods
	def byYear(self, year: YearType, operation: str) -> pandas.Series:
		""" Compares the series to its value in a given year.
			Parameters
			----------
			year: int, float, Timestamp
				A valid year to base all calculations on.
			operation: str; default 'ratio'
				* '-', 'difference': Returns the absolute difference between the base year
					and each other year.
				* '/', 'ratio': Returns the ratio between the base year and the base year.
			Returns
			-------
			pandas.Series


		"""
		base_value = self.getValue(year)

		if operation == '/':
			func = lambda s: s / base_value

		elif operation == '-':
			func = lambda s: s - base_value
		else:
			message = "'{}' is not a valid annual operation type ('ratio', 'difference')"
			raise KeyError(message)

		result = self.apply(func)
		return result

	def timeChange(self, kind: str) -> pandas.Series:
		""" Calculates year-on-year changes in the series
			Parameters
			----------
				kind: {'doublingTime', 'doublingYear', 'yearlyGrowth', 'yearlyChange'}; default 'yearlyGrowth'
					'yearlyGrowth': The percent change from year-to-year
					'yearlyChange': The absolute change between years
					'doublingTime': The total time for the series to double in value
					'doublingYear': The year the series will double in value
					'cumulative': The cumulative value, with year 0 being the earliest value.
			Returns
			----------
			pandas.Series
		"""

		if kind == '%' or kind == 'yearlyGrowth':
			result = self.series.pct_change(fill_method = None)
		elif kind == '-' or kind == 'yearlyChange':
			result = self.series.diff()
		elif kind == 'doublingTime':
			ratio = self.series.pct_change(fill_method = None)
			result = math.log(2) / ratio
		elif kind == 'doublingYear':
			ratio = self.series.pct_change(fill_method = None)
			doubling_time = math.log(2) / ratio
			result = [(i.year, i.year + doubling_time) for i in self.series.index]
		elif kind == 'cumulative':
			result = self.series.cumsum()
		else:
			message = "Invalid operation: '{}' ({})".format(
				kind,
				", ".join({'doublingTime', 'doublingYear', 'yearlyGrowth', 'yearlyChange, cumulative'})
			)
			raise ValueError(message)

		return result

	# Export Methods

	def toSql(self):
		raise NotImplementedError

	def toDict(self):
		return self.data

	@property
	def region(self):
		return self.data['seriesRegion']
