from ._core_validation import CoreValidation
from typing import *

class ValidateSqlResponse(CoreValidation):
	def __init__(self):
		self.expected_region_keys:List[str] = ['name', 'code', 'regionType']

	@staticmethod
	def validateEntity(entity, entity_type):
		if entity_type == 'units':
			entity_type = 'unit'
		return hasattr(entity, 'entity_type') and entity.entity_type == entity_type

	def validatestrValues(self, values:str)->bool:
		"""

		Parameters
		----------
		values: str

		Returns
		-------

		"""
		xy_separator = '|'
		point_separator = '||'

		unpacked_values = values.split(point_separator)
		unpacked_values = [i.split(xy_separator) for i in unpacked_values]
		unpacked_values = [(i, float(j)) for i, j in unpacked_values]

		x_values_status = [self._validateString(i) for i, j in unpacked_values]
		y_values_status = [self._validateNumber(j) for i, j in unpacked_values]
		is_valid = all(x_values_status + y_values_status)
		if not is_valid:
			print("Series Values:")
			for i, j, k in zip(unpacked_values, x_values_status, y_values_status):
				print("{}\t{}\t{}".format(i, j, k))
		return is_valid

	def validateRegion(self, response:Dict)->None:
		required_region_keys = ['name', 'code', 'type']

		self.validateKeys('region', required_region_keys, response.keys())

		region_name = response['name']
		region_code = response['code']
		region_type = response['type']

		region_validation_status = {
			'regionNameIsValid': self._validateString(region_name),
			'regionCodeIsValid': self._validateString(region_code),
			'regionTypeIsValid': self._validateString(region_type)
		}

		if not all(region_validation_status.values()):
			self.showError('region', response, region_validation_status)

	def validateReport(self, response):
		expected_report_keys = [
			'name', 'code', 'url', 'date', 'agency'
		]

		self.validateKeys('report', expected_report_keys, response.keys())

		report_name = response['name']
		report_code = response['code']
		report_url = response['url']
		report_date = response['date']
		report_agency = response['agency']

		report_validation_status = {
			'reportNameIsValid':   self._validateString(report_name),
			'reportCodeIsValid':   self._validateString(report_code),
			'reportUrlIsValid':    self._validateString(report_url),
			'reportDateIsValid':   self._validateTimestamp(report_date),
			'reportAgencyIsValid': self.validateEntity(report_agency, 'agency')
		}
		if not all(report_validation_status.values()):
			self.showError('report', response, report_validation_status)

	def validateAgency(self, response):

		expected_agency_keys = ['code', 'name', 'url', 'address']

		self.validateKeys('agency', expected_agency_keys, response.keys())

		agency_name = response['name']
		agency_code = response['code']
		agency_url = response['url']
		agency_address = response['address']

		agency_validation_status = {
			'agencyNameIsValid':    self._validateString(agency_name),
			'agencyCodeIsValid':    self._validateString(agency_code),
			'agencyUrlIsValid':     self._validateString(agency_url),
			'agencyAddressIsValid': self._validateString(agency_address)
		}

		if not all(agency_validation_status.values()):
			self.showError('agency', response, agency_validation_status)

	def validateSeries(self, response):
		expected_series_keys = [
			'region', 'report', 'code', 'name', 'description', 'notes', 'units', 'scale', 'strvalues'
		]

		self.validateKeys('series', expected_series_keys, response.keys())

		series_name = response['name']
		series_code = response['code']
		series_region = response['region']
		series_report = response['report']
		series_description = response['description']
		series_notes = response['notes']

		series_units = response['units']
		series_scale = response['scale']
		series_values = response['strvalues']

		series_validation_status = {
			'seriesNameIsValid':        self._validateString(series_name),
			'seriesCodeIsValid':        self._validateString(series_code),
			'seriesDescriptionIsValid': self._validateString(series_description),
			'seriesNotesAreValid':      self._validateString(series_notes),
			'seriesRegionIsValid':      self.validateEntity(series_region, 'region'),
			'seriesReportIsValid':      self.validateEntity(series_report, 'report'),
			'seriesUnitsAreValid':      self.validateEntity(series_units, 'units'),
			'seriesScaleIsValid':       self.validateEntity(series_scale, 'scale'),
			'seriesValuesAreValid':     self.validatestrValues(series_values)
		}

		if not all(series_validation_status.values()):
			self.showError('series', response, series_validation_status)

	def validateUnit(self, response):
		expected_unit_keys = ['string', 'code']

		self.validateKeys('unit', expected_unit_keys, response.keys())

		unit_string = response['string']
		unit_code = response['code']

		unit_validation_status = {
			'unitStringIsValid': self._validateString(unit_string),
			'unitCodeIsValid':   self._validateString(unit_code)
		}

		if not all(unit_validation_status.keys()):
			self.showError('unit', response, unit_validation_status)

	def validateScale(self, response):
		expected_scale_keys = ['string', 'multiplier']

		self.validateKeys('scale', expected_scale_keys, response.keys())

		scale_string = response['string']
		scale_multiplier = response['multiplier']

		scale_validation_status = {
			'scaleStringIsValid':     self._validateString(scale_string),
			'scaleMultiplierIsValid': self._validateNumber(scale_multiplier, number_type = 'float')
		}

		if not all(scale_validation_status.values()):
			self.showError('scale', response, scale_validation_status)

	def validateNamespace(self, response):
		expected_namespace_keys = ['name', 'code', 'regex', 'url']

		self.validateKeys('namespace', expected_namespace_keys, response.keys())

		namespace_name = response['name']
		namespace_code = response['code']
		namespace_regex = response['regex']
		namespace_url = response['url']

		namespace_validation_status = {
			'namespaceNameIsValid':  self._validateString(namespace_name),
			'namespaceCodeIsValid':  self._validateString(namespace_code),
			'namespaceRegexIsValid': self._validateString(namespace_regex),
			'namespaceUrlIsValid':   self._validateString(namespace_url)
		}

		if not all(namespace_validation_status.values()):
			self.showError('namespace', response, namespace_validation_status)

	def validateIdentifier(self, response):
		expected_identifier_keys = ['string', 'region', 'namespace']

		self.validateKeys('identifier', expected_identifier_keys, response.keys())

		identifier_string = response['string']
		identifier_region = response['region']
		identifier_namespace = response['namespace']

		identifier_validation_status = {
			'identifierStringIsValid':    self._validateString(identifier_string),  # TODO Implement Regex
			'identifierRegionIsValid':    self.validateEntity(identifier_region, 'region'),
			'identifierNamespaceIsValid': self.validateEntity(identifier_namespace, 'namespace')
		}

		if not all(identifier_validation_status.values()):
			self.showError('identifier', response, identifier_validation_status)

	def validateResponse(self, kind, response):
		if kind == 'series':
			self.validateSeries(response)
		elif kind == 'region':
			self.validateRegion(response)
		elif kind == 'report':
			self.validateReport(response)
		elif kind == 'agency':
			self.validateAgency(response)
		elif kind == 'scale':
			self.validateScale(response)
		elif kind == 'unit':
			self.validateUnit(response)
		elif kind == 'namespace':
			self.validateNamespace(response)
		elif kind == 'identifier':
			self.validateIdentifier(response)
		else:
			raise ValueError
