import math
import datetime

from pony.orm import db_session
from scipy.interpolate import interp1d


class AbstractSeries:
	""" Sets up common operations on a Series instance. Defines all required properties that
		every subsequent Series entity must implement. 
	"""
	entity_type = 'series'


	# @db_session
	def __iter__(self):
		for i in self.values:
			yield i

	def __str__(self):
		region_name = self.region.name

		series_code = self.code

		string = "Series('{}', {}-{}, '{}')".format(series_code, min(self.x), max(self.x), region_name)
		return string



	@staticmethod
	def _applyOperation(left, right, operation):
		# Basic operations
		if operation == '+':
			new_y = left + right
		elif operation == '-':
			new_y = left - right
		elif operation == '*':
			new_y = left * right
		elif operation == '/':
			new_y = left / right

		# Comparison operations
		elif operation == '==':
			new_y = left == right
		elif operation == '>=':
			new_y = left >= right
		elif operation == '>':
			new_y = left > right
		elif operation == '<':
			new_y = left < right
		elif operation == '<=':
			new_y = left <= right
		elif operation == '!=':
			new_y = left != right

		# Other operations
		elif operation == '%':
			# Relative change
			new_y = (right - left) / left

		else:
			message = "Invalid operation: '{}'".format(operation)
			raise ValueError(message)

		return new_y



	def applyScalarOperation(self, other, operation):
		"""
			Applies a scalar operation to the Series. Used when 'other' is a single value rather than a series.
		Parameters
		----------
		other
		operation

		Returns
		-------

		"""

		new_values = list()
		for x, y in self.values:
			# Algebraic operators
			new_y = self._applyOperation(y, other, operation)
			new_values.append((x, new_y))

		new_series = self.emulate(self, new_values)
		return new_series

	def applySeriesOperation(self, other, operation):
		domain = set(self.x) | set(other.x)

		values = list()

		for year in sorted(domain):
			left = self.getValue(year)
			right = other.getValue(year)
			result = self._applyOperation(left, right, operation)
			values.append((year, result))

		new_series = self.emulate(self, values)

		return new_series


	@classmethod
	def emulate(cls, template, values, **kwargs):
		raise NotImplementedError

	@db_session
	def _splitStringValues(self):
		numeric_values = [
			(int(i[0]), float(i[1]))
			for i in [
				point.split('|') for point in self.strvalues.split('||')
			]
		]
		return numeric_values

	def describe(self):

		lines = [
			('Region Name', self.region.name),
			('Report Name', self.report.name),
			('Series Code', "'{}'".format(self.code)),
			('Series Name', self.name),
			('Series Units', self.unit),
			('Series Scale', self.scale)
		]
		lines = "\n".join(["{}:\t{}".format(i, j) for i, j in lines])
		_max_width = 100
		# [your_string[i:i+n] for i in range(0, len(your_string), n)]

		description = ['\t' + self.notes[i:i + _max_width] for i in range(0, len(self.notes), _max_width)]
		description = "\n".join(["Notes:"] + description)

		string = lines + '\n' + description
		print(string)

	# Export Methods

	def export(self):
		result = {
			'code':       self.code,
			'name':       self.name,
			'report':     self.report.name,
			'regionCode': self.region.code,
			'regionName': self.region.name,
			'values':     list(self.values),
			'scale':      self.scale,
			'units':      self.unit,
			'notes':      self.notes
		}
		return result

	def toSql(self):
		pass
	def toDict(self):
		pass
	# Access Methods

	def getInterpolatedValue(self, x):
		if not hasattr(self, '_interpolation_cache'):
			bounds = (self.y[0], self.y[-1])
			if len(self.x) == 1:
				self._interpolation_cache = lambda s: self.y[0]
			else:
				self._interpolation_cache = interp1d(
					self.x,
					self.y,
					bounds_error = False,
					fill_value = bounds
				)

		value = self._interpolation_cache(x)

		return value

	def getValue(self, x, method = 'interpolate', absolute = True, default = math.nan):
		""" Returns the `y` value at `x`. Interpolation is supported.
			Parameters
			----------
			x: int
				The x-value to use when calculating the y-value
			absolute: bool; default True
				If True, the returned y-value will be automatically scaled according
				to the series.scale value.
			method: {'interpolate', 'inner', 'exact'}
				* 'interpolate': interpolates and extrapolates over all values of 'x'
				* 'inner': only interpolates the series between min(x) and max(x)
				* 'exact': returns the exact value saved for the given 'x' value.
			default: scalar; default math.nan
				Default value to return if the requested value cannot be found.
		"""

		_minimum_x = min(self.x)
		_maximum_x = max(self.x)

		if method == 'exact':
			if x in self.x:
				value = [i for i in self.values if i[0] == x][0]
			else:
				value = default
		elif _minimum_x <= x <= _maximum_x:
			value = self.getInterpolatedValue(x)
		elif x < _minimum_x or x > _maximum_x:
			if method == 'interpolate':
				value = self.getInterpolatedValue(x)
			else:
				value = default
		else:
			raise NotImplementedError

		if absolute:
			value *= self.multiplier

		return value

	# Series Profiling methods.

	def coverage(self):
		"""
			Information on which years have values in the series.
		Returns
		-------

		"""
		pass


	# Conversion methods
	def byYear(self, year, operation):
		""" Compares the series to its value in a given year.
			Parameters
			----------
				year: int
					A valid year to base all calculations on.
				operation: str; default 'ratio'
					* '-', 'difference': Returns the absolute difference between the base year
						and each other year.
					* '/', 'ratio': Returns the ratio between the base year and the base year.


		"""
		base_value = self.getValue(year)

		if operation == '/':
			new_series = self / base_value

		elif operation == '-':
			new_series = self - base_value
		else:
			message = "'{}' is not a valid annual operation type ('ratio', 'difference')"
			raise KeyError(message)
		return new_series


	def timeChange(self, kind = 'yearlyGrowth'):
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
				series: list<tuple<int,number>>
		"""

		newseries = list()

		cumulative_total = 0
		for year in self.x:

			v1 = self.getValue(year - 1)
			v2 = self.getValue(year)

			difference = v2 - v1
			ratio = v2 / v1
			if kind == 'yearlyChange':
				value = difference
			elif kind == 'yearlyGrowth':
				value = ratio

			elif kind == 'doublingTime':
				value = math.log(2) / math.log(ratio)

			elif kind == 'doublingYear':
				value = math.log(2) / math.log(ratio)
				value += year
			elif kind == 'cumulative':
				cumulative_total += v2
				value = cumulative_total
			else:
				message = "Invalid operation: '{}' ({})".format(
					kind,
					", ".join({'doublingTime', 'doublingYear', 'yearlyGrowth', 'yearlyChange'})
				)
				raise ValueError(message)

			if not math.isnan(value):
				newseries.append((year, value))
		newseries = self.emulate(self, newseries)
		return newseries


	@staticmethod
	def intersection():
		""" Calculates the projected time when self will intersect with other.
		"""
		return None


	def toTable(self):
		""" Converts the series to a dict, where each attribute becomes a dict key """
		region = self.region
		identifiers = {i.namespace.code: i.string for i in region.identifiers}
		series_dict = {
			'seriesCode':   self.code,
			'seriesName':   self.name,
			'regionName':   region.name,
			'seriesReport': self.report.name,
			'seriesUnit':   self.unit,
			'seriesScale':  self.scale
		}

		values = {i: j for i, j in self}

		series_dict = {**series_dict, **identifiers, **values}

		return series_dict


	def indexYear(self, index_year):
		""" Describes how a series has changed over time.
			Parameters
			----------
		"""

		index = self.getValue(index_year)

		result = list()
		for year, value in self:
			new_value = (index - value) / index
			result.append((year, new_value))

		new_series = self.emulate(self, result)
		return new_series


	def average(self):
		return sum(self.y) / len(self.x)

	def currentValue(self, default = math.nan, interpolate = False):

		current_year = datetime.datetime.now().year

		if interpolate or current_year in self.x:
			value = self.getValue(current_year)
		else:

			previous_years = [i for i in self.x if i <= current_year]
			if len(previous_years) == 0:
				value = default
			else:
				value = max(previous_years)

		return value

	# Properties

	@property
	def values(self):
		if not hasattr(self, '_values_cache'):
			self._values_cache = self._splitStringValues()
		return self._values_cache


	@property
	def x(self):
		if not hasattr(self, '_x_cache'):
			self._x_cache = [i[0] for i in self.values]

		return self._x_cache


	@property
	def y(self):
		if not hasattr(self, '_y_cache'):
			self._y_cache = [i[1] for i in self]
		return self._y_cache


	@property
	def multiplier(self):
		if not hasattr(self, '_multiplier_cache'):
			self._multiplier_cache = self.scale.multiplier
		return self._multiplier_cache

	@property
	def scale(self):
		raise NotImplementedError


	@property
	def strvalues(self):
		raise NotImplementedError


	@property
	def name(self):
		raise NotImplementedError


	@property
	def code(self):
		raise NotImplementedError


	@property
	def report(self):
		raise NotImplementedError


	@property
	def notes(self):
		raise NotImplementedError


	@property
	def region(self):
		raise NotImplementedError


	@property
	def unit(self):
		raise NotImplementedError
