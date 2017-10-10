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

UN_Geoschemes = {
	'Northern America': ['USA', 'CAN', 'BMU', 'GRL', 'SPM'],
	'Central America': ['MEX']
}

class Union:
	""" Allows easy access to various characteristics of unions."""

	def __init__(self, members):
		print(members)