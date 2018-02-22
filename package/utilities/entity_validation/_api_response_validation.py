
from pprint import pprint
from functools import partial
pprint = partial(pprint, width = 180)
from ._core_validation import CoreValidation
class ValidateApiResponse(CoreValidation):
	"""
		Expected Format:
		* 'namespace": str, dict<>
		* 'report': dict<>
			* 'reportName': str
			* 'reportCode': str
			* 'reportAgency': dict<>
				* 'agencyName': str
				* 'agencyCode': str
				* 'agencyAddress': str
				* 'agencyUrl': str
			* 'reportDate': Timestamp
			* 'reportUrl': str
		* 'reportData': list<dict<>>
			* 'regionCode': str
			* 'regionName': str
			* 'regionType': str
			* 'regionIdentifiers': list<>
			* 'regionSeries': dict<>
				* 'seriesName': str
				* 'seriesCode': str
				* 'seriesDescription': str
				* 'seriesNotes': str
				* 'seriesTags: list<str>
				* 'seriesUnits': str, dict<>
				* 'seriesScale': str, dict<>

	"""

	def __init__(self, response):
		self.required_primary_keys =['report', 'agency', 'regions']
		self.required_report_keys = ['reportName', 'reportCode', 'reportDate', 'reportUrl']
		self.required_region_keys = ['regionName', 'regionCode', 'regionType', 'regionSeries']
		self.required_agency_keys = ['agencyName', 'agencyCode', 'agencyAddress', 'agencyUrl']
		self.required_series_keys = [
			'seriesName', 'seriesCode', 'seriesDescription', 'seriesNotes', 'seriesTags', 'seriesUnits', 'seriesScale'
		]

		self.validateKeys('report', self.required_primary_keys, response.keys())

		report_arguments = response['report']
		report_agency_arguments = response['agency']
		report_data = response['regions']

		self._validateReport(report_arguments)
		self._validateAgency(report_agency_arguments)
		self._validateReportData(report_data)



	def _validateReport(self, response):

		self.validateKeys('report', self.required_report_keys, response.keys())
		report_name = response['reportName']
		report_code = response['reportCode']
		report_date = response['reportDate']
		report_url = response['reportUrl']

		name_is_valid = self._validateString(report_name)
		code_is_valid = self._validateString(report_code)
		date_is_valid = self._validateTimestamp(report_date)
		url_is_valid = self._validateString(report_url)

		report_validation_results = {
			'reportNameIsValid': name_is_valid,
			'reportCodeIsValid': code_is_valid,
			'reportDateIsValid': date_is_valid,
			'reportUrlIsValid':  url_is_valid
		}

		report_is_valid = all(report_validation_results.values())

		if not report_is_valid:
			self.showError('report', response, report_validation_results)

		return report_validation_results

	def _validateReportData(self, report_regions):
		data_validation_status = list()
		for region in report_regions:

			self.validateKeys('region', self.required_region_keys, region.keys())
			region_name = region['regionName']
			region_code = region['regionCode']
			region_type = region['regionType']

			name_is_valid = self._validateString(region_name)
			code_is_valid = self._validateString(region_code)
			type_is_valid = self._validateString(region_type)

			region_validation_status = {
				'regionNameIsValid':             name_is_valid,
				'regionCodeIsValid':             code_is_valid,
				'regionTypeIsValid':             type_is_valid
			}
			region_is_valid = all([name_is_valid, code_is_valid, type_is_valid])

			if not region_is_valid:
				region.pop('regionSeries')
				self.showError('region', region, region_validation_status)

			validated_region_series = list()
			region_rows = region['regionSeries']

			for rs in region_rows:
				if not hasattr(rs, 'keys'):
					for i, s in enumerate(region_rows):
						print(i, '\t', type(s))

				series_validation_status = self._validateSeries(rs)
				series_is_valid = series_validation_status['validationStatus']

				if not series_is_valid:
					self.showError('series', rs, series_validation_status)
				else:
					validated_region_series.append(series_validation_status)



		return data_validation_status

	def _validateAgency(self, report_agency):

		self.validateKeys('agency', self.required_agency_keys, report_agency.keys())

		agency_name = report_agency['agencyName']
		agency_code = report_agency['agencyCode']
		agency_address = report_agency['agencyAddress']
		agency_url = report_agency['agencyUrl']

		agency_name_is_valid = self._validateString(agency_name)
		agency_code_is_valid = self._validateString(agency_code)
		agency_address_is_valid = self._validateString(agency_address)
		agency_url_is_valid = self._validateString(agency_url)

		agency_validation_status = {
			'agencyNameIsValid':    agency_name_is_valid,
			'agencyCodeIsValid':    agency_code_is_valid,
			'agencyAddressIsValid': agency_address_is_valid,
			'agencyUrlIsValid':     agency_url_is_valid
		}

		agency_is_valid = all(agency_validation_status.values())
		if not agency_is_valid:
			self.showError('agency', report_agency, agency_validation_status)

		return agency_validation_status

	def _validateSeries(self, series):

		self.validateKeys('series', self.required_series_keys, series.keys())


		series_name = series['seriesName']
		series_code = series['seriesCode']
		series_description = series['seriesDescription']
		series_notes = series['seriesNotes']
		series_tags = series['seriesTags']
		series_unit = series['seriesUnits']
		series_scale = series['seriesScale']

		series_name_is_valid = self._validateString(series_name)
		series_code_is_valid = self._validateString(series_code)
		series_description_is_valid = self._validateString(series_description)
		series_notes_is_valid = self._validateString(series_notes, optional = True)

		if not isinstance(series_tags, list):
			series_tags_is_valid = False
		elif len(series_tags) == 0:
			series_tags_is_valid = True
		else:
			series_tags_is_valid = all([self._validateString(i) for i in series_tags])

		series_unit_is_valid = self._validateUnit(series_unit)
		series_scale_is_valid = self._validateScale(series_scale)

		all_valid_list = [
			series_name_is_valid, series_code_is_valid, series_description_is_valid,
			series_notes_is_valid, series_tags_is_valid, series_unit_is_valid, series_scale_is_valid
		]
		all_valid = all(all_valid_list)

		series_values_are_valid = True

		series_validation_status = {
			'validationStatus': all_valid,
			'seriesNameIsValid': series_name_is_valid,
			'seriesCodeIsValid': series_code_is_valid,
			'seriesDescriptionIsValid': series_description_is_valid,
			'seriesNotesIsValid': series_notes_is_valid,
			'seriesTagsIsValid': series_tags_is_valid,
			'seriesUnitsAreValid': series_unit_is_valid,
			'seriesScaleIsValid': series_scale_is_valid,
			'seriesValuesAreValid': series_values_are_valid
		}

		return series_validation_status

	def _validateUnit(self, series_unit):
		if isinstance(series_unit, dict):
			unit_string = series_unit.get('unitString')
			unit_code = series_unit.get('unitCode')
			unit_string_is_valid = self._validateString(unit_string)
			unit_code_is_valid = self._validateString(unit_code)
			series_unit_is_valid = unit_string_is_valid and unit_code_is_valid
		else:
			series_unit_is_valid = isinstance(series_unit, str)
		return series_unit_is_valid

	def _validateScale(self, series_scale):
		if isinstance(series_scale, dict):
			scale_string = series_scale.get('scaleString')
			scale_multiplier = series_scale.get('scaleMultiplier')

			scale_string_is_valid = self._validateString(scale_string)
			scale_multiplier_is_valid = self._validateNumber(scale_multiplier)
			series_scale_is_valid = scale_string_is_valid and scale_multiplier_is_valid
		else:
			series_scale_is_valid = isinstance(series_scale, str)
		return series_scale_is_valid

