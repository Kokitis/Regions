""" The RegionDatabase class is designed to represent any one region database as a single object.
	Additional databases are represented by their own RegionDatabase objects.
"""
import os
from pprint import pprint

import pony
import progressbar

from .. import entities

from ..utilities import namespaces, validation, getDefinition
from ..github import Texttable, timetools

database_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "databases")

standard_datasets = {
	'europe': os.path.join(database_folder, "eurostat_database.sqlite"),
	'global': os.path.join(database_folder, "global_database.sqlite")
}

class CoreDatabase:
	def __init__(self, filename, create = False):
		"""
			Parameters
			----------
				filename: string
					Either a path to a region database or the name of a commonly used database.
		"""
		self.create = create
		self._main_database = self._initializeDatabase(filename, create)
	def _getEntityClass(self, entity):
		""" Matches an entity string to the corresponding class.
			Parameters
			----------

				entity: str, Entity
				{
					'agency', 'identifier', 'namespace', 'observation', 'region', 'series', 'tag', 'unit', 'scale'
				}

		"""
		if not isinstance(entity, str):
			entity = entity.entity_type
		if entity == 'agency':
			_class = self.Agency
		elif entity == 'identifier':
			_class = self.Identifier
		elif entity == 'namespace':
			_class = self.Namespace
		elif entity == 'region':
			_class = self.Region
		elif entity == 'report':
			_class = self.Report
		elif entity == 'series':
			_class = self.Series
		elif entity == 'tag':
			_class = self.Tag
		elif entity == 'unit':
			_class = self.Unit
		elif entity == 'scale':
			_class = self.Scale
		else:
			message = "'{}' is not a valid entity type.".format(entity)
			raise KeyError(message)

		return _class

	def _initializeDatabase(self, _filename, create):

		if _filename in standard_datasets:
			_filename = standard_datasets[filename]
		self.filename = _filename
		print("Database Filename: ", self.filename)

		_database = pony.orm.Database()
		_entities = entities.importDatabaseEntities(_database)

		#Agency, Identifier, Namespace, Observation, Region, Report, Series, Tag, Unit, Scale = _entities

		self.Agency 	= _entities['agency']
		self.Identifier = _entities['identifier']
		self.Namespace 	= _entities['namespace']
		#self.Observation= _entities['observation']
		self.Region 	= _entities['region']
		self.Report 	= _entities['report']
		self.Series 	= _entities['series']
		self.Tag 		= _entities['tag']
		self.Unit 		= _entities['unit']
		self.Scale 		= _entities['scale']

		_database.bind("sqlite", self.filename, create_db = create) #create_tables
		_database.generate_mapping(create_tables = create)

		return _database

	@pony.orm.db_session
	def _insertEntity(self, entity_type, **kwargs):
		""" Inserts an entity into the database. Assumes valid data was passed.
			Parameters
			----------
				entity_type: {'agency', 'identifier', 'namespace', 'observation', 'region', 'report', 'series', 'unit', 'scale'}
				*args
				**kwargs
		"""

		if not self.create:
			message = "The database must be initialized with the 'create' keyword set to True."
			print(message)
			return None
		entity_class = self._getEntityClass(entity_type)
		try:
			result = entity_class(**kwargs)
		except Exception as exception:
			print("Exception: ", str(exception))
			print("Arguments passed to class ('{}'): ".format(entity_class))
			for k, v in sorted(kwargs.items()):
				print("\t{}:\t{}".format(k, v))
			message = "Entity creation failed due to incorrect arguments ({})".format(str(exception))
			raise ValueError(message)
		return result


	def select(self, entity_type, expression):
		entity_class = self._getEntityClass(entity_type)
		result = entity_class.select(expression)
		return result

	def get(self, entity_type, **kwargs):
		entity_class = self._getEntityClass(entity_type)
		try:
			result = entity_class.get(**kwargs)
		except TypeError:
			#The entity class doesn't have one of the attribute keys passed in kwargs
			result = None
		return result



