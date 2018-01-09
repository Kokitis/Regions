import pandas

class AddFrenchRegions:
	"""

	"""
	def __init__(self, dataset, filename):

		region_table = pandas.read_excel(filename, sheet_name = 'Régions', skiprows = 7)

		departement_table = pandas.read_excel(filename, sheet_name = 'Départements', skiprows = 7)

		arrondissements_table = pandas.read_excel(filename, sheet_name = 'Arrondissements', skiprows = 7)

		cantons_table = pandas.read_excel(filename, sheet_name = 'Cantons et métropoles', skiprows = 7)

		communes_table = pandas.read_excel(filename, sheet_name = 'Communes', skiprows = 7)

		regions = self.parseTable(region_table, "")
		departements = self.parseTable(departement_table, '')
		cantons = self.parseTable(cantons_table, '')
		communes = self.parseTable(communes_table, '')

		#Code région	Nom de la région	Code département	Nom du département	Nombre d'arrondissements
		# Nombre de cantons	Nombre de communes	Population municipale	Population totale	Superficie

	def parseTable(self, region_table, **kwargs):

		region_name_column =

		regions = list()

		for row in region_table:

			result = {
				'regionCode': row['Code région'],
				'regionName': row['Nom de la région'],
				'regionPopulation': row.get('Population totale', 0),
				'superRegion': row.get(super_region_column),
				'regionArea': row.get('Superficie', 0)
			}
			regions.append(result)

		return regions
