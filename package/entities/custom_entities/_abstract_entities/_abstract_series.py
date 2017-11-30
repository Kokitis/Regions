import math

from scipy.interpolate import interp1d
from pony.orm import db_session

class AbstractSeries:

	""" Sets up common operations on a Series instance. Defines all required properties that 
		every subsequent Series entity must implement. 
	"""
	entity_type = 'series'
	_values = None
	def __call__(self, x, absolute = False, method = 'inner', fill_value = math.nan):
		""" Returns the `y` value at `x`. Interpolation is supported.
			Parameters
			----------
			x: int
				The x-value to use when calculating the y-value
			absolute: bool; default True
				If True, the returned y-value will be automatically scaled according
				to the series.scale value.
			method: {'interpolate', 'inner', 'exact'}
				* 'interpolate': 
				* 'inner': 
				* 'exact': 	
			fill_value: int, float; default math.nan
				Returned if there is no corresponding `y` for the given `x`
		"""
		if not hasattr(self, '_interpolate'):
			self.setInterpolation()
		
		if method == 'extrapolate':
			value = self._interpolate(x)
		elif method == 'inner':
			if min(self.x) <= x <= max(self.x):
				value = self._interpolate(x)
			else:
				value = math.nan
		else:
			value = self._interpolate(x) if x in self.x else math.nan
		value = float(value)
		return value

	#@db_session
	def __iter__(self):
		for i in self.values:
			yield i
	#@db_session
	def __add__(self, other):
		#print("__add__({},{})".format(self, other))
		return self._applyOperation(self, other, '+')
	#@db_session
	def __sub__(self, other):
		return self._applyOperation(self, other, '-')
	#@db_session
	def __mul__(self, other):
		return self._applyOperation(self, other, '*')
	#@db_session
	def __div__(self, other):
		return self._applyOperation(self, other, '/')
	#@db_session
	def __truediv__(self, other):
		return self._applyOperation(self, other, '/')
	#@db_session
	def __radd__(self, other):
		#print("__radd__({}, {})".format(self, other))
		return self.__add__(other)
	#@db_session
	def __rmul__(self, other):
		return self.__mul__(other)

	@db_session
	def _convertToParsableFormat(self, other):
		# Convert 'other' into a parsable format.
		if hasattr(other, 'entity_type') and other.entity_type == 'series':
			_parsable = other 
		else:
			try:
				_parsable = list(other)
			except TypeError:
				try:
					_parsable = [(i, float(other)) for i in self.x]
				except Exception as exception:
					message = "Invalid type for series operation: value = {}, type = {}".format(other, type(other))
					print(message)
					raise exception
			
			_parsable = self.emulate(self, sorted(_parsable))

		return _parsable

	@staticmethod
	def _apply2DOperation(y, other_y, operation):
		# Basic operations
		if operation == '+':
			new_y = y + other_y
		elif operation == '-':
			new_y = y - other_y
		elif operation == '*':
			new_y = y * other_y
		elif operation == '/':
			new_y = y / other_y
		
		# Relational operations
		elif operation == '==':
			new_y = y == other_y
		elif operation == '>=':
			new_y = y >= other_y
		elif operation == '>':
			new_y = y > other_y
		elif operation == '<':
			new_y = y < other_y
		elif operation == '<=':
			new_y = y <= other_y 
		elif operation == '!=':
			new_y = y != other_y

		elif operation == '%':
			# Relative change
			new_y = (other_y - y) / y 

		else:
			message = "Invalid operation: '{}'".format(operation)
			raise ValueError(message)
		
		return new_y

	@classmethod
	def _applyOperation(cls, left, right, operation, method = 'extrapolate', domain = None):
		""" The point of entry for comparing/applying operations to this series object. 
			Parameters
			----------
			other: number, list, Series
				The other value set to compare against `self`
			method: {'extrapolate', 'strict', 'inner'}
			domain: list, tuple
				The x-values to iterate over. Defalts to `self.x`.
			Returns
			-------
			result: Series
		"""

		if not hasattr(left, 'entity_type') or left.entity_type != 'series':
			if hasattr(right, 'entity_type') and right.entity_type == 'series':
				left, right = right, left
			else:
				print('Left Argument Type: ', type(left))
				print('Right Argument Type: ', type(right))
				raise TypeError('At least one of the arguments must be a series!')
			
		if right == 0: 
			return left # sum() tries to add 0 to the objects

		if domain is None: domain = left.x

		right = left._convertToParsableFormat(right)

		result = list()

		for x in domain:
			y = left(x, method = method, absolute = True)
			other_y = right(x, method = method, absolute = True)
			new_y = left._apply2DOperation(y, other_y, operation)
			result.append((x, new_y))
		
		configuration = dict()
		if operation in {'/'}:
			configuration['scale'] = None
		else:
			configuration['scale'] = left.scale
		

		result = left.emulate(left, result, **configuration)

		return result
	
	def setInterpolation(self, bounds = 'nan'):
		""" Runs once to generate an interpolation for the series 
			Parameters
			----------
			bounds: {'nan', 'zero', 'bounds', 'extrapolate'}:
				Describes how to handle x values outside of the provided `x` range 
				* 'nan': All values outside the provided domain return *nan*
				* 'zero': Any call to an `x` value outside of the series `x` values
					returns zero
				* 'bounds': returns x[0] for calls to undefined x's below min(x) and returns
					x[-1] for calls to x's greater than max(x)
				* 'extrapolate': Values outside the x range are extrapolated.
		"""
		if len(self.x) > 1:
			if bounds == 'bounds':
				bounds = (self.y[0], self.y[-1])
			elif bounds == 'zero':
				bounds = (0, 0)
			elif bounds == 'extrapolate':
				bounds = 'extrapolate'
			elif bounds == 'nan' or bounds is None:
				bounds = (math.nan, math.nan)

			_interpolation = interp1d(
				self.x, 
				self.y,
				bounds_error = False,
				fill_value = bounds
			)
		elif len(self.x) == 1:
			_interpolation = lambda s: self.y[0]
		else:
			_interpolation = lambda s: math.nan
		self._interpolate = _interpolation

	@classmethod
	def emulate(cls, template, values, **kwargs):
		raise NotImplementedError

	@db_session
	def _splitStringValues(self):
		numeric_values = [
			(int(i[0]), float(i[1]) * self._rate())
			for i in [
				point.split('|') for point in self.strvalues.split('||')
			]
		]
		return numeric_values

	@db_session
	def _rate(self):
		_i = self.scale
		if not _i:
			_i = 1.0
		return _i

	@property
	def values(self):
		raise NotImplementedError

	@property
	def x(self):
		return [i[0] for i in self]

	@property
	def y(self):
		return [i[1] for i in self]

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
		#[your_string[i:i+n] for i in range(0, len(your_string), n)]

		description = ['\t'+self.notes[i:i+_max_width] for i in range(0, len(self.notes), _max_width)]
		description = "\n".join(["Notes:"] + description)

		string = lines + '\n' + description
		print(string)

	def export(self):
		result = {
			'code': self.code,
			'name': self.name,
			'report': self.report.name,
			'regionCode': self.region.code,
			'regionName': self.region.name,
			'values': list(self.values),
			'scale': self.scale,
			'units': self.unit,
			'notes': self.notes
		}
		return result


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
		base_value = self(year)

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

			v1 = self(year-1)
			v2 = self(year)

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
		identifiers = {i.namespace.code:i.string for i in region.identifiers}
		series_dict = {
			'seriesCode': self.code,
			'seriesName': self.name,
			'regionName': region.name,
			'seriesReport': self.report.name,
			'seriesUnit': self.unit,
			'seriesScale': self.scale
		}

		values = {i:j for i,j in self}

		series_dict = {**series_dict, **identifiers, **values}

		return series_dict
	
	def indexYear(self, index_year):
		""" Describes how a series has changed over time.
			Parameters
			----------
		"""

		index = self(index_year)

		result = list()
		for year, value in self:
			new_value = (index - value) / index 
			result.append((year, new_value))
		
		new_series = self.emulate(self, result)
		return new_series

	def average(self):
		return sum(self.y) / len(self.x)

