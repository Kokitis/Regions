import progressbar

from package.utilities import tables
from package.github import tabletools, pprint, timetools, numbertools
from math import isnan
from.entity_validation import ValidateApiResponse


class TableApi:
	""" Designed to parse a spreadsheet and import it into the database.
		Parameters
		----------
		filename: str, Table
		report: dict
			Details concerning the report.
			* 'name': str
				The name of the report
			* 'publishDate': str
				The date the report was published
			* 'retrieveDate': str
				The date the report was looked up.
			* 'url': str
				A website url that contains the dataset or has further information on the dataset.
		agency: dict<>
			*'name': str

		Keyword Arguments
		-----------------
		* 'tableConfig': dict
			Arguments to pass to pandas.DataFrame()
		* 'startDay': str; default '01-01'
		* 'jsonCompatible': bool; default False
		* 'blacklist': list<str>
			A list of series names or codes to skip when processing the table.
		* 'whitelist': list<str>
			If provided, only the listed series will be imported. Overrides 'blacklist'.

		* 'seriesTagColumn', 'seriesTagMap': str, dict
			Either the column containing tags for the series for the series, or a dictionary
			mapping series codes to relevant tags.
		* 'seriesTagDelimiter': str; default '|' Todo
			The delimiter used to unpack the tags if tags are provided as a str.
		* 'seriesNoteColumn', 'seriesNoteMap': str, dict
			Dictionary keys should be strings of the form 'region_code|subject_code'. region_code defaults to None.
		* 'seriesDescriptionColumn', 'seriesDescriptionMap': str, dict

		* 'seriesCodeColumn': str
		* 'seriesNameColumn': str
		* 'regionCodeColumn': str
		* 'regionNameColumn': str

		Returns
		-------
		dict<>
	"""

	def __init__(self, filename, **kwargs):
		kwargs['startDay'] = kwargs.get('startDay', '01-01')

		kwargs['jsonCompatible'] = kwargs.get('jsonCompatible', False) or 'saveTo' in kwargs
		file_kwargs = kwargs.get('tableConfig', dict())
		namespace_key = kwargs.get('namespace')
		report = kwargs.get('report')
		agency = kwargs.get('agency')
		assert isinstance(namespace_key, str)
		assert isinstance(report, dict)
		assert isinstance(agency, dict)

		report_table = self._openTable(filename, **file_kwargs)

		region_list = self._parseTable(report_table, **kwargs)

		report_information = {
			'report':    report,
			'agency':    agency,
			'namespace': namespace_key,
			'regions':   region_list
		}

		self.data = report_information

		save_filename = kwargs.get('saveTo')
		if save_filename:
			import json
			with open(save_filename, 'w') as file1:
				file1.write(json.dumps(self.data, indent = 4, sort_keys = True))

		ValidateApiResponse(self.data)


	@staticmethod
	def _openTable(filename, **kwargs):
		if isinstance(filename, str):
			table = tabletools.Table(filename, **kwargs)
		else:
			table = filename

		return table

	@staticmethod
	def _getColumnNames(columns, **kwargs):
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
		detected_columns = tables.getRequiredColumns(columns, **kwargs)
		region_code_column = detected_columns['regionCodeColumn']
		region_name_column = detected_columns['regionNameColumn']
		series_code_column = detected_columns['seriesCodeColumn']
		series_name_column = detected_columns['seriesNameColumn']

		series_note_column = detected_columns['seriesNoteColumn']
		series_tag_column = detected_columns['seriesTagColumn']
		series_unit_column = detected_columns['seriesUnitNameColumn']
		series_scale_column = detected_columns['seriesScaleColumn']
		series_description_column = detected_columns['seriesDescriptionColumn']

		# Check if any selection methods were included as kwargs
		_region_code_column_keyword = kwargs.get('regionCodeColumn')
		_region_name_column_keyword = kwargs.get('regionNameColumn')
		_series_code_column_keyword = kwargs.get('seriesCodeColumn', kwargs.get('subjectCodeColumn'))
		_series_name_column_keyword = kwargs.get('seriesNameColumn', kwargs.get('subjectNameColumn'))

		# Check if any of the column keywords is overridden by kwargs.

		if _region_code_column_keyword:
			region_code_column = _region_code_column_keyword

		if _region_name_column_keyword:
			region_name_column = _region_name_column_keyword

		if _series_code_column_keyword:
			series_code_column = _series_code_column_keyword

		if _series_name_column_keyword:
			series_name_column = _series_name_column_keyword

		series_note_map = kwargs.get('seriesNoteMap')
		series_tag_map = kwargs.get('seriesTagMap')
		series_description_map = kwargs.get('seriesDescriptionMap')
		series_scale_map = kwargs.get('seriesScaleMap')
		series_unit_map = kwargs.get('seriesUnitMap')

		if series_note_map:
			series_note_column = series_note_map

		if series_tag_map:
			series_tag_column = series_tag_map

		if series_description_map:
			series_description_column = series_description_map

		if series_scale_map:
			series_scale_column = series_scale_map
		if series_unit_map:
			series_unit_column = series_unit_map

		column_config = {
			'regionCodeColumn':        region_code_column,
			'regionNameColumn':        region_name_column,
			'seriesCodeColumn':        series_code_column,
			'seriesNameColumn':        series_name_column,

			'seriesNoteColumn':        series_note_column,
			'seriesTagColumn':         series_tag_column,
			'seriesDescriptionColumn': series_description_column,
			'seriesScaleColumn':       series_scale_column,
			'seriesUnitColumn':        series_unit_column,

			'seriesNoteMap':           series_note_map,
			'seriesTagMap':            series_tag_map,
			'seriesDescriptionMap':    series_description_map,
			'seriesScaleMap':          series_scale_map,
			'seriesUnitMap':           series_unit_map
		}

		return column_config

	def _parseTable(self, table, **kwargs):
		""" Imports a spreadsheet into the database.
			Parameters
			----------
			filename: str, tabletools.Table, pandas.DataFrame
				The file path of the table to import. Should be compatible with tabletools.Table.




		"""

		# Get the relevant columns for the data.

		report_columns = self._getColumnNames(table.columns, **kwargs)
		# pprint(report_columns)
		api_table = list()
		print("Converting the table into a compatible json format...")

		region_groups = table.groupby(by = report_columns['regionCodeColumn'])
		index = 0
		pbar = progressbar.ProgressBar(max_value = len(region_groups))
		for region_code, region_group in region_groups:
			index += 1
			pbar.update(index)

			report_region = self._parseRegion(region_code, region_group, report_columns, **kwargs)
			api_table.append(report_region)

		return api_table

	def _parseRegion(self, region_code, region_group, columns, **kwargs):
		"""
			Parses all rows belonging to a single region from a table.
		Parameters
		----------
		region_code: str
		region_group: pandas.DataFrame
		columns: dict<>
		kwargs

		Returns
		-------
		dict<>
			* 'regionName': str
			* 'regionCode': str
			* 'regionSeries': list<dict<>>
		"""
		region_series = list()
		region_name = region_group[columns['regionNameColumn']].values[0]
		for index, row in region_group.iterrows():

			current_series = self._convertRow(row, columns, **kwargs)

			if current_series and len(current_series['seriesValues']) != 0:
				region_series.append(current_series)

		region_information = {
			'regionName':    region_name,
			'regionCode':    region_code,
			'regionType':   'country',
			'regionSeries': region_series
		}

		return region_information

	def _convertRow(self, row, report_columns, **kwargs):
		""" Converts a row into an importable dict.
			Parameters
			----------
			row: dict, pandas.Series
			report_columns: dict

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
		whitelist = kwargs.get('whitelist', [])

		# Should be static
		try:
			region_code = row[report_columns['regionCodeColumn']]  # identifier
			region_name = row[report_columns['regionNameColumn']]

			subject_code = row[report_columns['seriesCodeColumn']]
			subject_name = row[report_columns['seriesNameColumn']]
		except KeyError as exception:
			error_message = {
				'exception':        exception,
				'exceptionMessage': str(exception),
				'parameters':       {
					'row':            row,
					'report_columns': report_columns,
					'kwargs':         kwargs
				}
			}
			pprint(error_message)
			raise exception

		_in_whitelist = len(whitelist) != 0 or subject_code in whitelist
		_not_in_blacklist = len(whitelist) == 0 and subject_code not in blacklist
		use_row = _in_whitelist or _not_in_blacklist

		if use_row:

			series_code_column = report_columns.get('seriesCodeColumn')
			series_code = row[series_code_column]

			series_unit_map = report_columns.get('seriesUnitColumn')
			if not series_unit_map:
				series_unit_map = report_columns.get('seriesUnitMap')

			series_scale_map = report_columns.get('seriesScaleColumn')
			if not series_scale_map:
				series_scale_map = report_columns.get('seriesScaleMap')

			series_tag_map = report_columns.get('seriesTagColumn')
			if not series_tag_map:
				series_tag_map = report_columns.get('seriesTagMap')

			series_note_map = report_columns.get('seriesNoteColumn')
			if not series_note_map:
				series_note_map = report_columns.get('seriesNoteMap')

			series_description_map = report_columns.get('seriesDescriptionColumn')
			if not series_description_map:
				series_description_map = report_columns.get('seriesDescriptionMap')

			series_units = self._getMetadata(row, series_unit_map, series_code)
			series_scale = self._getMetadata(row, series_scale_map, series_code)
			series_tags = self._getMetadata(row, series_tag_map, series_code)
			series_notes = self._getMetadata(row, series_note_map, series_code, region_code)
			series_description = self._getMetadata(row, series_description_map, series_code)

			if series_tags is None:
				series_tags = []
			elif isinstance(series_tags, str):
				series_tags = series_tags.split('|')
			if series_scale is None:
				series_scale = 'unit'
			if series_notes is None:
				series_notes = ''

			series_values = self._getValues(row, kwargs['startDay'], kwargs['jsonCompatible'])

			json_series = {
				'regionCode':        region_code,
				'regionName':        region_name,
				'seriesName':        subject_name,
				'seriesCode':        subject_code,
				'seriesScale':       series_scale,

				'seriesNotes':       series_notes,
				'seriesDescription': series_description,
				'seriesTags':        series_tags,
				'seriesUnits':       series_units,
				'seriesValues':      series_values
			}
		else:
			json_series = None


		return json_series

	@staticmethod
	def _getValues(row, start_day, json_compatible):
		""" Dates may take to following formats:
			* int, float: ex. 2017, 2017.0
			* str ex. '2017', '2017-03-21'
			* datetime object
		"""
		year_columns, _ = tables.separateTableColumns(row.keys())

		# Check if the years include date information.
		fy = year_columns[0]

		if isinstance(fy, (int, float)) or (isinstance(fy, str) and fy.isdigit()):
			values = [(str(int(y)) + '-' + start_day, row[y]) for y in year_columns]
		else:
			values = [(y, row[y]) for y in year_columns]

		values = [(i, numbertools.toNumber(j)) for i, j in values]
		values = [(timetools.Timestamp(i), j) for i, j in values if not isnan(j)]

		if json_compatible:
			values = [(i.toIso(), j) for i, j in values]
		return values

	@staticmethod
	def _getMetadata(row, metadata_map, subject_code, region_code = None):
		"""
			Extracts metadata from the row.
		Parameters
		----------
		row: pandas.Series
			The row to extract metadata from.
		metadata_map: str, dict<>
			The label of the column containing the desired metadata or a dictionary mapping the
			series code to metadata values.
		subject_code: str
		region_code: str; default None

		Returns
		-------
			str
		"""


		if isinstance(metadata_map, str) and metadata_map in row.keys():
			metadata_value = row[metadata_map]
		elif isinstance(metadata_map, dict):
			if region_code:
				metadata_key = region_code + '|' + subject_code
			else:
				metadata_key = subject_code
			metadata_value = metadata_map.get(metadata_key)
		else:
			error_message = {
				'parameters': {
					'metadata_map': metadata_map,
					'subject_column': subject_code,
					'row': row.keys()
				}
			}
			pprint(error_message)
			raise ValueError
		if isinstance(metadata_value, float) and isnan(metadata_value):
			metadata_value = None
		return metadata_value