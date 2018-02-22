
from math import isnan
from functools import partial
from pprint import pprint
pprint = partial(pprint, width = 180)

class CoreValidation:

	@staticmethod
	def _validateString(string, optional = False):
		is_valid = isinstance(string, str)
		if not optional:
			is_valid = is_valid and string != ''
		return is_valid


	@staticmethod
	def _validateNumber(value, optional = False, number_type = 'any'):
		if number_type == 'any':
			dtypes = (float, int)
		elif number_type == 'int':
			dtypes = int
		elif number_type == 'float':
			dtypes = float
		else:
			message = "'{}' is not a supported dtype!".format(number_type)
			raise ValueError(message)
		is_valid_number = isinstance(value, dtypes)

		if not optional:
			is_valid_number = is_valid_number and not isnan(value)
		return is_valid_number


	@staticmethod
	def _validateTimestamp(value, optional = False, require_timestamp = False):
		is_valid_timestamp = hasattr(value, 'year')

		if optional:
			is_valid_timestamp = is_valid_timestamp or value == ''

		if not require_timestamp:
			is_valid_timestamp = is_valid_timestamp or isinstance(value, str)

		return is_valid_timestamp

	@staticmethod
	def validateKeys(entity_type, expected_keys, keys):
		all_keys_are_present = all([i in keys for i in expected_keys])
		missing_keys = sorted(i for i in expected_keys if i not in keys)
		if not all_keys_are_present:
			print("Entity Type: ", entity_type)
			print("Expected Keys: ", sorted(expected_keys))
			print("Keys Given: ", sorted(keys))
			print("Missing Keys: ", missing_keys)
			raise KeyError("Missing one or more required keys!")
	@staticmethod
	def showError(entity_type, raw_parameters, validation_status):
		"""

		Parameters
		----------
		entity_type: str
		raw_parameters: dict
		validation_status: dict

		Returns
		-------

		"""
		print("An error occured when validating the API response.")
		print("Entity Type: ", entity_type)
		print("---------------------- Raw Arguments -------------------")
		pprint(raw_parameters)
		print("-------------------- Validation Status -----------------")
		pprint(validation_status)

		raise ValueError('The API response does not match the specification!')

