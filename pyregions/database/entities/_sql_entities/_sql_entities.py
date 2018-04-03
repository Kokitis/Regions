from pony.orm import Optional, PrimaryKey, Required, Set, db_session, Database
from pony.orm.core import Entity

from typing import Dict

from .sql_base_classes import *


@db_session
def importDatabaseEntities(db: Database) -> Dict[str, Entity]:
	""" Defines the structure of the database.
		Parameters
		----------
		db: pony.orm.Database
			The database object to insert the entities into.
	"""

	class Region(db.Entity, SqlRegion):
		region_type = Required(str)
		region_name = Required(str)  # PrimaryKey(str)
		region_code = PrimaryKey(str)
		region_identifiers = Set('Identifier')
		region_parent = Optional('Region', reverse = 'subregions')
		region_children = Set('Region', reverse = 'parent')
		region_series = Set('Series')
		region_tags = Set('Tag')
		entity_type = 'region'

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

	class Report(db.Entity, SqlReport):
		report_name = PrimaryKey(str)
		report_code = Optional(str)
		report_url = Required(str)
		report_date = Required(str)
		report_data = Set('Series')
		report_agency = Required('Agency')
		report_tags = Set('Tag')
		entity_type = 'report'

	class Series(db.Entity, SqlSeries):
		series_region = Required(Region)
		series_report = Required(Report)
		series_code = Required(str)
		series_name = Required(str)
		series_description = Optional(str)
		series_notes = Optional(str)

		series_units = Optional('Unit')
		series_scale = Optional('Scale')

		strvalues = Required(str)
		series_tags = Set('Tag')
		PrimaryKey(series_region, series_report, series_code)
		entity_type = 'series'

	class Agency(db.Entity, SqlAgency):
		agency_code = Required(str)
		agency_name = PrimaryKey(str)
		agency_url = Optional(str)
		agency_address = Optional(str)
		agency_reports = Set(Report)
		entity_type = 'agency'

	class Namespace(db.Entity):
		namespace_name = PrimaryKey(str)
		namespace_code = Optional(str)
		namespace_regex = Optional(str)
		namespace_subtypes = Optional(str)
		namespace_url = Required(str)
		namespace_identifiers = Set(Identifier)
		entity_type = 'namespace'

		@db_session
		def toDict(self, compact = False):
			if compact:
				namespace_identifiers = list()
			else:
				namespace_identifiers = [i.key for i in self.namespace_identifiers]

			data = {
				'entityType':           'namespace',
				'entityKey':            self.key,
				'namespaceName':        self.namespace_name,
				'namespaceCode':        self.namespace_code,
				'namespacePattern':     self.namespace_regex,
				'namespaceWebsite':     self.namespace_url,
				'namespaceIdentifiers': namespace_identifiers
			}
			return data

		@property
		def key(self):
			return self.namespace_name

	class Tag(db.Entity):
		tag_string = PrimaryKey(str)
		tag_regions = Set(Region)
		tag_reports = Set(Report)
		tag_series = Set(Series)
		entity_type = 'tag'

		@property
		def key(self):
			return self.tag_string

		@property
		def value(self):
			return self.tag_string.split('|')[1]

		@db_session
		def toDict(self):
			data = {
				'entityType': 'tag',
				'entityKey':  self.tag_key,
				'tagString':  self.tag_string
			}

			return data

	class Unit(db.Entity, SqlUnit):
		# id 	 = PrimaryKey(int, auto=True)
		unit_code = Optional(str)
		unit_string = PrimaryKey(str)
		unit_series = Set(Series)
		entity_type = 'unit'



	class Scale(db.Entity, SqlScale):
		# id 			= PrimaryKey(int, auto=True)
		scale_series = Set(Series)
		scale_string = PrimaryKey(str)
		scale_multiplier = Required(float)
		entity_type = 'scale'


	_entities: Dict[str, Entity] = {
		'agency':     Agency,
		'identifier': Identifier,
		'namespace':  Namespace,
		'region':     Region,
		'report':     Report,
		'series':     Series,
		'tag':        Tag,
		'unit':       Unit,
		'scale':      Scale
	}

	return _entities
