from itertools import zip_longest
import math
from texttable import Texttable
def compareSeries(left, right):
	""" Compares two Series objects against each other.
		Parameters
		----------
			left, right: Series
	"""
	left_str = "{} ({}) ({})".format(left.name, left.report.code, left.region.name)
	right_str = "{} ({}) ({})".format(right.name, right.report.code, right.region.name)
	field_names = ['Year', left_str, right_str, 'Difference', 'PCT']
	table = Texttable()
	table.add_row(field_names)
	#table.add_row()
	table.set_cols_dtype(['i', 'e', 'e', 'e', 't'])
	
	common_x = set(left.x) & set(right.x)
	#print("\tYear\t\tLeft\tRight\tDiff\tRatio")
	for year in sorted(common_x):
		l = left(year)
		r = right(year)
			
		diff = l - r
		ratio = (r / l)# * 100

		pct = (r - l) / l
		pct = "{:.2%}".format(pct)

		table.add_row([year, l, r, diff, pct])    
		#print(line)
	return table
