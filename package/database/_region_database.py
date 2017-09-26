""" The RegionDatabase class is designed to represent any one region database as a single object.
	Additional databases are represented by their own RegionDatabase objects.
"""
import os
from pprint import pprint

import pony
import progressbar

from .. import entities
from ..data import getDefinition
from ..utilities import namespaces, validation

DATA_FOLDER = "C:\\Users\\Deitrickc\\Documents\\GitHub\\RegionDB\\data\\databases\\"

standard_datasets = {
	'global': os.path.join(DATA_FOLDER, "global_database.sqlite"),
	'europe': os.path.join(DATA_FOLDER, "eurostat_database.sqlite")
}

class RegionDatabase:
	""" Accesses a database with information concerning various regions.
	"""
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
		elif entity == 'observation':
			_class = self.Observation
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
	
	def _initializeDatabase(self, filename, create):

		if filename in standard_datasets:
			filename = standard_datasets[filename]


		_database = pony.orm.Database()
		_entities = entities.importDatabaseEntities(_database)

		Agency, Identifier, Namespace, Observation, Region, Report, Series, Tag, Unit, Scale = _entities

		self.Agency 	= Agency 
		self.Identifier = Identifier 
		self.Namespace 	= Namespace 
		self.Observation= Observation 
		self.Region 	= Region 
		self.Report 	= Report 
		self.Series 	= Series
		self.Tag 		= Tag
		self.Unit 		= Unit 
		self.Scale 		= Scale

		

		_database.bind("sqlite", filename, create_db = create) #create_tables
		_database.generate_mapping(create_tables = create)

		return _database
	
	@pony.orm.db_session
	def _insertEntity(self, entity_class, **kwargs):
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

		try:
			result = entity_class(**kwargs)
		except Exception as exception:
			print("Exception: ", str(exception))
			print("Arguments passed to class: ")
			for k, v in sorted(kwargs.items()):
				print("\t{}:\t{}".format(k, v))
			message = "Entity creation failed due to incorrect arguments ({})".format(str(exception))
			raise ValueError(message)
		return result
	@staticmethod
	def _selectEntity(entity_class, **kwargs):
		""" Retrieves an entity based on available arguments.
			If the entity is not found, returns None. 
			Parameters
			----------
				entity_class: Entity
				**kwargs: Valid keyword arguments.
		"""
		try:
			response = entity_class.get(**kwargs)
		except ValueError:
			response = None 

		return response

	@pony.orm.db_session
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
		keys = [i for i in keys if isinstance(i, str)]
		#print(keys)
		if namespace is None:
			candidates = self.Identifier.select(lambda s: s)
		else:
			namespace = self.access('get', 'namespace', namespace)
			if namespace is None:
				raise ValueError
			candidates = self.Identifier.select(lambda s: s.namespace == namespace)

		candidates = [i for i in candidates if i.string in keys]
		
		if len(candidates) == 0:
			candidates = list(self.Region.select(lambda s: s.name in keys))
		
		
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
			result = candidates[0]
		
		return result
	def insertEntity(self, entity_type, **kwargs):
		return self.access('insert', entity_type, **kwargs)

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

		
		_filter = lambda s: (s.code == key or s.name == key) and s.region == region
		
		series = region.series.select(_filter)
		series = list(series)
		if select_one and len(series) > 0:
			series = series[0]
		return series


	@pony.orm.db_session
	def _searchEntity(self, entity_class, *args, **kwargs):
		"""	Requests an entity based on a variety of inputs. If nothing is found, returns None.
			entity_class: Entity
			*args: string, dict, Entity (Limit 1 argument)
				Should map to the primary key of a single entity.
			kwargs: dict<string>
				Keyword arguments to use.
		"""

		if len(kwargs) == 0 and len(args) == 1:
			entity_key = args[0]
		else:
			entity_key = kwargs

		# Choose the method to use by the type of input
		if isinstance(entity_key, str):
			result = self._searchByString(entity_class, entity_key)
		elif isinstance(entity_key, dict):
			result = self._searchByKeywords(entity_class, **kwargs)
		elif isinstance(entity_key, entity_class):
			result = entity_key
		else:
			result = None
		return result
	
	@staticmethod
	def _searchByString(entity_class, string, search_field = 'all'):
		"""
			Searches for an entity based on a single key string.
			Parameters
			----------
			entity_class: string, Entity
				The entity type to search through
			string: str
				The key to search for.
			search_field: {'all', 'code', 'name', 'value'}; default 'all'
				A specific class field to search through. If not provided,
				Will search through a number of fields based on the entity type.
			Returns
			-------
				result: Entity, None
		"""
		# For readability and shorter code.

		_checkFields = lambda r, l: r is None and search_field in {'all', l} and hasattr(entity_class, l)

		if string is None:
			return None
		elif _checkFields(None, 'code'):
			result = entity_class.get(code=string)
		else:
			result = None

		if _checkFields(result, 'name'):
			result = entity_class.get(name=string)

		if _checkFields(result, 'string'):
			result = entity_class.get(string=string)

		return result

	def _searchByKeywords(self, entity_class, **kwargs):
		"""
			Searches for a match between the identifying features in a dict
			and the entities in the database.
			Parameters
			----------
				entity_class: str, Entity
					A valid entity class or identifier
				keywords: dict<{'code', 'name', 'value', 'namespace'}:scalar>
					One or more keywords that identify a single entity in the dataset.
					if searching for a region, namespace must be provided.
		"""
		if isinstance(entity_class, str):
			entity_type = entity_class
		else:
			entity_type = entity_class.entity_type
		data = validation.parseEntityArguments(entity_type, kwargs)

		entity_code = data.get('code')
		entity_name = data.get('name')
		entity_string = data.get('string')


		result = self._searchByString(entity_class, entity_code, 'code')

		if result is None and hasattr(entity_class, 'name'):
			result = self._searchByString(entity_class, entity_name, 'name')

		if result is None and entity_string is not None and hasattr(entity_class, 'string'):
			result = self._searchByString(entity_class, entity_string, 'string')

		return result

	def describe(self, section = 'all'):
		"""
			Parameters
			----------
			section: {'all', 'regions', 'subjects', 'reports', 'series'}
		"""

		# List available regions
		if section in {'all', 'regions'}:
			print("Available Regions")
			for region in sorted(self.Region.select(lambda s: s), key = lambda s: s.name):
				print("\t", region.name)

		# List available reports/subjects
		if section in {'all', 'subjects', 'series', 'reports'}:
			print("Available Reports")
			for report in sorted(self.Report.select(lambda s: s), key = lambda s: s.name):
				print("\t", report.name)
				seen = set()
				for series in sorted(report.rows, key = lambda s: s.name):
					if series.code in seen: continue
					else: seen.add(series.code)
					print("\t\t{:<12}\t{}".format("'{}'".format(series.code), series.name))

	
	

	@pony.orm.db_session
	def access(self, method, entity_type, data = None, **kwargs):
		""" Access items from the database and adds them if desired.
			Parameters
			----------
				method: {'get', 'search', 'request', 'import', 'insert'}
					* 'get', 'request': If the item cannot be found, returns None
					* 'import': If the entity is not found, inserts it into the database.
					* 'insert': inserts an entity into the database.
				
				entity_type: {'agency', 'identifier', 'namespace', 'region', 'report', 'series'}
					The specific class of entity to search for. 
				
				data: str, dict, Entity
					
		"""

		entity_class = self._getEntityClass(entity_type)

		if data is None and len(kwargs) > 0:
			data = kwargs 

		if isinstance(data, dict):
			arguments = validation.parseEntityArguments(entity_type, data)
		elif hasattr(data, 'entity_type'):
			if data.entity_type != entity_type:
				message = "the entity passed to the function ('{}') does not match the requested entity type ('{}')".format(data.entity_type, entity_type)
				raise TypeError(message)
			else:
				return data
		elif isinstance(data, str):
			arguments = {}
		else:
			arguments = data

		if method == 'get':
			result = self._selectEntity(entity_class, **arguments)

		elif method in {'import', 'search'}:
			result = self._searchEntity(entity_class, data, **arguments)
		else:
			result = None

		if method == 'insert' or (method == 'import' and result is None):
			result = self._insertEntity(entity_class, **arguments)

		return result

	@pony.orm.db_session 
	def addNamespace(self, key):
		""" Adds a namespace to the database.
		""" 
		namespace = self.access('get', 'namespace', code = key)
		if namespace: return namespace
		if key == 'ISO':
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

	@pony.orm.db_session
	def importSeries(self, series):
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
		"""

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

	@pony.orm.db_session
	def importJson(self, data):
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
		"""
		namespace_code = data['namespace']
		self.addNamespace(namespace_code)
		
		report = data['report']
		agency = report['agency']
		agency = getDefinition('agency', agency)
		agency = self.access('import', 'agency', agency)

		report['agency'] = agency
		report = self.access('import', 'report', data['report'])

		skipped_region_codes = set()
		skipped = list()
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
					skipped_region_codes.add(region_code)
					skipped.append((region_code, region_name, namespace_code))
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

			series_description = row.get('seriesDescription')
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
				'values': row['values']
			}
			if scale is not None:
				series_json['scale'] = scale
			
			if isinstance(series_description, str): #checks if None or nan
				series_json['description'] = series_description

			#pprint(series_json)
			self.importSeries(series_json)
		print("Could not locate these regions: ")
		for item in skipped:
			rc, rn, ns = item
			print("\tRegion Code:\t", region_code)
			print("\t\tRegion Name:\t", region_name)
			print("\t\tNamespace:\t", ns)