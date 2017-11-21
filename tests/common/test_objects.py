
TEST_REGION = {
	'name': 'United States of America',
 	'parentRegion': None,
 	'regionType': 'country'
}

TEST_SERIES = {
	'code': 'LP',
	'description': 'For census purposes, the total population of the country '
					'consists of all persons falling within the scope of the '
					'census. In the broadest sense, the total may comprise either '
					'all usual residents of the country or all persons present in '
					'the country at the time of the census. [Principles and '
					'Recommendations for Population and Housing Censuses, Revision '
					'1, paragraph 2.42]',
	'name': 'Population',
	'notes': '',
	'region': 'United States of America',
	'report': 'World Economic Outlook, April 2017',
	'scale': 'Millions',
	'strvalues': '1980|227.622||1981|229.916||1982|232.128||1983|234.247||1984|236.307||1985|238.416||1986|240.593||1987|242.751||1988|244.968||1989|247.286||1990|250.047||1991|253.392||1992|256.777||1993|260.146||1994|263.325||1995|266.458||1996|269.581||1997|272.822||1998|276.022||1999|279.195||2000|282.296||2001|285.216||2002|288.019||2003|290.733||2004|293.389||2005|296.115||2006|298.93||2007|301.903||2008|304.718||2009|307.374||2010|309.756||2011|312.019||2012|314.284||2013|316.476||2014|318.789||2015|321.08||2016|323.298||2017|325.741||2018|328.244||2019|330.766||2020|333.307||2021|335.867||2022|338.448',
	'unit': 'Persons',
	'values': [
		(1980, 227622000.0), (1981, 229916000.0), (1982, 232128000.0), (1983, 234247000.0), 
		(1984, 236307000.0), (1985, 238416000.0), (1986, 240593000.0), (1987, 242751000.0), 
		(1988, 244968000.0), (1989, 247286000.0), (1990, 250047000.0), (1991, 253392000.0), 
		(1992, 256777000.0), (1993, 260146000.00000003), (1994, 263325000.0), 
		(1995, 266458000.00000003), (1996, 269581000.0), (1997, 272822000.0), (1998, 276022000.0), 
		(1999, 279195000.0), (2000, 282296000.0), (2001, 285216000.0), (2002, 288019000.0), 
		(2003, 290733000.0), (2004, 293389000.0), (2005, 296115000.0), (2006, 298930000.0), 
		(2007, 301903000.0), (2008, 304718000.0), (2009, 307374000.0), (2010, 309756000.0), 
		(2011, 312019000.0), (2012, 314284000.0), (2013, 316476000.0), (2014, 318789000.0), 
		(2015, 321080000.0), (2016, 323298000.0), (2017, 325741000.0), (2018, 328244000.0), 
		(2019, 330766000.0), (2020, 333307000.0), (2021, 335867000.0), (2022, 338448000.0)
	]
}
TEST_REPORT = {
	'agency': 'International Monetary Fund',
 	'code': 'WEO2017B',
 	'name': 'World Economic Outlook, April 2017',
 	'publishDate': 'April 2017',
 	'retrievedDate': '',
 	'url': 'http://www.imf.org/en/Publications/WEO/Issues/2017/04/04/world-economic-outlook-april-2017'
}

TEST_IDENTIFIER = {
	'namespace': 'International Organization for Standardization',
	'region': 'United States of America',
	'string': 'USA'
}

TEST_AGENCY = {
	'address': '700 19th Street, N.W., Washington, D.C. 20431|1900 Pennsylvania '
    'Ave NW, Washington, DC, 20431',
	'code': 'IMF',
	'name': 'International Monetary Fund',
	'url': 'http://www.imf.org/external/index.htm|http://www.imf.org/en/data'
}

TEST_NAMESPACE = {
	'code': 'ISO',
	'name': 'International Organization for Standardization',
	'regex': '(?P<iso2>[A-Z]{2})|(?P<iso3>[A-Z]{3})|(?P<numeric>[0-9]{3})',
	'subtypes': 'iso2|iso3|numeric',
	'url': 'https://www.iso.org/iso-3166-country-codes.html'
 }

TEST_TAG = {

}

TEST_UNIT = {'code': '', 'string': 'Persons'}

TEST_SCALE = {'multiplier': 1000000, 'string': 'Millions'}
