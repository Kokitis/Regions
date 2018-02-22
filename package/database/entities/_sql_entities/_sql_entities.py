from pony.orm import Optional, PrimaryKey, Required, Set, db_session
from ._custom_sql_region import CustomSqlRegion
from package.github import timetools


@db_session
def importDatabaseEntities(db):
	""" Defines the structure of the database.
		Parameters
		----------
		db: pony.orm.Database 
			The database object to insert the entities into.
	"""

	class Region(db.Entity, CustomSqlRegion):
		# code 		= PrimaryKey(str)
		type = Required(str)
		name = Required(str)  # PrimaryKey(str)
		code = PrimaryKey(str)
		identifiers = Set('Identifier')
		parent = Optional('Region', reverse = 'subregions')
		subregions = Set('Region', reverse = 'parent')
		series = Set('Series')
		tags = Set('Tag')
		entity_type = 'region'

		@property
		def key(self):
			region_key = self.name
			return region_key

		@db_session
		def toDict(self, compact = False):

			parent_region = self.parentRegion
			if compact:
				if parent_region:
					region_parent = parent_region.toDict()
				else:
					region_parent = None
				region_identifiers = [i.string for i in self.identifiers]
				subregions = list()
				region_series = list()

			else:
				region_series = [i.key for i in self.series]
				if parent_region:
					region_parent = parent_region.key
				else:
					region_parent = None
				region_identifiers = [i.key for i in self.identifiers]
				subregions = [i.key for i in self.subRegions]


			data = {
				'entityType':        'region',
				'entityKey':         self.key,
				'regionType':        self.regionType,
				'regionName':        self.name,

				# Relations
				'regionIdentifiers': region_identifiers,
				'regionParent':      region_parent,
				'regionSubregions':  subregions,
				'regionSeries':      region_series,
				'regionTags':        list()
			}

			return data

	class Identifier(db.Entity):
		string = Required(str)
		region = Required(Region)
		namespace = Required('Namespace')
		entity_type = 'identifier'
		PrimaryKey(namespace, string)

		@property
		def key(self):
			identifier_key = (self.namespace.key, self.string)
			return identifier_key

		@db_session
		def toDict(self, compact):

			if compact:
				identifier_namespace = self.namespace.key
				identifier_region = self.region.key
			else:
				identifier_namespace = self.namespace.toDict(True)
				identifier_region = self.region.toDict(True)

			data = {
				'entityType':       'identifier',
				'entityKey':        self.key,
				'identifierRegion': identifier_region,
				'string':           self.string,
				'namespace':        identifier_namespace
			}
			return data

	class Report(db.Entity):
		name = PrimaryKey(str)
		code = Optional(str)
		url = Required(str)
		date = Required(str)
		data = Set('Series')
		agency = Required('Agency')
		tags = Set('Tag')
		entity_type = 'report'

		@property
		def key(self):
			report_key = self.name
			return report_key

		@db_session
		def toDict(self, compact=False):
			if compact and False:
				report_agency = self.agency.key

			else:
				report_agency = self.agency.toDict(True)
			report_data = list()

			data = {
				'entityType':   'report',
				'reportName':   self.name,
				'reportCode':   self.code,
				'reportUrl':    self.url,
				'reportDate':   self.publishDate,
				'data':         report_data,
				'reportAgency': report_agency,
				'reportTags':   list()
			}



			return data

	class Series(db.Entity):
		region = Required(Region)
		report = Required(Report)
		code = Required(str)
		name = Required(str)
		description = Optional(str)
		notes = Optional(str)

		units = Optional('Unit')
		scale = Optional('Scale')

		strvalues = Required(str)
		tags = Set('Tag')
		PrimaryKey(region, report, code)
		entity_type = 'series'

		def _splitStringValues(self):
			string_values = self.strvalues

			nvalues = list()
			for element in string_values.split('||'):
				year, value = element.split('|')
				value = float(value)
				if len(year) == 4:
					year = year + '-01-01'
				year = timetools.Timestamp(year)
				nvalues.append((year, value))
			return nvalues

		@property
		def values(self):
			""" Returns list<Timestamp, float> """
			if not hasattr(self, '_values_cache'):
				self._values_cache = self._splitStringValues()

			return self._values_cache

		@property
		def fvalues(self):
			if not hasattr(self, '_fvalues_cache'):
				self._fvalues_cache = [(i.toYear(), j) for i, j in self.values]
			return self._fvalues_cache

		@property
		def key(self):
			series_key = (self.region.key, self.report.key, self.code)
			return series_key

		@db_session
		def toDict(self, compact = False, **kwargs):
			to_json = kwargs.get('to_json', False)
			if compact:
				series_region = self.region.key
				series_report = self.report.key
				series_units = self.unit.key
				series_scale = self.scale.key
			else:
				series_region = self.region.toDict(True)
				series_report = self.report.toDict(True)
				series_units = self.unit.toDict(True)
				series_scale = self.scale.toDict(True)

			if to_json:
				series_values = self.fvalues
			else:
				series_values = self.values


			data = {
				'entityType':        'series',
				'entityKey':         self.key,
				'seriesRegion':      series_region,
				'seriesReport':      series_report,
				'seriesCode':        self.code,
				'seriesName':        self.name,
				'seriesDescription': self.description,
				'seriesNotes':       self.notes,
				'seriesUnits':       series_units,
				'seriesScale':       series_scale,
				'seriesValues':      series_values,
				'seriesTags':        list(),
			}
			return data

	class Agency(db.Entity):
		code = Required(str)
		name = PrimaryKey(str)
		url = Optional(str)
		address = Optional(str)
		reports = Set(Report)
		entity_type = 'agency'

		@db_session
		def toDict(self, compact = False):
			if compact:
				agency_reports = list()
			else:
				agency_reports = [i.key for i in self.reports]

			data = {
				'entityType':    'agency',
				'agencyCode':    self.code,
				'agencyName':    self.name,
				'agencyWebsite': self.url,
				'agencyAddress': self.address,
				'agencyReports': agency_reports
			}
			return data

		@property
		def key(self):
			return self.name

	class Namespace(db.Entity):
		name = PrimaryKey(str)
		code = Optional(str)
		regex = Optional(str)
		subtypes = Optional(str)
		url = Required(str)
		identifiers = Set(Identifier)
		entity_type = 'namespace'

		@db_session
		def toDict(self, compact = False):
			if compact:
				namespace_identifiers = list()
			else:
				namespace_identifiers = [i.key for i in self.identifiers]

			data = {
				'entityType':           'namespace',
				'entityKey':            self.key,
				'namespaceName':        self.name,
				'namespaceCode':        self.code,
				'namespacePattern':     self.regex,
				'namespaceWebsite':     self.url,
				'namespaceIdentifiers': namespace_identifiers
			}
			return data

		@property
		def key(self):
			return self.name

	class Tag(db.Entity):
		string = PrimaryKey(str)
		regions = Set(Region)
		reports = Set(Report)
		series = Set(Series)
		entity_type = 'tag'

		@property
		def key(self):
			return self.string

		@property
		def value(self):
			return self.string.split('|')[1]

		@db_session
		def toDict(self):
			data = {
				'entityType': 'tag',
				'entityKey':  self.key,
				'tagString':  self.string
			}

			return data

	class Unit(db.Entity):
		# id 	 = PrimaryKey(int, auto=True)
		code = Optional(str)
		string = PrimaryKey(str)
		series = Set(Series)
		entity_type = 'unit'

		@property
		def key(self):
			return self.string

		@db_session
		def toDict(self):

			data = {
				'entityType':   'unit',
				'entityKey':    self.key,
				'entityString': self.string,
				'entityCode':   self.code
			}
			return data

	class Scale(db.Entity):
		# id 			= PrimaryKey(int, auto=True)
		series = Set(Series)
		string = PrimaryKey(str)
		multiplier = Required(float)
		entity_type = 'scale'

		@property
		def key(self):
			return self.string

		@db_session
		def toDict(self):
			scale_series = list()
			data = {
				'entityType':      'scale',
				'entityKey':       self.key,
				'scaleSeries':     scale_series,
				'scaleString':     self.string,
				'scaleMultiplier': self.multiplier
			}
			return data

	_entities = {
		'agency':      Agency,
		'identifier':  Identifier,
		'namespace':   Namespace,
		'region':      Region,
		'report':      Report,
		'series':      Series,
		'tag':         Tag,
		'unit':        Unit,
		'scale':       Scale
	}

	return _entities
