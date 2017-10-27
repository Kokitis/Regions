from texttable import Texttable
from pony.orm import db_session 
from ..github import numbertools
@db_session
def rankRegions(dataset, report, subject, year = 2017):
	report_query = dataset.access('get', 'report', report)
	
	query = dataset.select('series', lambda s: s.report == report_query and s.code == subject)
	
	rows = list()
	for element in query:
		row = {
			'regionName': element.region.name,
			'value': element(year)
		}
		rows.append(row)
	rows = sorted(rows, key = lambda s: s['value'], reverse = True)
	
	table = Texttable()
	table.add_row(['regionName', 'value', 'rank'])
	table.set_cols_dtype(['t', 't', 'i'])
	table.set_cols_align(['l', 'r', 'r'])
	for index, row in enumerate(rows, start = 1):
		v = numbertools.humanReadable(row['value'])
		table.add_row([row['regionName'], v, index])
	print(table.draw())
	