class RegionDatabase(CoreDatabase):
	""" Accesses a database with information concerning various regions.
	"""

	##########################
	#    Private Methods     #
	##########################
	
	def _searchByString(self, entity_type, string):
		"""
			Searches for an entity based on a single key string.
			Parameters
			----------
			entity_type: string
				The entity type to search through
			string: str
				The key to search for.
			Returns
			-------
				result: Entity, None
		"""

		for key in ['code', 'name', 'string']:
			result = self.get(entity_type, **{key: string})
			if result is not None:
				break
		else:
			result = None
		return result
	
	@staticmethod
	def _validateEntityArguments(entity_type, arg, **kwargs):
		""" Validates parameters used to insert or retrieve entities from the database.
			Parameters
			----------
			entity_type: str
				One of the valid entity identifiers
			arg: str, dict, None
				Referes to either a key or name for a pre-existing entity 
			**kwargs: Valid entity parameters
		"""
		if arg is None and len(kwargs) > 0:
			arg = kwargs

		if isinstance(arg, dict):
			arguments = validation.parseEntityArguments(entity_type, arg)
		elif hasattr(arg, 'entity_type'):
			if arg.entity_type != entity_type:
				message = "the entity passed to the function ('{}') does not match the requested entity type ('{}')".format(
					arg.entity_type, entity_type
				)
				raise TypeError(message)
			else:
				arguments = None

		elif isinstance(arg, str):
			arguments = {}
			if len(arg) < 4 or arg.isupper():
				arguments['code'] = arg
			else:
				arguments['name'] = arg
		else:
			message = "The paramters do not fit any excepted format: "
			message += "\n" + str(arg)
			raise ValueError(message)
	
		return arguments

	##########################
	#    Public Methods      #
	##########################

	@pony.orm.db_session
	def access(self, method, entity_type, data = None, **kwargs):
		""" Access items from the database and adds them if desired.
			Parameters
			----------
				method: {'add', 'get', 'search', 'request', 'import', 'insert'}
					* 'get', 'request': If the item cannot be found, returns None
					* 'import', 'add': If the entity is not found, inserts it into the database.
					* 'insert': inserts an entity into the database.

				entity_type: {'agency', 'identifier', 'namespace', 'region', 'report', 'series'}
					The specific class of entity to search for.

				data: str, dict, Entity

		"""

		#entity_class = self._getEntityClass(entity_type)

		arguments = self._validateEntityArguments(entity_type, data, **kwargs)

		if arguments is None:
			return data #Data is an entity object

		if method in {'get', 'retrieve'}:
			result = self.get(entity_type, **arguments)

		elif method in {'add', 'import', 'search'}:
			if isinstance(data, str):
				result = self._searchByString(entity_type, data)
			else:
				result = self.get(entity_type, **arguments)
		else:
			result = None

		if method == 'insert' or (method in {'import', 'add'} and result is None):
			result = self._insertEntity(entity_type, **arguments)

		return result

	@pony.orm.db_session
	def addNamespace(self, key):
		""" Adds a namespace to the database.
		"""
		namespace = self.access('get', 'namespace', code = key)
		if namespace: pass
		elif key == 'ISO':
			namespace = namespaces.importIsoNamespace(self)
		elif key == 'NUTS':
			namespace = namespaces.importNutsNamespace(self)
		elif key == 'FIPS':
			namespace = namespaces.importFipsNamespace(self)
		elif key == 'ST': #State codes
			namespace = namespaces.importStateNamespace(self)
		else:
			message = "'{}' is not a valid namespace code ({})".format(key, ', '.join(['ISO', 'NUTS', 'FIPS', 'ST']))
			raise ValueError(message)

		#namespace = self.access('import', 'namespace', **namespace)

		return namespace
	
	def describe(self, section = 'all'):
		"""
			Parameters
			----------
			section: {'all', 'regions', 'subjects', 'reports', 'series'}
		"""

		# List available regions
		if section in {'all', 'regions'}:
			print("Available Regions")
			for region in sorted(self.select('region', lambda s: s), key = lambda s: s.name):
				print("\t", region.name)

		display_table = Texttable()
		display_table. set_cols_width([20, 20, 30, 60, 60])
		display_table.add_row(['reportName', 'seriesCode', 'seriesName', 'seriesDescription', 'seriesNotes'])

		# List available reports/subjects
		if section in {'all', 'subjects', 'series', 'reports'}:
			print("Available Reports")
			for report in self.select('report', lambda s: s):
				#print("\t", report.name)
				display_table.add_row([report.name, "", "", "", ""])
				seen = set()
				report_series  =self.select('series', lambda s: s.report == report)
				report_series.order_by(lambda s: s.name)
				for series in report_series:
					if series.code in seen: continue
					else: seen.add(series.code)
					#print("\t\t{:<12}\t{}".format("'{}'".format(series.code), series.name))
					display_table.add_row(["", "'{}'".format(series.code), series.name, series.description, series.notes])
		print(display_table.draw())
		return display_table
	def exists(self, entity_type, expression):
		""" Wrapper around self.select(entity_type, expression).exists() """
		response =  self.select(entity_type, expression).exists()
		return response

	def getRegion(self, keys, namespace = None):
		"""Requests a region based on its name or namespace.
			Parameters
			----------
			keys: str, list
				The code or name of a region.
			namespace: str, Namespace; default None
				The namespace to search through, if a code is provided.
				The keys are required to be valid identifiers if the namespace is not given.
			Returns
			-------
			region: Region; default None
		"""
		if not isinstance(keys, (list,tuple,set)):
			keys = [keys]
		keys = (i for i in keys if isinstance(i, str))

		candidates = self.select('identifier', lambda s: s.string in keys)

		if namespace is not None:
			namespace = self.access('get', 'namespace', namespace)
			candidates = candidates.filter(lambda s: s.namespace == namespace)

		if len(candidates) > 1:
			message = "Error when searching for regions!"
			print("Arguments passed to getRegion: ")
			print("\tkeys: ", keys)
			print("\tnamespace: ", namespace)
			print("Found:")
			for i in candidates:
				print("\t", i)
			raise ValueError(message)
			
		elif len(candidates) == 0:
			result = None
		else:
			result = candidates.first().region

		return result
	
	@pony.orm.db_session
	def getRegions(self, keys, namespace = None):
		""" Searches for a number of regions. """

		for key in keys:
			yield self.getRegion(key, namespace)

	@pony.orm.db_session
	def getSeries(self, region, key, select_one = True):
		"""	Retrieves a specific series for a given region.
			Parameters
			----------
				region: str, Identifier, Region
				key: str
					The name or code of a series.
				select_one: bool; default True
					Returns a single result
		"""
		region = self.getRegion(region)

		_filter = lambda s: (s.code == key or s.name == key) and region in s.region.identifiers

		series = self.select('series', _filter)

		if select_one and len(series) > 0:
			series = series.first()
		return series

	@pony.orm.db_session
	def addJson(self, data, verbose = False):
		""" Imports a series into the database.
			Parameters
			----------
			data: dict
				* namespace: str
				* agency: str
				* report: dict
				* series: list of dict
					* 'regionCode': str
					* 'seriesCode': str
					* 'seriesName': str
					* 'seriesScale': str
					* 'seriesUnits': dict
						* 'unitCode': str; default None
						* 'unitString': str
					* seriesValues: list
			verbose: bool; default False
				If True, additional status messages will be displayed
				when importing series, including which regions could
				not be updated.
		"""
		print("Importing from JSON", flush = True)
		timer = timetools.Timer()
		if os.path.exists(self.filename):
			db_size = os.path.getsize(self.filename) / 1024**2
		else:
			db_size = 0.0
		print("size of database: {:.2f} MB".format(db_size))
		namespace_code = data['namespace']
		self.addNamespace(namespace_code)

		report = data['report']
		agency = report['agency']
		agency = getDefinition('agency', agency)
		agency = self.access('import', 'agency', agency)

		report['agency'] = agency
		report = self.access('import', 'report', data['report'])

		skipped_region_codes = set()
		skipped = set()
		print("Importing the converted series into the database...")
		pbar = progressbar.ProgressBar(max_value = len(data['series']))
		for index, row in enumerate(data['series']):
			pbar.update(index)

			region_code = row['regionCode']
			region_name = row.get('regionName')
			region = self.getRegion(region_code, namespace_code)

			if region is None:
				if region_code not in skipped_region_codes:
					#print("Could not find region when importing series!")
					#print("\tRegion Code:\t'{}'\t{}".format(region_code, type(region_code)))
					#print("\tRegion Name:\t'{}'\t{}".format(region_name, type(region_name)))
					#print("\tNamespace:\t'{}'".format(namespace_code))
					skipped_region_codes.add(str(region_code))
					skipped.add((region_code, region_name, namespace_code, row['seriesCode']))
				continue
				#raise ValueError

			scale_string = row['seriesScale']

			if scale_string is not None and not isinstance(scale_string, float):
				scale = self.access('import', 'scale', string = scale_string)
			else:
				scale = None

			units = row['seriesUnits']
			if units is not None:
				units = self.access('import', 'unit', units)

			series_description = row['seriesDescription']
			series_tags = row['seriesTags']
			if series_tags is None:
				series_tags = []
			series_tags = [self.access('import', 'tag', string = i) for i in series_tags if isinstance(i, str)]

			series_json = {
				'region': region,
				'report': report,
				'code': row['seriesCode'],
				'name': row['seriesName'],
				'unit': units,
				'tags': series_tags,
				'values': row['values'],
			}
			
			if scale is not None:
				series_json['scale'] = scale

			if isinstance(series_description, str): #checks if None or nan
				series_json['description'] = series_description

			self.addSeries(series_json)
		print("Imported {} of {} series".format(len(data['series']) - len(skipped), len(data['series'])))
		db_size = os.path.getsize(self.filename) / 1024**2
		print("Size of database: {:.2f} MB".format(db_size))
		print("Finished in ", timer)
		if verbose:
			print("Could not locate these regions: ")
			table = Texttable()
			table.add_row(['Region Code', 'Region Name', 'Namespace', 'Series Code'])
			for item in sorted(skipped):
				#rc, rn, ns, sc= item
				table.add_row([(str(i) if str(i) != 'nan'  else "") for i in item])


			print(table.draw())

	@pony.orm.db_session
	def addSeries(self, series):
		""" Imports a series into the database.
			Parameters
			----------
			series: dict
				* 'region': Region
				* 'report': Report
				* 'name': str
				* 'code': str
				* 'notes': str
				* 'units': Units
				* 'scale': Scale
				* 'values': list of x-y value pairs.
				* 'description': str
		"""
		#pprint(series)
		series = validation.parseEntityArguments('series', series)
		
		series_values = series.pop('values')

		if series['region'] is None:
			pprint(series)
			message = "Could not find the region"
			raise ValueError(message)

		elif series['region'].entity_type == 'identifier':
			series['region'] = series['region'].region

		string_values = list()
		for x, y in series_values:
			if validation.isNull(x) or validation.isNull(y): continue
			if not validation.isNumber(x) or not validation.isNumber(y): continue

			string_values.append((x, y))

		if 'tags' in series:
			series_tags = series.pop('tags')
		else:
			series_tags = []

		string_values = ["{}|{}".format(x, y) for x, y in sorted(string_values)]
		string_values = "||".join(string_values)

		series['strvalues'] = string_values

		if len(string_values) > 0:
			series = self.access('insert', 'series', **series)

		for tag in series_tags:
			t = self.access('import', 'tag', tag)
			if not isinstance(series, dict):
				series.tags.add(t)
		return series

