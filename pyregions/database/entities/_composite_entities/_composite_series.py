from .._data_containers import DataSeries
import pandas
from pprint import pprint
from functools import partial
from ....github import timetools


pprint = partial(pprint, width = 200)



class CompositeSeries(DataSeries):
	"""
		Parameters
		----------
		region_data: dict<>
		report_data: dict<>
		members: list<dict>, list<DataSeries>
			A list of the series to combine.
		kwargs:
		* 'skipna': bool; default False
			If True, will ignore missing values and continue combining any non-missing values present in the series.
			If False, any year where a subregion is missing a value will be assigned math.nan.
	"""

	def __init__(self, region_data, report_data, members, **kwargs):
		if isinstance(members[0], dict):
			subjects = [DataSeries(i) for i in members]
		else:
			subjects = members
		self.members = subjects

		skipna = kwargs.get('skipna', False)

		# Check for common errors
		self._checkForBasicErrors(self.members)
		if 'entityKey' not in region_data:
			region_data['entityKey'] = region_data['regionName']
		region_name = region_data['regionName']

		composite_dataframe, composite_values = self._combineMembers(region_name, subjects, skipna = skipna)
		first_member = subjects[0]
		subject_code = first_member['seriesCode']
		subject_name = first_member['seriesName']
		subject_description = first_member['seriesDescription']
		subject_scale = first_member['seriesScale']
		subject_units = first_member['seriesUnits']

		composite_series_data = {
			'entityType':        'series',
			'entityKey':         subject_code,
			'seriesRegion':      region_data,
			'seriesReport':      report_data,
			'seriesCode':        subject_code,
			'seriesName':        subject_name,
			'seriesDescription': subject_description,
			'seriesScale':       subject_scale,
			'seriesUnits':       subject_units,
			'seriesValues':      [(timetools.Timestamp(i), j) for i, j in composite_values.items()]
		}

		super().__init__(composite_series_data, israw = False)

		self.dataframe = composite_dataframe

	def __str__(self):
		string = "Composite" + super().__str__()
		return string

	@staticmethod
	def _checkForBasicErrors(subjects):
		subject_codes = set()
		subject_names = set()

		for i in subjects:
			subject_codes.add(i['seriesCode'])
			subject_names.add(i['seriesName'])

		if len(subject_codes) != 1:
			pprint(subject_codes)
			raise ValueError

		if len(subject_names) != 1:
			pprint(subject_names)
			raise ValueError

	@staticmethod
	def _combineMembers(region_name, members, skipna):

		#TODO Chack if all members share the same index. Make sure each years begins at the same day.


		dataframe = pandas.DataFrame(i.series for i in members)

		composite_series = dataframe.sum(skipna = skipna)
		composite_series.rename(region_name)

		return dataframe, composite_series


	def composition(self):
		"""
			Generates a table showing how each region contributes to the individual values.
		Returns
		-------

		"""
		pass

	def toSql(self):
		raise NotImplementedError
