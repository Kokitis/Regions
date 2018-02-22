from .validation import parseKeywords
def isNumber(value):
	""" Checks if a value is a numeric type or if all characters in the string are digits.
		Parameters
		----------
			value: int, float, str
	"""
	is_numeric_type = isinstance(value, (int, float))
	is_all_digit = is_numeric_type or (isinstance(value, str) and value.isdigit())
	return is_all_digit
def separateTableColumns(columns):
	""" Separates a list of columns into 'years' and 'other'
		Parameters
		----------
			columns: list<str,int>
				The column list. Year columns may be represented
				by either number or strings of numeric digits.
		Returns
		-------
			years, other_columns
	"""
	years = [i for i in columns if isNumber(i)]
	other_columns = [i for i in columns if i not in years]
	return years, other_columns

def _getColumnName(columns, keys):
	if len(keys) == 0:
		return None
	elif len(keys) == 1:
		return keys[0] if keys[0] in columns else None
	elif keys[0] in columns:
		return keys[0]
	else:
		return _getColumnName(columns, keys[1:])


def getRequiredColumns(table_columns, **kwargs):
	""" Attempts to retrieve the required columns that are needed
		to import a table into the database. 
		Parameters
		----------
			table_columns: list<>
		Keyword Arguments
		-----------------
			* 'regionCodeColumn'
			* 'regionNameColumn'
			* 'seriesCodeColumn'
			* 'seriesNameColumn'
			* 'seriesNoteColumn'
			* 'unitNameColumn'
			* 'unitCodeColumn'
			* 'scaleColumn'
			* 'seriesDescriptionColumn'

	"""
	region_code_column = parseKeywords(
		table_columns, 
		[
			'regionCode', 'countryCode', 'isoCode', 'fipsCode', 'stateCode', kwargs.get('regionCodeColumn')
		],
		return_type = 'column'
	)

	region_name_column = parseKeywords(
		table_columns, 
		[
			'regionName', 'countryName', 'state', 'countyName', 'cityName', kwargs.get('regionNameColumn')
		], 
		return_type = 'column'
		
	)

	series_code_column = parseKeywords(
		table_columns, 
		[
			'seriesCode', 'subjectCode', 'variable', 'subjectCodeColumn', 'subjectCodeColumn', 'seriesCodeColumn', kwargs.get('seriesCodeColumn')
		], 
		return_type = 'column'
	)

	series_name_column = parseKeywords(
		table_columns, 
		[
			'seriesName', 'subjectName', 'subjectNameColumn', 'seriesNameColumn', kwargs.get('seriesNameColumn')
		], 
		return_type = 'column'
	)
	
	series_note_column = parseKeywords(
		table_columns, 
		[
			'notes', 'subjectNotes', 'seriesNotes', kwargs.get('seriesNoteColumn')
		], 
		return_type =  'column'
	)

	series_scale_column = parseKeywords(
		table_columns, 
		[
			'scale', 'multiplier', 'seriesScale', kwargs.get('scaleColumn')
		], 
		return_type = 'column'
	)
	
	series_unit_name_column  = parseKeywords(
		table_columns, 
		[
			'units', 'unit', 'Unit', 'Units', 'seriesUnit', 
			'seriesUnits', 'subjectUnits', 'subjectUnit', kwargs.get('unitNameColumn')
		], 
		return_type = 'column'
	)

	series_unit_code_column = parseKeywords(
		table_columns,
		[
			'unitCode', 'seriesUnitCode', kwargs.get('unitCodeColumn')
		],
		return_type = 'column'
	)

	series_description_column = parseKeywords(
		table_columns,
		[
			'seriesDescription', 'subjectDescription', 'description', kwargs.get('seriesDescriptionColumn')
		],
		return_type = 'column'

	)

	series_tag_column = parseKeywords(
		table_columns,
		[
			'seriesTags', 'subjectTags', 'tags'
		],
		return_type = 'column'
	)

	result = {
		'regionCodeColumn': region_code_column,
		'regionNameColumn': region_name_column,
		'seriesCodeColumn': series_code_column,
		'seriesNameColumn': series_name_column,
		'seriesNoteColumn': series_note_column,
		'seriesScaleColumn': series_scale_column,
		'seriesUnitNameColumn': series_unit_name_column,
		'seriesUnitCodeColumn': series_unit_code_column,
		'seriesDescriptionColumn': series_description_column,
		'seriesTagColumn': series_tag_column
	}

	return result