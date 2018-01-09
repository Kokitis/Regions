""" Contains default configurations for common tables used in the database such as
	the World Economic Outlook and Word Development Indicators
"""
from ._world_population_prospects import addWorldPopulationProspects
from ._add_world_development_indcators import _addWorldDevelopmentIndicators
from ._add_world_economic_outlook import _addWorldEconomicOutlook

def addReport(dataset, string, filename):
	""" Adds the selected report to the dataset. """

	if string in {'WEO', 'World Economic Outlook'}:
		result = _addWorldEconomicOutlook(dataset, filename)
	elif string in {'WDI', 'World Development Indicators'}:
		result = _addWorldDevelopmentIndicators(dataset, filename)
	elif string.startswith('WPP'):
		result = addWorldPopulationProspects(dataset, filename)
	else:
		message = "Incorrect report key: '{}'".format(string)
		raise ValueError(message)
	return result

def _defaultMadisonHistoricalTables():
	pass

