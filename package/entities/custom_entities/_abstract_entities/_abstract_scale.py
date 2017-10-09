from ....github import numbertools

class AbstractScale:
	def __float__(self):
		""" Returns a floating-point represenation f 'Scale'
			Ex. Scale('Thousands') -> 1E3
		"""
		if self.multiplier:
			return float(self.multiplier)
		
		_string = self.string.lower()

		_default_conversions = {
			'trillion': 1E12,
			'billion': 1E9,
			'million': 1E6,
			'thousand': 1E3,
			'hundred': 1E2,
			'unit': 1.0,
			'tenth': 1E-1,
			'thousandth': 1E-3
		}

		if _string.endswith('s'):
			_string = _string[:-1]
		_value = _default_conversions.get(_string)
		if _value:
			return _value
		print("Scale String: ", self.string)

		return 1.0

	def __str__(self):
		return "Scale('{}')".format(self.scale)

	def __call__(self, array, human_readable = False):
		""" Returns the scaled version of the provided array.
			Ex. Scale('Hundreds')([1,2,3]) -> [100, 200, 300]
			Ex. Scale('Millions')(314) -> 314,000,000
			Ex. Scale('Thousands')([31.4, 2, 3], human_readable = True) -> ['31.4K', '200K', '300K']
		"""
		if not hasattr(array, '__iter__'):
			array = [array]

		result = [i * float(self) for i in array]

		if human_readable:
			result = numbertools.humanReadable(array)
		return result

	def __mul__(self, other):
		""" Multiplies a value by the floating-point representation of this Scale object."""

		result = other * float(self)

		return result

	def __rmul__(self, other):
		return self.__mul__(other)

	@property
	def multiplier(self):
		raise NotImplementedError

	@property
	def string(self):
		raise NotImplementedError

