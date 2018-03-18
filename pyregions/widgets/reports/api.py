import pathlib
import pandas
from pyregions.widgets import TableApi


def getMaddisonConfiguration():
	#configuration_filename = getFilename('maddison_historical_data_configuration')
	#configuration = loadConfiguration(configuration_filename)
	configuration = None
	if configuration is None:
		report = {
			'reportName': 'Historical Statistics of the World Economy:  1-2008 AD',
			'reportCode': 'MADDISONPOP',
			'reportDate': '2008-09-08',
			'reportUrl':  'http://www.ggdc.net/maddison/oriindex.htm'
		}

		agency = {
			'agencyName':    'University of Groningen',
			'agencyCode':    '',
			'agencyUrl':     'https://www.rug.nl',
			'agencyAddress': 'University of Groningen PO Box 72 9700 AB Groningen'
		}

		configuration = {
			'report':         report,
			'agency':         agency,
			'namespace':      'ISO',
			'seriesTagMap':   {'POP': ['POP']},
			'jsonCompatible': False,
			'yearRange':      (1820, None),
			'tableConfig':    {
				'skiprows':  2,
				'sheetname': 'Population'
			}
		}
		#saveConfiguration(configuration, configuration_filename)

	return configuration


def generateMaddisonResponse(filename: str):
	configuration = getMaddisonConfiguration()
	code_map = configuration['regionCodeMap']
	population_table = pandas.read_excel(filename, sheetname = 'Population', skiprows = 2)
	population_table.columns = ['regionName'] + population_table.columns[1:]
	gdp_table = pandas.read_excel(filename, sheetname = 'GDP', skiprows = 2)
	gdp_table.columns = ['regionName'] + gdp_table.columns[1:]
	capita_table = pandas.read_excel(filename, sheetname = 'PerCapita GDP', skiprows = 2)
	capita_table.columns = ['regionName'] + capita_table.columns[1:]


	population_table['seriesUnits'] = 'persons'


	gdp_table['seriesUnits'] = '1990 International Geary-Khamis dollars '
	gdp_table['seriesScale'] = 'million'


	capita_table['seriesUnits'] = '1990 International Geary-Khamis dollars'

	full_table: pandas.DataFrame = pandas.concat([population_table, gdp_table, capita_table])

	api_response = TableApi(full_table, **configuration)


if __name__ == "__main__":
	fname = pathlib.Path()
