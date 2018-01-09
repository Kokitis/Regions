
import pandas
from ._converters import ConvertTable
def addUSHistoricalProjections(dataset):

	filename = r"C:\Users\Deitrickc\Google Drive\Region Data\Regions\United States\Population\Population Projections\Illustrative Projections of the Population of the United States, by Age and Sex - 1960 to 1980.xlsx"
	table = pandas.read_excel(filename, sheet_name = None)
	reports = dict()

	for index, report in table['Reports'].iterrows():
		reports[report['reportCode']] = report.to_dict()

	for sheetname, sheet in table.items():
		if sheetname == 'Reports':
			continue
		elif len(sheet) == 0:
			continue

		namespace = 'ISO'
		report = reports[sheetname]
		config = {
			'namespace': namespace,
			'report': report,
			'seriesUnitMap': lambda *s: 'Persons'
		}
		converter = ConvertTable(dataset, sheet, **config)