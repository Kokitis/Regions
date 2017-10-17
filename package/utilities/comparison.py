
from texttable import Texttable

def compareSeries(left, right):
	""" Compares two Series objects against each other.
		Parameters
		----------
		left, right: Series
	"""
	left_str = "{} ({}) ({})".format(left.name, left.report.code, left.region.name)
	right_str = "{} ({}) ({})".format(right.name, right.report.code, right.region.name)
	field_names = ['Year', left_str, right_str, 'Difference', 'PCT', 'ratio']
	table = Texttable()
	table.add_row(field_names)

	table.set_cols_dtype(['i', 'e', 'e', 'e', 't', 'f'])
	
	common_x = set(left.x) & set(right.x)

	for year in sorted(common_x):
		l = left(year)
		r = right(year)
			
		diff = l - r

		pct = (l-r) / r
		pct = "{:.2%}".format(pct)
		ratio = l / r

		table.add_row([year, l, r, diff, pct, ratio])    
		#print(line)
	return table
