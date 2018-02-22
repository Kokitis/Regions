""" The RegionDatabase class is designed to represent any one region database as a single object.
	Additional databases are represented by their own RegionDatabase objects.
"""
import os
from pprint import pprint
from functools import partial
from ..utilities import ValidateApiResponse, ValidateSqlResponse
pprint = partial(pprint, width = 180)

from pony.orm import Database, db_session
import progressbar

from . import entities

from ..utilities import validation
from ..widgets import *
from ..github import timetools, numbertools
from ..data import configuration
import math
from texttable import Texttable
database_folder = os.path.join(configuration.data_directory, "databases")

standard_datasets = {
	'europe': os.path.join(database_folder, "eurostat_database.sqlite"),
	'global': os.path.join(database_folder, "global_database.sqlite"),
	'test':   os.path.join(database_folder, 'test_database.sqlite')
}

XY_SEPARATOR = '|'
POINT_SEPARATOR = '||'

SQL_ARGUMENT_VALIDATION = ValidateSqlResponse()

class RegionDatabase:
	def __init__(self, filename, create = False, replace = False):
		"""
			Parameters
			----------
				filename: string
					Either a path to a region database or the name of a commonly used database.
		"""

		self.create = create
		self._main_database = self._initializeDatabase(filename, create, replace)
	@db_session
	def _getEntityClass(self, entity):
		""" Matches an entity string to the corresponding class.
			Parameters
			----------

				entity: str,Entity
				{
					'agency', 'identifier', 'namespace', 'observation', 'region', 'series', 'tag', 'unit', 'scale'
				}

		"""

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

	def _getFilename(self, string):
		if string in standard_datasets:
			filename = standard_datasets[string]
		elif string == 'temp' or string == ':memory:':
			filename = ":memory:"
		else:
			filename = os.path.join(database_folder, string)
			if not filename.endswith('.sqlite'):
				filename += '.sqlite'
		return filename

	def _initializeDatabase(self, _filename, create, replace):

		self.filename = self._getFilename(_filename)

		print("Database Filename: ", self.filename)
		if replace and os.path.exists(self.filename):
			os.remove(self.filename)

		_database = Database()
		_entities = entities.importDatabaseEntities(_database)

		#Agency, Identifier, Namespace, Observation, Region, Report, Series, Tag, Unit, Scale = _entities

		self.Agency 	= _entities['agency']
		self.Identifier = _entities['identifier']
		self.Namespace 	= _entities['namespace']
		self.Region 	= _entities['region']
		self.Report 	= _entities['report']
		self.Series 	= _entities['series']
		self.Tag 		= _entities['tag']
		self.Unit 		= _entities['unit']
		self.Scale 		= _entities['scale']

		_database.bind("sqlite", self.filename, create_db = create) #create_tables
		_database.generate_mapping(create_tables = create)

		return _database

	@db_session
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
		SQL_ARGUMENT_VALIDATION.validateResponse(entity_type, kwargs)
		entity_class = self._getEntityClass(entity_type)

		result = entity_class(**kwargs)

		return result

	@db_session
	def select(self, entity_type, expression):
		entity_class = self._getEntityClass(entity_type)
		result = entity_class.select(expression)
		return result
	@db_session
	def get(self, entity_type, expression = None, **kwargs):
		entity_class = self._getEntityClass(entity_type)
		try:
			if expression is not None:
				result = entity_class.get(expression)
			else:
				result = entity_class.get(**kwargs)
		except Exception as exception:
			#The entity class doesn't have one of the attribute keys passed in kwargs
			error_message = {
				'exception': exception,
				'exceptionMessage': str(exception),
				'parameters': {
					'entity_type': entity_type,
					'kwargs': kwargs
				},
				'entity_class': entity_class
			}
			pprint(error_message)
			raise exception
		return result

	def _getEntityKey(self, entity_type):
		if entity_type in {'report', 'agency'}:
			entity_key = 'name'
		elif entity_type in {'unit', 'scale', 'units'}:
			entity_key = 'string'
		elif entity_type == 'namespace':
			entity_key = 'code'
		elif entity_type == 'series':
			raise NotImplementedError
		else:
			raise NotImplementedError

		return entity_key


	##########################
	#    Private Methods     #
	##########################
	@db_session
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
			message = "The parameters do not fit any excepted format: "
			message += "\n" + str(arg)
			raise ValueError(message)
	
		return arguments

	##########################
	#    Public Methods      #
	##########################

	@db_session
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
		if 'verbose' in kwargs:
			verbose = kwargs.pop('verbose')
		else:
			verbose = False

		if entity_type == 'region' and method in {'get', 'request'}:
			message = "The retrieval of 'region' entities is not supported. Use *.getRegion() instead."
			raise KeyError(message)

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

		"""
		if exception is not None or verbose:
			exception_data = {
				'exception': str(exception),
				'sqlArguments': arguments,
				'parameters': {
					'method': method,
					'entity_type': entity_type,
					'data': data,
					'kwargs': kwargs
				}
			}
			pprint(exception_data)
			if exception is not None:
				message = "Entity creation failed due to incorrect arguments ({})".format(str(exception))
				raise ValueError(message)
		"""
		return result

	@db_session
	def addNamespace(self, key):
		""" Adds a namespace to the database.
			TODO: Change to support the addition of a namespace from a dictionary.
			Returns
			-------
			Namespace
		"""
		namespace = self.access('get', 'namespace', code = key)
		if namespace: return namespace
		elif key == 'ISO':
			namespace = importIsoNamespace()
		elif key == 'NUTS':
			namespace = namespaces.importNutsNamespace(self)
		elif key == 'FIPS':
			namespace = namespaces.importFipsNamespace(self)
		elif key == 'ST': #State codes
			namespace = namespaces.importStateNamespace(self)
		else:
			message = "'{}' is not a valid namespace code ({})".format(key, ', '.join(['ISO', 'NUTS', 'FIPS', 'ST']))
			raise ValueError(message)

		namespace_data = namespace['namespace']
		regions = namespace['regions']
		namespace_entity = self._insertEntity('namespace', **namespace_data)


		for region_data in regions:
			identifiers = region_data.pop('identifiers')
			region_entity = self._insertEntity('region', **region_data)
			for identifier in identifiers:
				identifier_data = {
					'string': identifier,
					'namespace': namespace_entity,
					'region': region_entity
				}
				self._insertEntity('identifier', **identifier_data)


		return namespace_entity
	
	def summary(self, section = 'all'):
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
	@db_session
	def exists(self, entity_type, key):
		""" Wrapper around self.select(entity_type, expression).exists() """
		entity_class = self._getEntityClass(entity_type)
		entity_key = self._getEntityKey(entity_type)
		params = {
			entity_key: key,
		}
		response =  entity_class.exists(**params)
		return response

	@db_session
	def contains(self, string):
		""" Wrapper over self.exists() to test for regions, either by name or code. """

		expression = lambda s: s.name == string or string in s.identifiers.string 
		result = self.exists('region', expression)
		return result

	@db_session
	def getRegion(self, key, namespace = None):
		"""Requests a region based on its name or namespace.
			Parameters
			----------
			key: str, Identifier
				The code or name of a region.
			namespace: str,Namespace; default None
				The namespace to search through, if a code is provided.
				The keys are required to be valid identifiers if the namespace is not given.
			Returns
			-------
			region: Region; default None
		"""
		if isinstance(key, str):
			region = self.get('region', code = key)
		else:
			region = None

		if region is None:
			if namespace is None:
				identifier = self.get('identifier', string = key)
			else:
				if not isinstance(namespace, str):
					namespace_code = namespace.code
				else:
					namespace_code = namespace
				identifier = self.get('identifier', lambda s: s.string == key and s.namespace.code == namespace_code)
			if identifier is not None:
				region = identifier.region
			else:
				region = None

		return region
	
	@db_session
	def getRegions(self, keys, namespace = None):
		""" Searches for a number of regions. """

		for key in keys:
			yield self.getRegion(key, namespace)

	@db_session
	def getSeries(self, region, key):
		"""	Retrieves a specific series for a given region.
			Parameters
			----------
				region: str, Identifier, Region
				key: str
					The name or code of a series.
		"""
		series_region = self.getRegion(region)
		series = self.get('series', region = series_region, code = key)
		return series



	# Methods for adding data to the database.
	@db_session
	def addReport(self, report, namespace, verbose = False):
		"""
			Adds a report to the database.
		Parameters
		----------
			report: dict<>
				* 'agency': dict<>
					*''
				* 'report': dict<>
				* 'regions': list<dict<>>
					A list of all region identifiers that will be added.
				* 'series': list<dict<>>
					* 'region': str
					* 'seriesCode': str
					* 'seriesName': str
					* 'seriesScale': str
					* 'seriesDescription': str
					* 'seriesValues': list<Timestamp, float>
				* 'scales': list<dict>
				* 'units': list<dict>
			namespace: str
			verbose: bool; default False


		"""
		########################## Setup #######################################
		print("Importing from Dict...", flush = True)
		timer = timetools.Timer()
		db_size = self.filesize
		print("size of database: {:.2f} MB".format(db_size))


		############################## Workflow ###############################
		if verbose:
			print("Adding the report...")
		namespace = self.addNamespace(namespace)

		#report_namespace = self.get('namespace', namespace)
		report_name = report['report']['reportName']
		# Check if the report already exists.
		agency_entity = self.access('import', 'agency', report['agency'])
		report_information = report['report']
		report_information['reportAgency'] = agency_entity

		if self.exists('report', report_name):
			print("The report '{}' already exists in the database.".format(report_name))
			return None
		else:
			report_entity = self.access('insert', 'report', report_information)

		self._main_database.commit()


		################################ Add Regions ##############################
		# Check if any of the regions contained in the report are missing.
		if verbose:
			print("Adding regions...")
		_missing_regions = list()
		region_entities = dict()
		for region in report['regions']:

			region_key = region['regionCode']
			region_entity = self.getRegion(region_key, namespace)

			if region_entity is None:
				# Need to add the region to the database
				_missing_regions.append(region_key)
				region_data = {
					'code': region_key,
					'regionType':   region['regionType'],
					'name':         region['regionName'],
					'parentRegion': region['regionParent']
				}

				region_entity = self.access('insert', 'region', region_data)

				identifier_data = {
					'string': region_key,
					'namespace': namespace,
					'region': region_entity
				}
				self.Identifier(**identifier_data)

			else:
				# TODO update region identifiers
				pass

			region_entities[region_key] = region_entity


		print("Added {} of {} total regions.".format(len(_missing_regions), len(report['regions'])))
		############################### Add Scales ################################
		if verbose:
			print("Adding scales...")
		for scale in report['scales']:
			scale_key = scale['scaleString']
			scale_entity = self.getEntity('scale', scale_key)
			if scale_entity is None:
				scale_data = {
					'string':     scale_key,
					'multiplier': numbertools.getMultiplier(scale_key)
				}
				self.access('insert', 'scale', scale_data)

		############################# Add Units ###################################
		if verbose:
			print("Adding units...")
		for unit in report['units']:
			unit_key = unit['unitString']
			unit_entity = self.getEntity('unit', unit_key)
			if unit_entity is None:
				unit_data = {
					'code':   unit['unitCode'],
					'string': unit['unitString']
				}
				self.access('insert', 'unit', unit_data)

		############################# Add Series ####################################
		if verbose:
			print("Adding series...")

		pbar = progressbar.ProgressBar(max_value = len(report['series']))
		for index, series in enumerate(report['series']):
			pbar.update(index)

			region_key = series['regionKey']
			scale_key = series['seriesScale']
			unit_key = series['seriesUnits']

			# series_region = self.getEntity('region', region_key)
			series_region = region_entities[region_key]
			series_report = report_entity
			series_scale = self.getEntity('scale', scale_key)
			series_unit = self.getEntity('unit', unit_key)

			series_values = series['seriesValues']
			series_values = [(i, numbertools.toNumber(j)) for i, j in series_values]
			series_values = ["{}{}{}".format(i, XY_SEPARATOR, j) for i, j in series_values if not math.isnan(j)]

			if len(series_values) == 0:
				continue

			series_data = {
				'code':        series['seriesCode'],
				'name':        series['seriesName'],
				'description': series['seriesDescription'],

				# Relations
				'scale':       series_scale,
				'units':        series_unit,
				'region':      series_region,
				'report':      series_report,
				'strvalues':   POINT_SEPARATOR.join(series_values)
			}

			self.access('insert', 'series', series_data)
		self._main_database.commit()
		# print("Imported {} of {} series".format(len(data['series']) - len(skipped), len(data['series'])))
		db_size = self.filesize
		print("Size of database: {:.2f} MB".format(db_size))
		print("Finished in ", timer)
		if verbose:
			print("Could not locate these regions: ")
	@db_session
	def addFromApi(self, report, verbose = True):
		"""
			Adds a report formatted as an API response to the database.

		Parameters
		----------
		report: dict<>
			* 'report': dict<>
			* 'namespace': str
			* 'regions': dict<>
				* 'regionName': str
				* 'regionIdentifiers': list<str>
				* 'regionSeries': list<dict>
					* 'seriesName': str
					* 'seriesCode': str
					* 'seriesScale': str
					* 'seriesUnits': str
			* 'scales': list<dict<>>
			* 'units': list<dict<>>
		verbose: bool; default True

		Returns
		-------

		"""
		########################## Setup #######################################
		print("Importing from Dict...", flush = True)
		timer = timetools.Timer()
		db_size = self.filesize
		print("size of database: {:.2f} MB".format(db_size))

		ValidateApiResponse(report)


		report_namespace = self.addNamespace(report['namespace'])

		report_data = report['report']
		agency_data = report['agency']
		agency_entity = self.access('import', 'agency', agency_data)

		report_data['reportAgency'] = agency_entity

		report_entity = self.access('insert', 'report', report_data)



		for region_data in report['regions']:

			# Add region
			region_key = region_data['regionCode']
			region_entity = self.getRegion(region_key, report_namespace)

			if region_entity is None:
				# Need to add the region to the database
				region_config = {
					'code': region_key,
					'type':   region_data['regionType'],
					'name':         region_data['regionName'],
					'parent': region_data['regionParent']
				}

				region_entity = self.access('insert', 'region', region_config)

				identifier_data = {
					'string': region_key,
					'namespace': report_namespace,
					'region': region_entity
				}
				self.Identifier(**identifier_data)

			else:
				# TODO update region identifiers
				pass


			for series_data in region_data['regionSeries']:

				scale_data = series_data['seriesScale']
				unit_data = series_data['seriesUnits']

				if isinstance(scale_data, str):
					scale_data = {
						'string': scale_data.lower(),
						'multiplier': float(numbertools.getMultiplier(scale_data))
					}
				if isinstance(unit_data, str):
					unit_data = {
						'string': unit_data,
						'code': ''
					}

				scale_entity = self.access('import', 'scale', scale_data)
				unit_entity = self.access('import', 'unit', unit_data)

				series_values = series_data['seriesValues']
				if len(series_values) == 0: continue
				series_values = ["{}{}{}".format(i, XY_SEPARATOR, j) for i,j  in series_values]
				series_values = POINT_SEPARATOR.join(series_values)
				series_config = {
					'code':        series_data['seriesCode'],
					'name':        series_data['seriesName'],
					'description': series_data['seriesDescription'],
					'notes':       series_data['seriesNotes'],

					# Relations
					'scale':       scale_entity,
					'units':        unit_entity,
					'region':      region_entity,
					'report':      report_entity,
					'strvalues':   series_values
				}
				self.access('insert', 'series', series_config)

		db_size = self.filesize
		print("Size of database: {:.2f} MB".format(db_size))
		print("Finished in ", timer)
		if verbose:
			print("Could not locate these regions: ")

	@db_session
	def getEntity(self, entity_type, key, **kwargs):
		if entity_type == 'region':
			result = self.getRegion(key, **kwargs)

		else:
			entity_key = self._getEntityKey(entity_type)

			result = self.get(entity_type, **{entity_key: key})

		if result is None:
			if entity_type == 'namespace':
				result = self.get(entity_type, code = key)


		return result

	@property
	def filesize(self):
		if os.path.exists(self.filename):
			db_size = os.path.getsize(self.filename) / 1024**2
		else:
			db_size = 0.0

		return db_size
	@db_session
	def toDict(self, entity_type, key, expand = 1, **kwargs):
		entity = self.getEntity(entity_type, key)
		if entity:
			data = entity.toDict(expand, **kwargs)
		else:
			data = None
		return data