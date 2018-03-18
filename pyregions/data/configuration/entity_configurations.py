import os
DATA_FOLDER = os.path.dirname(os.path.dirname(__file__))
agencies = {
	"International Monetary Fund":                    {
		'code':    "IMF",
		'name':    "International Monetary Fund",
		'url':     "http://www.imf.org/external/index.htm|http://www.imf.org/en/data",
		# 'wiki': "https://en.wikipedia.org/wiki/International_Monetary_Fund",
		'address': "700 19th Street, N.W., Washington, D.C. 20431|1900 Pennsylvania Ave NW, Washington, DC, 20431"
	},
	"United States Census Bureau":                    {
		'code':    'CEN',
		'name':    "United States Census Bureau",
		'url':     "https://www.census.gov",
		# 'wiki': "https://en.wikipedia.org/wiki/United_States_Census_Bureau",
		'address': "4600 Silver Hill Road, Washington, DC 20233"
	},
	'World Bank':                                     {
		'code':    'WB',
		'name':    'World Bank',
		'url':     "http://data.worldbank.org",
		# 'wiki': "https://en.wikipedia.org/wiki/World_Bank"
		'address': "1818 H Street, NW Washington, DC 20433 USA"
	},

	'International Organization for Standardization': {
		'code': 'ISO',
		'name': 'International Organization for Standardization',
		'url':  'https://www.iso.org/home.html',
		# 'wiki': "https://en.wikipedia.org/wiki/International_Organization_for_Standardization"
	},

	'International Air Transport Association':        {
		'code': 'IATA',
		'name': 'International Air Transport Association',
		'url':  "http://www.iata.org/Pages/default.aspx",
		# 'wiki': "https://en.wikipedia.org/wiki/International_Air_Transport_Association"
	},
	'Eurostat':                                       {
		'code': 'EUR',
		'name': 'Eurostat',
		'url':  "http://ec.europa.eu/eurostat"
	},
	'United Nations':                                 {
		'code':    'UN',
		'name':    'United Nations',
		'url':     'http://www.un.org/en/index.html',
		'address': "902 Broadway, 4th Floor New York, NY 10010"
	}
}

namespaces = {
	'International Organization for Standardization':     {
		'code':     'ISO',
		'name':     'ISO 3166-1',
		'subTypes': 'alpha-2,alpha-3,numeric',
		'regex':    "(?P<iso3>[A-Z]{3})|(?P<iso2>[A-Z]{2})|(?P<numeric>[0-9]{3})",
		'url':      'https://www.iso.org/iso-3166-country-codes.html',
		'wiki':     'https://en.wikipedia.org/wiki/ISO_3166-1',
		'agency':   'International Organization for Standardization'
	},
	"Classification of Territorial Units for Statistics": {
		'code':     'NUTS',
		'name':     "Classification of Territorial Units for Statistics",
		'subTypes': "NUTS-1,NUTS-2,NUTS-3",
		'regex':    "(?P<nuts-1>[A-Z]{2}[0-9A-N])|(?P<nuts-2>[A-Z]{2}[0-9A-N]{2})|(?P<nuts-3>[A-Z]{2}[0-9A-N]{3}",
		'url':      "http://ec.europa.eu/eurostat/web/nuts/overview",
		'wiki':     "https://en.wikipedia.org/wiki/Nomenclature_of_Territorial_Units_for_Statistics",
		'agency':   'EUR'
	},
	"Federal Information Processing Standards":           {
		'code':   'FIPS',
		'name':   "Federal Information Processing Standards",
		'regex':  "(?P<state>[\d]{2})(?P<county>[\d]{3})",
		'url':    "https://www.census.gov/geo/reference/codes/cou.html",
		'wiki':   "https://en.wikipedia.org/wiki/Federal_Information_Processing_Standards",
		'agency': "FED"
	},
	"International Air Transport Association":            {
		'code':   'IATA',
		'name':   "International Air Transport Association",
		'url':    "http://iatacodes.org",
		'wiki':   "https://en.wikipedia.org/wiki/International_Air_Transport_Association_airport_code",
		'agency': "IATA"
	}

}

files = {
	'NUTS': "",
	'ISO Namespace': os.path.join(DATA_FOLDER, 'namespaces', 'country-codes.xlsx'),
	'USPS Namespace':os.path.join(DATA_FOLDER, 'namespaces', 'state_codes.xlsx')
}