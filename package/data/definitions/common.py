agencies = [
	{
		'code': "IMF",
		'name': "International Monetary Fund",
		'url': "http://www.imf.org/external/index.htm|http://www.imf.org/en/data",
		#'wiki': "https://en.wikipedia.org/wiki/International_Monetary_Fund",
		'address': "700 19th Street, N.W., Washington, D.C. 20431|1900 Pennsylvania Ave NW, Washington, DC, 20431"
	},

	{
		'code': 'CEN',
		'name': "United States Census Bureau",
		'url': "https://www.census.gov",
		#'wiki': "https://en.wikipedia.org/wiki/United_States_Census_Bureau",
		'address': "4600 Silver Hill Road, Washington, DC 20233"
	},

	{
		'code': 'WB',
		'name': 'World Bank',
		'url': "http://data.worldbank.org",
		#'wiki': "https://en.wikipedia.org/wiki/World_Bank"
		'address': "1818 H Street, NW Washington, DC 20433 USA"
	},


	{
		'code': 'ISO',
		'name': 'International Organization for Standardization',
		'url': 'https://www.iso.org/home.html',
		#'wiki': "https://en.wikipedia.org/wiki/International_Organization_for_Standardization"
	},


	{
		'code': 'IATA',
		'name': 'International Air Transport Association',
		'url': "http://www.iata.org/Pages/default.aspx",
		#'wiki': "https://en.wikipedia.org/wiki/International_Air_Transport_Association"
	},

	{
		'code': 'EUR',
		'name': 'Eurostat',
		'url': "http://ec.europa.eu/eurostat"
	},

	{
		'code': 'UN',
		'name': 'United Nations',
		'url' : 'http://www.un.org/en/index.html',
		'address': "902 Broadway, 4th Floor New York, NY 10010"
	}
]

namespaces = [
	{
		'code': 	'ISO',
		'name': 	'ISO 3166-1',
		'subTypes': 'alpha-2,alpha-3,numeric',
		'regex': 	"(?P<iso3>[A-Z]{3})|(?P<iso2>[A-Z]{2})|(?P<numeric>[0-9]{3})",
		'url': 		'https://www.iso.org/iso-3166-country-codes.html',
		'wiki': 	'https://en.wikipedia.org/wiki/ISO_3166-1',
		'agency': 	'International Organization for Standardization'
	},
	{
		'code': 	'NUTS',
		'name': 	"Classification of Territorial Units for Statistics",
		'subTypes': "NUTS-1,NUTS-2,NUTS-3",
		'regex': 	"(?P<nuts-1>[A-Z]{2}[0-9A-N])|(?P<nuts-2>[A-Z]{2}[0-9A-N]{2})|(?P<nuts-3>[A-Z]{2}[0-9A-N]{3}",
		'url': 		"http://ec.europa.eu/eurostat/web/nuts/overview",
		'wiki': 	"https://en.wikipedia.org/wiki/Nomenclature_of_Territorial_Units_for_Statistics",
		'agency': 	'EUR'
	},
	{
		'code': 'FIPS',
		'name': "Federal Information Processing Standards",
		'regex': "(?P<state>[\d]{2})(?P<county>[\d]{3})",
		'url': "https://www.census.gov/geo/reference/codes/cou.html",
		'wiki': "https://en.wikipedia.org/wiki/Federal_Information_Processing_Standards",
		'agency': "FED"
	},
	{
		'code': 'IATA',
		'name': "International Air Transport Association",
		'url': "http://iatacodes.org",
		'wiki': "https://en.wikipedia.org/wiki/International_Air_Transport_Association_airport_code",
		'agency': "IATA"
	}
	
]

files = [
	("namespaces\\country-codes.xlsx", 'ISO'),
	("namespaces\\NUTS2013-NUTS2016.xls", 'NUTS'),
	("namespaces\\fips_codes_website.xls)", 'FIPS'),
	("Global\\World Economic Outlook April 2017.xlsx", 'WEO', 'World Economic Outlook'),
	("Global\\World Development Indicators\\WDIEXCEL.xlsx", "WDI", "World Development Indicators"),
	("Global\\Population\\UN World Population Prospects, 2017\\WPP2017_POP_F01_1_TOTAL_POPULATION_BOTH_SEXES.xlsx", 'WPP2017', 'World Population Prospects, 2017'),
	("Global\\Population\\UN World Population Prospects, 2015\\tabula-WPP2015_Volume-I_Comprehensive-Tables.xlsx", 'WPP2015', 'World Population Prospects, 2015 Revision')
]

ignore = [
	# World Economic Outlook series to ignore.
	'NGDP_RPCH', 'NGDP_R', 'NGDP_D', 'PPPSH', 'NID_NGDP',
	'NGSD_NGDP','PCPI','PCPIPCH', 'PCPIE', 'PCPIEPCH', 
	'GGSB', 'GGSB_NPGDP', 'GGXONLB', 'GGXONLB_NGDP', 'BCA', 
	'BCA_NGDPD'
]