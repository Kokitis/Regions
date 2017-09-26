from prettytable import PrettyTable

def compareSeries(left, right, operation = None):
	""" Compares two series agains each other.
		Parameters
		----------
			left: Series
			right: Series
			operation: str
	"""
	ratio_series = left / right
	total_series = left + right
	diff_series  = left - right
	table = PrettyTable()

	if operation:
		pass
	else:
		for l, r, ratio, total, diff in zip(left, right, ratio_series, total_series, diff_series):
			year = l[0]
			print("{}\t{}\t{}\t{}\t{}\t{}".format(year, l[1], r[1], ratio[1], total[1], diff[1]))



