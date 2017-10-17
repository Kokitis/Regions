from pony.orm import Optional, PrimaryKey, Required, Set, db_session

from .custom_entities import *


@db_session
def importDatabaseEntities(db):
	""" Defines the structure of the database.
		Parameters
		----------
		db: pony.orm.Database 
			The database object to insert the entities into.
	"""

	class Region(db.Entity, AbstractRegion):
		#code 		= PrimaryKey(str)
		regionType 	= Required(str)
		name 		= PrimaryKey(str)
		identifiers = Set('Identifier')
		parentRegion = Optional('Region', reverse='subRegions')
		subRegions 	= Set('Region', reverse='parentRegion')
		series 		= Set('Series')
		tags 		= Set('Tag')
		entity_type = 'region'


	class Identifier(db.Entity, AbstractIdentifier):
		string 		= Required(str)
		region 		= Required(Region)
		namespace 	= Required('Namespace')
		entity_type = 'identifier'
		PrimaryKey(namespace, string)


	class Report(db.Entity, AbstractReport):
		name 		= PrimaryKey(str)
		code 		= Optional(str)
		url 		= Required(str)
		publishDate = Required(str)
		retrievedDate = Optional(str)
		rows 		= Set('Series')
		agency 		= Required('Agency')
		tags 		= Set('Tag')
		entity_type = 'report'

		@property
		def data(self):
			return self.rows


	class Series(db.Entity, AbstractSeries):
		region 	= Required(Region)
		report 	= Required(Report)
		code 	= Required(str)
		name 	= Required(str)
		description = Optional(str)
		notes 	= Optional(str)
		
		unit = Optional('Unit')
		scale = Optional('Scale')

		strvalues = Required(str)
		#day = Optional(str)
		tags 	= Set('Tag')
		PrimaryKey(region, report, code)
		entity_type = 'series'
		@classmethod
		def emulate(cls, template, values, **kwargs):
			""" Generates an SeriesEmulator object.
				Parameters
				----------
					values: list<int, float>
					template: Series
			"""
			return EmulatorSeries(template, values, **kwargs)

		@property
		def values(self):
			if self._values is None:
				self._values = self._splitStringValues()

			return self._values


	class Agency(db.Entity, AbstractAgency):
		code 		= Required(str)
		name 		= PrimaryKey(str)
		url 		= Optional(str)
		address 	= Optional(str)
		reports 	= Set(Report)
		entity_type = 'agency'


	class Observation(db.Entity):
		#series 	= Required(Series)
		series  = Required(str)
		x 		= Required(int)
		y 		= Required(float)
		PrimaryKey(series, x)
		entity_type = 'observation'


	class Namespace(db.Entity, AbstractNamespace):
		name 		= PrimaryKey(str)
		code 		= Optional(str)
		regex 		= Optional(str)
		subtypes 	= Optional(str)
		url 		= Required(str)
		identifiers = Set(Identifier)
		entity_type = 'namespace'


	class Tag(db.Entity, AbstractTag):
		string 		= PrimaryKey(str)
		regions 	= Set(Region)
		reports 	= Set(Report)
		series 		= Set(Series)
		entity_type = 'tag'

		@property
		def key(self):
			return self.string.split('|')[0]
		@property
		def value(self):
			return self.string.split('|')[1]
		


	class Unit(db.Entity, AbstractUnit):
		#id 	 = PrimaryKey(int, auto=True)
		code = Optional(str)
		string = PrimaryKey(str)
		series = Set(Series)
		entity_type = 'unit'


	class Scale(db.Entity, AbstractScale):
		#id 			= PrimaryKey(int, auto=True)
		series 		= Set(Series)
		string 		= PrimaryKey(str)
		multiplier 	= Optional(float)
		entity_type = 'scale'

	_entities = {
		'agency': Agency,
		'identifier': Identifier,
		'namespace': Namespace,
		'observation': Observation,
		'region': Region,
		'report': Report,
		'series': Series,
		'tag': Tag,
		'unit': Unit,
		'scale': Scale
	}

	#return Agency, Identifier, Namespace, Observation, Region, Report, Series, Tag, Unit, Scale
	return _entities