import pathlib
import pandas
from pyregions.widgets import TableApi


def getMaddisonConfiguration():
	# configuration_filename = getFilename('maddison_historical_data_configuration')
	# configuration = loadConfiguration(configuration_filename)
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
			},
			'regionCodeMap':  {
				"Austria":                                       "AUT",
				"Belgium":                                       "BEL",
				"Denmark":                                       "DNK",
				"Finland":                                       "FIN",
				"France":                                        "FRA",
				"Germany":                                       "DEU",
				"Italy":                                         "ITA",
				"Netherlands":                                   "NLD",
				"Norway":                                        "NOR",
				"Sweden":                                        "SWE",
				"Switzerland":                                   "CHE",
				"United Kingdom":                                "GBR",
				"Ireland":                                       "IRL",
				"Greece":                                        "GRC",
				"Portugal":                                      "PRT",
				"Spain":                                         "ESP",
				"Australia":                                     "AUS",
				"New Zealand":                                   "NZL",
				"Canada":                                        "CAN",
				"United States":                                 "USA",
				"Albania":                                       "ALB",
				"Bulgaria":                                      "BGR",
				"Hungary":                                       "HUN",
				"Poland":                                        "POL",
				"Romania":                                       "ROU",
				"Bosnia":                                        "BIH",
				"Croatia":                                       "HRV",
				"Macedonia":                                     "MKD",
				"Slovenia":                                      "SVN",
				"Serbia/Montenegro/Kosovo":                      "UVK",
				"Czech Republic":                                "CZE",
				"Slovakia":                                      "SVK",
				"Armenia":                                       "ARM",
				"Azerbaijan":                                    "AZE",
				"Belarus":                                       "BLR",
				"Estonia":                                       "EST",
				"Georgia":                                       "GEO",
				"Kazakhstan":                                    "KAZ",
				"Kyrgyzstan":                                    "KGZ",
				"Latvia":                                        "LVA",
				"Lithuania":                                     "LTU",
				"Moldova":                                       "MDA",
				"Russian Federation":                            "RUS",
				"Tajikistan":                                    "TJK",
				"Turkmenistan":                                  "TKM",
				"Ukraine":                                       "UKR",
				"Uzbekistan":                                    "UZB",
				"Total Former USSR":                             "SUN",
				"Argentina":                                     "ARG",
				"Brazil":                                        "BRA",
				"Chile":                                         "CHL",
				"Colombia":                                      "COL",
				"Mexico":                                        "MEX",
				"Peru":                                          "PER",
				"Uruguay":                                       "URY",
				"Venezuela":                                     "VEN",
				"Bolivia":                                       "BOL",
				"Costa Rica":                                    "CRI",
				"Cuba":                                          "CUB",
				"Dominican Republic":                            "DOM",
				"Ecuador":                                       "ECU",
				"El Salvador":                                   "SLV",
				"Guatemala":                                     "GTM",
				"Haïti":                                         "HTI",
				"Honduras":                                      "HND",
				"Jamaica":                                       "JAM",
				"Nicaragua":                                     "NIC",
				"Panama":                                        "PAN",
				"Paraguay":                                      "PRY",
				"Puerto Rico":                                   "PRI",
				"Trinidad and Tobago":                           "TTO",
				"China":                                         "CHN",
				"India":                                         "IND",
				"Indonesia (including Timor until 1999)":        "IDN",
				"Japan":                                         "JPN",
				"Philippines":                                   "PHL",
				"South Korea":                                   "KOR",
				"Thailand":                                      "THA",
				"Taiwan":                                        "TWN",
				"Bangladesh":                                    "BGD",
				"Hong Kong":                                     "HKG",
				"Malaysia":                                      "MYS",
				"Nepal":                                         "NPL",
				"Pakistan":                                      "PAK",
				"Singapore":                                     "SGP",
				"Sri Lanka":                                     "LKA",
				"Afghanistan":                                   "AFG",
				"Cambodia":                                      "KHM",
				"Mongolia":                                      "MNG",
				"North Korea":                                   "PRK",
				"Vietnam":                                       "VNM",
				"Bahrain":                                       "BHR",
				"Iran":                                          "IRN",
				"Iraq":                                          "IRQ",
				"Israel":                                        "ISR",
				"Jordan":                                        "JOR",
				"Kuwait":                                        "KWT",
				"Lebanon":                                       "LBN",
				"Oman":                                          "OMN",
				"Qatar":                                         "QAT",
				"Saudi Arabia":                                  "SAU",
				"Syria":                                         "SYR",
				"Turkey":                                        "TUR",
				"United Arab Emirates":                          "ARE",
				"Yemen":                                         "YEM",
				"Algeria":                                       "DZA",
				"Angola":                                        "AGO",
				"Benin":                                         "BEN",
				"Botswana":                                      "BWA",
				"Burkina Faso":                                  "BFA",
				"Burundi":                                       "BDI",
				"Cameroon":                                      "CMR",
				"Central African Republic":                      "CAF",
				"Chad":                                          "TCD",
				"Congo 'Brazzaville'":                           "COG",
				"Côte d'Ivoire":                                 "CIV",
				"Djibouti":                                      "DJI",
				"Egypt":                                         "EGY",
				"Equatorial Guinea":                             "GNQ",
				"Gabon":                                         "GAB",
				"Gambia":                                        "GMB",
				"Ghana":                                         "GHA",
				"Guinea":                                        "GIN",
				"Guinea Bissau":                                 "GNB",
				"Kenya":                                         "KEN",
				"Lesotho":                                       "LSO",
				"Liberia":                                       "LBR",
				"Libya":                                         "LBY",
				"Madagascar":                                    "MDG",
				"Malawi":                                        "MWI",
				"Mali":                                          "MLI",
				"Mauritania":                                    "MRT",
				"Mauritius":                                     "MUS",
				"Morocco":                                       "MAR",
				"Mozambique":                                    "MOZ",
				"Namibia":                                       "NAM",
				"Niger":                                         "NER",
				"Nigeria":                                       "NGA",
				"Rwanda":                                        "RWA",
				"São Tomé and Principe":                         "STP",
				"Senegal":                                       "SEN",
				"Seychelles":                                    "SYC",
				"Sierra Leone":                                  "SLE",
				"Somalia":                                       "SOM",
				"South Africa":                                  "ZAF",
				"Sudan":                                         "SDN",
				"Swaziland":                                     "SWZ",
				"Tanzania":                                      "TZA",
				"Togo":                                          "TGO",
				"Tunisia":                                       "TUN",
				"Uganda":                                        "UGA",
				"Zaire (Congo Kinshasa)":                        "COG",
				"Zambia":                                        "ZMB",
				"Zimbabwe":                                      "ZWE",
				"Andorra":                                       "AND",
				"Cyprus":                                        "CYP",
				"Faeroe Islands":                                "FRO",
				"Gibraltar":                                     "GIB",
				"Greenland":                                     "GRL",
				"Guernsey":                                      "GGY",
				"Iceland":                                       "ISL",
				"Isle of Man":                                   "IMN",
				"Jersey":                                        "JEY",
				"Liechtenstein":                                 "LIE",
				"Luxembourg":                                    "LUX",
				"Malta":                                         "MLT",
				"Monaco":                                        "MCO",
				"San Marino":                                    "SMR",
				"Anguilla":                                      "AIA",
				"Antigua & Barbuda":                             "ATG",
				"Aruba":                                         "ABW",
				"Bahamas":                                       "BHS",
				"Barbados":                                      "BRB",
				"Belize":                                        "BLZ",
				"Bermuda":                                       "BMU",
				"British Virgin Islands":                        "VGB",
				"Cayman Islands":                                "CYM",
				"Dominica":                                      "DMA",
				"Grenada":                                       "GRD",
				"Guyana":                                        "GUY",
				"Montserrat":                                    "MSR",
				"St. Pierre and Miquelon":                       "SPM",
				"St. Vincent (and the grenadines)":              "VCT",
				"Suriname":                                      "SUR",
				"Turks and Caicos Islands":                      "TCA",
				"Virgin Islands":                                "VGB",
				"Bhutan":                                        "BTN",
				"Brunei":                                        "BRN",
				"Cook Islands":                                  "COK",
				"East Timor (included in Indonesia until 1999)": "IDN",
				"Maldives":                                      "MDV",
				"Fiji":                                          "FJI",
				"Papua New Guinea":                              "PNG",
				"American Samoa":                                "ASM",
				"French Polynesia":                              "PYF",
				"Guam":                                          "GUM",
				"Kiribati":                                      "KIR",
				"Marshall Islands":                              "MHL",
				"Micronesia":                                    "FSM",
				"Nauru":                                         "NRU",
				"New Caledonia":                                 "NCL",
				"Northern Mariana Islands":                      "MNP",
				"Palau":                                         "PLW",
				"Samoa":                                         "WSM",
				"Solomon Islands":                               "SLB",
				"Tonga":                                         "TON",
				"Tuvalu":                                        "TUV",
				"Vanuatu":                                       "VUT",
				"Eritrea":                                       "ERI",
				"Ethiopia":                                      "ETH",
				"Mayotte":                                       "MYT",
				"Saint Helena":                                  "SHN",
				"Western Sahara":                                "ESH",
				"Guadeloupe":                                    "GLP",
				"Guyana (Fr.)":                                  "GUY",
				"Martinique":                                    "MTQ",
				"Reunion":                                       "REU",
			}

		}
	# saveConfiguration(configuration, configuration_filename)

	return configuration


