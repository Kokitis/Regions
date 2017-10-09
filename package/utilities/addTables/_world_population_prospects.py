import pandas

from functools import partial

from ..definitions import getDefinition
from ...github import tabletools
from .._converters import ConvertTable

def addWorldPopulationProspects(dataset, variant = 2017):
	variant = str(variant)
	if variant == '2017':
		result = _addWorldPopulationProspects2017(dataset) 
	elif variant == '2015':
		result = _addWorldPopulationProspects2015(dataset)
	else:
		message = "Incorect variant provided for 'WPP': '{}'".format(variant)
		raise ValueError(message)
	return result

def _addWorldPopulationProspects2017(dataset):
	import re
	filename = getDefinition('file', 'WPP2017')
	# For reference

	subject_keymap = {
		'ESTIMATES':            'POP.EST',
		'MEDIUM VARIANT':       'POP.PROJ.MID',
		'HIGH VARIANT':         'POP.PROJ.MAX',
		'LOW VARIANT':          'POP.PROJ.MIN',
		'CONSTANT-FERTILITY':   'POP.PROJ.CONST.FERT',
		'ZERO-MIGRATION':       'POP.PROJ.ZERO',
		'NO CHANGE':            'POP.PROJ.STATIC',
		'MOMENTUM':             'POP.PROJ.MOM',
		'INSTANT-REPLACEMENT':  'POP.PROJ.INST',
		'CONSTANT-MORTALITY':   'POP.PROJ.CONST.MORT'
	}

	table_dict = pandas.read_excel(filename, sheetname = None, skiprows = 16) #Creates a dict of dataframes.
	table_dict.pop('NOTES')
	notes_table = tabletools.Table(filename, sheetname = 'NOTES')
	print("Extracting notes...")
	notes_dict = dict()

	for row in notes_table:
		regex = re.compile("[(](?P<num>.*)[)](?P<char>.*)")
		match = regex.search(row[0])
		if match:
			match = match.groupdict()
			#print(match)
			notes_dict[match['num']] = match['char'].strip()

	print("Configuring table...")

	for subject_name, sheet in table_dict.items():
		#print(subject_name, '\t', sheet.columns)
		sheet.columns = [(i[1:] if i.startswith("'") else i) for i in sheet.columns]
		subject_code = subject_keymap[subject_name]
		notes_values = sheet['Notes'].values
		sheet['subjectCode'] = [subject_code for _ in notes_values]
		sheet['subjectName'] = [subject_name for _ in notes_values]
		sheet['seriesNotes'] = [(notes_dict.get(i) if isinstance(i, str) else None) for i in notes_values]
		sheet['regionCode']  = ["{:>03}".format(i) for i in sheet['Country code'].values]

	print("Combining table...")
	full_table = pandas.concat(table_dict.values())

	_series_scale_map = lambda *s: 'Thousand'
	_series_unit_map = lambda *s: 'Persons'

	_series_description_map = {
		'POP.PROJ.MID':
			"""Medium fertility variant, 2015 - 2100|"""
			"""Total fertility in high-fertility countries is generally assumed to decline at an average pace of nearly one child per decade starting in 2005 or later. """
			"""Consequently, some of these countries do not reach replacement level by 2050. """
			"""Total fertility in medium-fertility countries is assumed to reach replacement level before 2050. """
			"""Total fertility in low-fertility countries is generally assumed to remain below the replacement level during the projection period, """
			"""reaching by 2045-2050 the total fertility of the cohort of women born in the early 1960s or, if """
			"""that information is lacking, reaching 1.7 children per woman if current total fertility is below 1.5 children per woman or 1.9 children """
			"""per woman if current total fertility is equal or higher than 1.5 children per woman.""",
		'POP.PROJ.MAX':
			"""High fertility variant, 2015 - 2100|"""
			"""Total fertility in high and medium-fertility countries remains above the total fertility in """
			"""the medium-fertility assumption and eventually reaches a value 0.5 children above that """
			"""reached by total fertility in the mediumfertility assumption in 2045-2050. """
			"""For low-fertility countries, total fertility eventually reaches a value 0.4 children above that """
			"""reached by total fertility in the mediumfertility assumption in 2045-2050.""",
		'POP.PROJ.MIN':
			"""Low fertility variant, 2015 - 2100|"""
			"""Total fertility in high and medium-fertility countries remains below the total fertility in """
			"""the medium-fertility assumption and eventually reaches a value 0.5 children below that """
			"""reached by total fertility in the mediumfertility assumption in 2045-2050. """
			""" For low-fertility countries, total fertility eventually reaches a value 0.4 children below that """
			""" reached by total fertility in the mediumfertility assumption in 2045-2050. """,
		'POP.PROJ.CONST.FERT': "Constant-fertility variant, 2015 - 2100|For each country, total fertility remains constant at the level estimated for 1995-2000.",
		'POP.PROJ.INST':
			"""Instant-replacement-fertility variant, 2015 - 2100|"""
			"""For each country and each quinquennium of the """
			"""projection period (2000-2050), total fertility is set """
			"""to a level that ensures a net reproduction rate of """
			"""one. That is, total fertility is set to the level that """
			"""would ensure population replacement in the long """
			"""run in light of the sex ratio at birth and level of """
			"""mortality of the country concerned at each particular period.""",
		'POP.PROJ.ZERO': "Zero-migration variant, 2015 - 2100|For each country, international migration is set to zero for the period 2000-2050.",
		'POP.PROJ.MOM': "Momentum variant (instant-replacement-fertility, constant-mortality and zero-migration), 2015 - 2100",
		'POP.PROJ.STATIC': "No change variant (constant-fertility and constant-mortality), 2015 - 2100",
		'POP.PROJ.CONST.MORT': "Constant-mortality variant, 2015 - 2100"
	}

	def _series_desc_map_func_mapper(mapper, region_code, sc):
		return mapper.get(sc)

	_series_desc_map_func = partial(_series_desc_map_func_mapper, _series_description_map)

	report = {
		'name': "World Population Prospects, The 2017 Revision",
		'code': "WPP2017",
		'agency': 'United Nations',
		'publishDate': "2017-06-21",
		'retrieved_date': "2017-09-27",
		'url': "https://esa.un.org/unpd/wpp/Download/Standard/Population/"
	}


	configuration = {
		'seriesNameColumn': 'subjectName',
		'seriesCodeColumn': 'subjectCode',
		'regionCodeColumn': 'regionCode',
		'regionNameColumn': 'Region, subregion, country or area *',

		'namespace': 'ISO',

		'unitMap': _series_unit_map,
		'scaleMap': _series_scale_map,
		'descriptionMap': _series_desc_map_func
	}

	ConvertTable(dataset, full_table, report = report, **configuration)
	return None

def _addWorldPopulationProspects2015(dataset):
	
	filename = getDefinition('file', 'WPP2015')
	#print(filename)
	table_dict = pandas.read_excel(filename, sheetname = None)
	full_table = pandas.concat(table_dict.values())
	#print(full_table.columns)
	#return full_table

	report = {
		'name': "World Population Prospects, The 2015 Revision",
		'code': "WPP2015",
		'agency': 'UN',
		'publishDate': "2015-06-29",
		'retrievedDate': "2017-09-27",
		'url': "http://www.un.org/en/development/desa/publications/world-population-prospects-2015-revision.html"
	}

	configuration = {
		'namespace': 'ISO',
		'subjectNameColumn': 'subjectName',
		'subjectCodeColumn': 'subjectCode',
		'regionNameColumn': 'regionName',
		'regionCodeColumn': 'regionCode'
	}

	ConvertTable(dataset, full_table, report = report, **configuration)
	return None

