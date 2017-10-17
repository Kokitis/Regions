nuts_codes  = [	"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", 
				"FR", "EL", "HU", "HR", "IE", "IT", "LT", "LU", "LV", "MT", 
				"NL", "PL", "PT", "RO", "SE", "SI", "SK", "UK", "AL", "MK", 
				"ME", "RS", "TR", "CH", "IS", "LI", "NO"]

state_codes = [	"AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
				"HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
				"MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
				"NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
				"SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", 
				"AS", "DC", "FM", "GU", "MH", "MP", "PW", "PR", "VI"]


composite_regions = {
	"The United Kingdom of Great Britain and Ireland": {
		"baseCode": "GBR",
		"description": "",
		"name": "United Kingdom of Great Britain and Ireland",
		"definition":{
			"GBR:1900": ["GBR", "IRL"]
		}
	},
	"European Union": {
		"baseCode": "EU",
		"description": "",
		"name": "European Union",
		"definition": {
			"EU:1958": ["BEL", "FRA", "ITA", "LUX", "NLD", "DEU"],
			
			"EU:1973": ["BEL", "FRA", "ITA", "LUX", "NLD", "DEU", "DNK", "IRL", "GBR"],
			
			"EU:1981": ["BEL", "FRA", "ITA", "LUX", "NLD", "DEU", "DNK", "IRL", "GBR", "GRC"],
			
			"EU:1986": [
				"BEL", "FRA", "ITA", "LUX", "NLD", "DEU", "DNK", "IRL", "GBR", "GRC", 
				"PRT", "ESP"
			],
			
			"EU:1995": [
				"BEL", "FRA", "ITA", "LUX", "NLD", "DEU", "DNK", "IRL", "GBR", "GRC", 
				"PRT", "ESP", "AUT", "FIN", "SWE"
			],
			
			"EU:2004": [
				"BEL", "FRA", "ITA", "LUX", "NLD", "DEU", "DNK", "IRL", "GBR", "GRC", 
				"PRT", "ESP", "AUT", "FIN", "SWE", "HUN", "CYP", "CZE", "EST", "LVA", 
				"LTU", "MLT", "POL", "SVK",	"SVN"
			],
			
			"EU:2007": [
				"BEL", "FRA", "ITA", "LUX", "NLD", "DEU", "DNK", "IRL", "GBR", "GRC", 
				"PRT", "ESP", "AUT", "FIN", "SWE", "HUN", "CYP", "CZE", "EST", "LVA", 
				"LTU", "MLT", "POL", "SVK",	"SVN", "BGR", "ROU"
			],
			
			"EU:2013": [
				"BEL", "FRA", "ITA", "LUX", "NLD", "DEU", "DNK", "IRL", "GBR", "GRC", 
				"PRT", "ESP", "AUT", "FIN", "SWE", "HUN", "CYP", "CZE", "EST", "LVA", 
				"LTU", "MLT", "POL", "SVK",	"SVN", "BGR", "ROU", "HRV"
			],
			"EU:2019": [
				"BEL", "FRA", "ITA", "LUX", "NLD", "DEU", "DNK", "IRL", "GRC", "PRT", 
				"ESP", "AUT", "FIN", "SWE", "HUN", "CYP", "CZE", "EST", "LVA", "LTU",
				"MLT", "POL", "SVK", "SVN", "BGR", "ROU", "HRV"
			]
		}
	},
	"German Empire": {
		"baseCode": "DEU",
		"description": "",
		"definition": {
			"DEU:1878": [
				"DEU", 
				"RUS-KGD", 
				"PL2&PL4&PL5&PL6|PL21&PL22&PL41&PL42&PL43&PL51&PL52&PL61&PL62&PL63",
				"DK03|DK032",
				"FR413&FR421&FR422"]
		},
		"name": "German Empire"
	}
}