def generateMaddisonResponse(filename: str):
	configuration = getMaddisonConfiguration()
	code_map = configuration['regionCodeMap']
	population_table = pandas.read_excel(filename, sheetname = 'Population', skiprows = 2)
	population_table.columns = ['regionName'] + list(population_table.columns)[1:]
	gdp_table = pandas.read_excel(filename, sheetname = 'GDP', skiprows = 2)
	gdp_table.columns = ['regionName'] + list(gdp_table.columns)[1:]
	capita_table = pandas.read_excel(filename, sheetname = 'PerCapita GDP', skiprows = 2)
	capita_table.columns = ['regionName'] + list(capita_table.columns)[1:]

	#population_table['regionCode'] = [code_map.get(i) for i in population_table['regionName'].values]
	population_table['seriesUnits'] = 'persons'
	population_table['seriesCode'] = 'POP'
	population_table['seriesName'] = 'Historical Population'

	#gdp_table['regionCode'] = [code_map.get(i) for i in gdp_table['regionName'].values]
	gdp_table['seriesCode'] = 'GDP'
	gdp_table['seriesName'] = 'Historical Gross Domestic Product'
	gdp_table['seriesUnits'] = '1990 International Geary-Khamis dollars '
	gdp_table['seriesScale'] = 'million'


	#capita_table['regionCode'] = [code_map.get(i) for i in capita_table['regionName'].values]
	capita_table['seriesCode'] = 'GDPPC'
	capita_table['seriesName'] = 'Historical Gross Domestic Product'
	capita_table['seriesUnits'] = '1990 International Geary-Khamis dollars'

	full_table: pandas.DataFrame = pandas.concat([population_table, gdp_table, capita_table], ignore_index = True)
	full_table['regionCode'] = [code_map.get(i) for i in full_table['regionName']]

	api_response = TableApi(full_table, **configuration)
	return api_response


if __name__ == "__main__":
	from pprint import pprint
	from functools import partial
	pprint = partial(pprint, width = 120)
	fname = r"C:\Users\Progi\Google Drive\Region Data\Global\Historical Datasets\horizontal-file_02-2010.xls"
	#fname = pathlib.Path(pathlib.Path.home())
	response = generateMaddisonResponse(fname)
	pprint(response)

