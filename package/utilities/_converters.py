from pprint import pprint

import progressbar

from . import tables, validation
from ..github import tabletools


class ConvertTable:
	""" Designed to parse a spreadsheet and import it into the database.
		Parameters
		----------
		dataset: RegionDatabase
		filename: str, Table
		namespace: str
		report: dict
			Details concerning the report.
			* `name`: str
				The name of the report
			* `publishDate`: str
				The date the report was published
			* `retrieveDate`: str
				The date the report was looked up.
			* `url`: str
				A website url that contains the dataset or has further information on the dataset.
			Keyword Arguments
			-----------------
			* `blacklist`: list<str>
				A list of series names or codes to skip when processing the table.
			* `whitelist`: list<str>
				If provided, only the listed series will be imported. Overrides 'blacklist'.
			* `seriesTagMap`: dict
				(`region_code`, `subject_code`) -> `tag` | dict<str,str> -> str,list<str>
			* `seriesNoteMap`: dict
			* `seriesDescriptionMap`: dict

			* 'seriesCodeColumn':
			* 'seriesNameColumn':
			* 'regionCodeColumn':
			* 'regionNameColumn'
	"""
	def __init__(self, dataset, filename, namespace, report, **kwargs):

		self.dataset = dataset
		assert isinstance(namespace, str)
		assert isinstance(report, dict)
		assert isinstance(report.get('agency'), str)

		#agency, namespace, report = self.handleRequiredArguments(agency, namespace, report)
		series_list = self.importTable(filename, **kwargs)

		json = {
			'report': report,
			'namespace': namespace,
			'series': series_list
		}
		
		self.dataset.importJson(json)
	#@pony.orm.db_session
	def importTable(self, filename, **kwargs):
		""" Imports a spreadsheet into the database.
			Parameters
			----------
			filename: str, tabletools.Table, pandas.DataFrame
				The file path of the table to import. Should be compatible with tabletools.Table.




		"""
		if isinstance(filename, (str, tabletools.pandas.DataFrame)):
			table = tabletools.Table(filename)
		else:
			table = filename

		# Get the relevant columns for the data.
		column_categories = self.parseTableColumns(table.columns, **kwargs)

		json_table = list()
		print("Converting the table into a compatible json format...")
		pbar = progressbar.ProgressBar(max_value = len(table))
		
		for index, row in enumerate(table):
			pbar.update(index)
			parsed_row = self.convertRow(row, column_categories, **kwargs)
			if parsed_row:
				json_table.append(parsed_row)
		
		return json_table

	def importJson(self, data, namespace, report):
		""" Imports a valid json/dict object into the database.

		:param data:
		:param namespace:
		:param report:
		:return:
		"""
		
		region_code = data['regionCode']
		region = self.dataset.getRegion(region_code, namespace)
		
		#agency = self.dataset.importEntity('agency', agency)
		#report['agency'] = agency 
		#report = self.dataset.importEntity('report', report)

		series = data
		series['region'] = region
		series['report'] = report 
		self.dataset.importjson(series)

	def handleRequiredArguments(self, agency, namespace, report):
		""" Confirms that the three arguments that must be provided are valid.
		"""
		
		agency 		= self.dataset.importEntity('agency', agency)
		namespace 	= self.dataset.requestNamespace(namespace)
		report['agency'] = agency
		report 		= self.dataset.insertEntity('report', report)

		try:
			assert agency
			assert report
			assert namespace
		except AssertionError as exception:
			validation.debugEntity('agency', agency)
			validation.debugEntity('namespace', namespace)
			validation.debugEntity('report', report)
			raise exception

		return agency, namespace, report
	@staticmethod
	def parseTableColumns(columns, **kwargs):
		""" Classifies the key columns that *must* be present in order to import a spreadhseet.
			Parameters
			----------
			columns: list<str>
				The columns present in the table.
			
			Keyword Arguments
			-----------------

			Notes
			-----
				This method identifies which columns contain information
				related to the region and subject.
		"""
		result = tables.getRequiredColumns(columns, **kwargs)
		region_code_column 		= result['regionCodeColumn']
		region_name_column 		= result['regionNameColumn']
		series_code_column 		= result['seriesCodeColumn']
		series_name_column 		= result['seriesNameColumn']
		series_note_column 		= result['seriesNoteColumn']
		series_scale_column		= result['seriesScaleColumn']
		series_description_column = result['seriesDescriptionColumn']

		# Check if any selectionmethods were included as kwargs
		_region_code_column_keyword = kwargs.get('regionCodeColumn')
		_region_name_column_keyword = kwargs.get('regionNameColumn')
		_series_code_column_keyword = kwargs.get('seriesCodeColumn', kwargs.get('subjectCodeColumn'))
		_series_name_column_keyword = kwargs.get('seriesNameColumn', kwargs.get('subjectNameColumn'))

		if _region_code_column_keyword:
			region_code_column = _region_code_column_keyword
		
		if _region_name_column_keyword:
			region_name_column = _region_name_column_keyword
		
		if _series_code_column_keyword:
			series_code_column = _series_code_column_keyword

		if _series_name_column_keyword:
			series_name_column = _series_name_column_keyword
		result['regionCodeColumn'] = region_code_column
		result['regionNameColumn'] = region_name_column
		result['seriesCodeColumn'] = series_code_column
		result['seriesNameColumn'] = series_name_column
		
		try:
			assert series_code_column
			assert series_name_column 
			assert region_code_column
			assert region_name_column
		except AssertionError as exception:
			print("Columns: ")
			for col in columns:
				print("\t", col)
			print("Column Categories:")
			for k, v in result.items():
				print("\t{}\t{}".format(k, v))
			print("Keyword Arguments:")
			for k,v in kwargs.items():
				print("\t{}\t{}".format(k, v))
			print("Region Name Column: ", region_name_column)
			print("Region Code Column: ", region_code_column)
			print("Series Code Column: ", series_code_column)
			print("Series Name Column: " ,series_name_column)
			print("Series Note Column: ", series_note_column)
			print("Series Scale Column:", series_scale_column)
			print("Series Description Column: ", series_description_column)
			raise exception
		
		return result

	def convertRow(self, row, column_classifier, **kwargs):
		""" Converts a row into an importable dict.
			Parameters
			----------
			row: dict, pandas.Series
			column_classifier: dict

			Keyword Arguments
			-----------------
				* unitMap: dict<tuple,dict>
				* scaleMap: dict<tuple,dict>
				* tagMap: dict<tuple,dict>
				* descriptionMap: dict<tuple,dict>
				* blacklist: list<>
					A list of series keys to skip when importing a table.
				* whitelist: list<>
					Overrides the blacklist. Only the series key contained in
					the whitelist will be imported.
		"""
		# Confirm that all required components exist.
		blacklist = kwargs.get('blacklist', [])
		whitelist = kwargs.get('whitelist')

		# Should be static
		try:
			region_code = row[column_classifier['regionCodeColumn']] # identifier
			region_name = row[column_classifier['regionNameColumn']]

			subject_code = row[column_classifier['seriesCodeColumn']]
			subject_name = row[column_classifier['seriesNameColumn']]
		except KeyError as exception:
			print(str(exception))
			for k, v in row.items():
				print("\t{}\t{}".format(k, v))
			raise exception
		_in_whitelist 		= (not whitelist or subject_code in whitelist)
		_not_in_blacklist 	= (not whitelist and subject_code not in blacklist)
		use_row 			= _in_whitelist or _not_in_blacklist

		if use_row:
			# May be dynamic
			#subject_description = column_classifier['description'](row, region_code, region_name)
			#subject_notes 		= column_classifier['notes'](row, region_code, subject_code)
			
			# Retrieve the series unit configuration
			json_units = self._getUnits(row, region_code, subject_code, column_classifier, kwargs.get('seriesUnitMap'))
			# Retrieve the series scale configuration.
			series_scale = self._getScale(row, region_code, subject_code, column_classifier, kwargs.get('seriesScaleMap'))
			# Retrieve any available tags
			series_tags = self._getTags(region_code, subject_code, kwargs.get('seriesTagMap'))

			subject_description = self._getDescription(row, region_code, subject_code, column_classifier, kwargs.get('seriesDescriptionMap'))
			# Parse the sereis values.
			values = self._getValues(row)

			json_series = {
				'regionCode': region_code,
				'regionName': region_name,
				'seriesName': subject_name,
				'seriesCode': subject_code,
				'seriesScale': series_scale,
				
				#'seriesNotes': subject_notes,
				'seriesDescription': subject_description,
				'seriesTags': series_tags,
				'seriesUnits': json_units,
				'values': values
			}
		else:
			json_series = None
		
		return json_series

	def _getUnits(self, row, region_code, subject_code, column_classifier, unit_map):
		""" Retrieves the values for the units from the provided information.
			Parameters
			----------
			row: dict, pandas.Series
			column_classifier: dict
			unit_map:dict, None
		"""
		unit_code_column = column_classifier['seriesUnitCodeColumn']
		unit_string_column = column_classifier['seriesUnitNameColumn']

		result = self._genericMap(region_code, subject_code, unit_map)

		if result is None and unit_string_column in row.keys():
			unit_string = row[unit_string_column]
			unit_code = row.get(unit_code_column)

			result = {
				'unitString': unit_string
			}
			if isinstance(unit_code, str):
				result['unitCode'] = unit_code


		return result

	def _getScale(self, row, region_code, subject_code, column_classifier, scale_map):
		scale_string_column = column_classifier['seriesScaleColumn']

		result = self._genericMap(region_code, subject_code, scale_map)

		if result is None and scale_string_column in row.keys():
			result = row[scale_string_column]

		return result

	@staticmethod
	def _getValues(row):
		year_columns, _ = tables.separateTableColumns(row.keys())

		values = [(int(year), row[year]) for year in year_columns]
		
		return values
	
	def _getTags(self, region_code, subject_code, tag_map):
		result =  self._genericMap(region_code, subject_code, tag_map)
		if isinstance(result, str):
			result = [result]
		return result


	def _getDescription(self, row, region_code, subject_code, column_classifier, description_map):

		description_column = column_classifier['seriesDescriptionColumn']

		result = self._genericMap(region_code, subject_code, description_map)
		
		if result is None and description_column in row.keys():
			result = row[description_column]
		
		return result

	@staticmethod
	def _genericMap(region_code, subject_code, mapper):
		if not mapper:
			result = None
		elif isinstance(mapper, dict):
			result = mapper.get((region_code, subject_code))
		elif callable(mapper):
			result = mapper(region_code, subject_code)
		else:
			message = "'{}' ('{}') is not a valid Map object".format(mapper, type(mapper))
			raise ValueError(message)
		
		return result