UN_Geoschemes =  {
    'Northern America': ['USA', 'CAN', 'BMU', 'GRL', 'SPM'],
    'Central America': ['MEX', 'BLZ', 'CRI', 'SLV', 'GTM', 'HND', 'NIC', 'PAN'],
    'Caribbean': [
        'AIA', 'ATG', 'ABW', 'BHS', 'BRB', 'BES', 'VGB', 'CYM', 'CUB', 'CUW', 
        'DMA', 'DOM', 'GRD', 'GLP', 'HTI', 'JAM', 'MTQ', 'MSR', 'PRI', 
        'BLM', 'KNA', 'LCA', 'MAF', 'VCT', 'SXM', 'TTO', 'TCA', 'VIR'
    ],
    'South America': [
        'ARG', 'BOL', 'BVT', 'BRA', 'CHL', 'COL', 'ECU', 'FLK', 'GUF', 
        'GUY', 'PRY', 'PER', 'SGS', 'SUR', 'URY', 'VEN'
    ],
    'Eastern Europe': [
        'BLR', 'BGR', 'CZE', 'HUN', 'POL', 'MDA', 'ROU', 'RUS', 'SVK', 'UKR', 
    ],
    'Northern Europe': [
        'ALA', 'DNK', 'EST', 'FRO', 'FIN', 'GGY', 'ISL', 'IRL', 'IMN', 'JEY', 
        'LVA', 'LTU', 'NOR', 'SJM', 'SWE', 'GBR'
    ],
    'Southern Europe': [
        'ALB', 'AND', 'BIH', 'HRV', 'GIB', 'GRC', 'ITA', 'MKD', 'MLT', 'MNE', 
        'PRT', 'SMR', 'SRB', 'SVN', 'ESP'
    ],
    'Western Europe': [
         'AUT', 'BEL', 'FRA', 'DEU', 'LIE', 'LUX', 'MCO', 'NLD', 'CHE' 
    ],
    'Central Asia': ['KAZ', 'KGZ', 'TJK', 'TKM', 'UZB'],
    'Eastern Asia': ['CHN', 'TWN', 'HKG', 'JPN', 'MAC', 'MNG', 'PRK', 'PRK'],
    'Southern Asia': ['AFG', 'BGD', 'BTN', 'IND', 'IRN', 'MDV', 'NPL', 'PAK', 'LKA'],
    'Southeastern Asia': [ 'BRN', 'KHM', 'IDN', 'LAO', 'MYS', 'MMR', 'PHL', 'SGP', 'THA', 'TLS', 'VNM'],
    'Eastern Asia': [
        'ARM', 'AZE', 'BHR', 'CYP', 'GEO', 'IRQ', 'ISR', 'JOR', 'KWT', 'LBN', 
        'OMN', 'QAT', 'SAU', 'PSE', 'SYR', 'TUR', 'ARE', 'YEM'
    ],
    'Eastern Africa': [
        'BDI', 'COM', 'DJI', 'ERI', 'ETH', 'KEN', 'MDG', 'MWI', 'MUS', 'MYT', 
        'MOZ', 'REU', 'RWA', 'SYC', 'SOM', 'SSD', 'TZA', 'UGA', 'ZMB', 'ZWE'
    ],
    'Central Africa': [
        'AGO', 'CMR', 'CAF', 'TCD', 'COD', 'GNQ', 'GAB', 'COG', 'STP',
    ],
    'Northern Africa': [
        'DZA', 'EGY', 'LBY', 'MAR', 'SDN', 'TUN', 'ESH'
    ],
    'Southern Africa': ['BWA', 'LSO', 'NAM', 'ZAF', 'SWZ'],
    'Western Africa': [
        'BEN', 'BFA', 'CPV', 'CIV', 'GMB', 'GHA', 'GIN', 'GNB', 'LBR', 
        'MLI', 'MRT', 'NER', 'NGA', 'SHN', 'SEN', 'SLE', 'TGO'
    ],
    'Oceania': [
        'AUS', 'FIJ', 'CCK', 'NZL', 'PNG', 'SLB', 'VUT', 'FSM', 'GUM', 
        'KIR', 'MHL', 'NRU', 'MNP', 'PLW', 'PYF', 'ASM', 'COK', 'WSM', 
        'TON', 'TUV'
    ]
}

class Union:
	""" Allows easy access to various characteristics of unions."""

	def __init__(self, members):
		print(members)