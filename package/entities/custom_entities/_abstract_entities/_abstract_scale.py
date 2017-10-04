
class AbstractScale:
	def __float__(self):
		""" Converts 'Scale' to a floating-point datatype """
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



	def __mul__(self, other):
		""" Multiplies a value by the value of 'scale' """

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

