""" The RegionDatabase class is designed to represent any one region database as a single object.
	Additional databases are represented by their own RegionDatabase objects.
"""

from pprint import pprint
from functools import partial
from ..widgets.validation import ValidateApiResponse, ValidateSqlResponse

pprint = partial(pprint, width = 180)

from pony.orm import Database, db_session
#from pony.orm.core import EntityMeta
import math
from . import entities
from .entities._sql_entities.sql_base_classes import *

from ..widgets import *
from ..github import timetools, numbertools
from ..data import configuration

from typing import *

Filename = str

database_folder: Filename = os.path.join(configuration.data_directory, "databases")

standard_datasets: Dict[str, Filename] = {
	'europe': os.path.join(database_folder, "eurostat_database.sqlite"),
	'global': os.path.join(database_folder, "global_database.sqlite"),
	'test':   os.path.join(database_folder, 'test_database.sqlite')
}

XY_SEPARATOR: str = '|'
POINT_SEPARATOR: str = '||'

SQL_ARGUMENT_VALIDATION = ValidateSqlResponse()
#EntityType = EntityMeta
EntityType = Union[SqlAgency, SqlRegion, SqlReport, SqlScale, SqlSeries, SqlUnit]

_checkEntityType: Callable[[EntityType, str], bool] = lambda a, b: hasattr(b, 'entity_type') and b.entity_type == a


class RegionDatabase:
	def __init__(self, filename: Filename, create: bool = False):
		"""
			Parameters
			----------
				filename: string
					Either a path to a region database or the name of a commonly used database.
		"""
		self.filename = self._getFilename(filename)
		self._main_database: Database = Database()
		_entities: Dict[str, EntityType] = entities.importDatabaseEntities(self._main_database)

		self.create: bool = create

		self.Agency: EntityType = _entities['agency']
		self.Identifier: EntityType = _entities['identifier']
		self.Namespace: EntityType = _entities['namespace']
		self.Region: EntityType = _entities['region']
		self.Report: EntityType = _entities['report']
		self.Series: EntityType = _entities['series']
		self.Tag: EntityType = _entities['tag']
		self.Unit: EntityType = _entities['unit']
		self.Scale: EntityType = _entities['scale']

		self._main_database.bind("sqlite", self.filename, create_db = create)  # create_tables
		self._main_database.generate_mapping(create_tables = create)

	@db_session
	def _getEntityClass(self, entity_type: str) -> EntityType:
		""" Matches an entity string to the corresponding class.
			Parameters
			----------

				entity_type: str,Entity
				{
					'agency', 'identifier', 'namespace', 'observation', 'region', 'series', 'tag', 'unit', 'scale'
				}

		"""

		if entity_type == 'agency':
			_class = self.Agency
		elif entity_type == 'identifier':
			_class = self.Identifier
		elif entity_type == 'namespace':
			_class = self.Namespace
		elif entity_type == 'region':
			_class = self.Region
		elif entity_type == 'report':
			_class = self.Report
		elif entity_type == 'series':
			_class = self.Series
		elif entity_type == 'tag':
			_class = self.Tag
		elif entity_type == 'unit':
			_class = self.Unit
		elif entity_type == 'scale':
			_class = self.Scale
		else:
			message = "'{}' is not a valid entity type.".format(entity_type)
			raise KeyError(message)

		return _class

	@staticmethod
	def _getFilename(string: str) -> Filename:
		if string in standard_datasets:
			filename = standard_datasets[string]
		elif string == 'temp' or string == ':memory:':
			filename = ":memory:"
		else:
			filename = os.path.join(database_folder, string)
			if not filename.endswith('.sqlite'):
				filename += '.sqlite'
		return filename

	@db_session
	def _insertEntity(self, entity_type: str, **kwargs) -> EntityType:
		""" Inserts an entity into the database. Assumes valid data was passed.
			Parameters
			----------
				entity_type: {'agency', 'identifier', 'namespace', 'observation', 'region', 'report', 'series', 'unit', 'scale'}
				*args
				**kwargs
		"""

		SQL_ARGUMENT_VALIDATION.validateResponse(entity_type, kwargs)
		entity_class = self._getEntityClass(entity_type)

		#result = entity_class(**kwargs)
		result = entity_class.fromDict(kwargs)

		return result

	@db_session
	def select(self, entity_type: str, expression: Callable[[EntityType], bool]) -> Any:
		entity_class = self._getEntityClass(entity_type)
		result = entity_class.select(expression)
		return result


	def _getEntityKey(self, entity_type: str) -> str:
		entity_class = self._getEntityClass(entity_type)
		entity_key = entity_class.getPrimaryKey()
		if entity_type in {'report', 'agency'}:
			entity_key = 'name'
		elif entity_type in {'unit', 'scale', 'units', 'identifier'}:
			entity_key = 'string'
		elif entity_type == 'namespace':
			entity_key = 'code'
		elif entity_type == 'region':
			entity_key = 'code'
		elif entity_type == 'tag':
			entity_key = 'string'
		elif entity_type == 'series':
			entity_key = ('code', 'region', 'report')
		else:
			message = "'{}' is not supported!".format(entity_type)
			raise ValueError(message)

		return entity_key

	##########################
	#    Public Methods      #
	##########################

	@db_session
	def addNamespace(self, key: str) -> EntityType:
		""" Adds a namespace to the database.
			TODO: Change to support the addition of a namespace from a dictionary.
			Returns
			-------
			Namespace
		"""

		namespace = self.getEntity('namespace', code = key)
		if namespace:
			return namespace
		elif key == 'ISO':
			namespace = namespace_configurations.importIsoNamespace()
		elif key == 'NUTS':
			namespace = namespace_configurations.importNutsNamespace()
		elif key == 'FIPS':
			namespace = namespace_configurations.importFipsNamespace()
		elif key == 'USPS':  # State codes
			namespace = namespace_configurations.importUSPSNamespace()
		else:
			message = "'{}' is not a valid namespace code ({})".format(key, ', '.join(['ISO', 'NUTS', 'FIPS', 'ST']))
			raise ValueError(message)

		namespace_data = namespace['namespace']
		regions = namespace['regions']
		namespace_entity = self._insertEntity('namespace', **namespace_data)

		for region_data in regions:
			identifiers = region_data.pop('identifiers')
			region_key = region_data['code']
			if self.exists('region', region_key):
				region_entity = self.getRegion('region', region_key)
			else:
				region_entity = self._insertEntity('region', **region_data)

			for identifier in identifiers:

				if not self.exists('identifier', identifier):
					identifier_data = {
						'string':    identifier,
						'namespace': namespace_entity,
						'region':    region_entity
					}
					self._insertEntity('identifier', **identifier_data)
		self._main_database.commit()
		return namespace_entity

	def _getEntityPrimaryKey(self, entity_type: str, key: str = None, **kwargs) -> Dict[str, str]:
		entity_key = self._getEntityKey(entity_type)
		if key is None:
			if entity_key in kwargs:
				key = kwargs.get(entity_key)
			else:
				error_message = {
					'parameters': {
						'entity_type': entity_type,
						'key':         key,
						'kwargs':      kwargs
					},
					'variables':  {
						'entity_key': entity_key
					}
				}
				pprint(error_message)
				message = "No entity key was provided!"
				raise ValueError(message)
		if isinstance(entity_key, str):
			entity_key = [entity_key]

		if isinstance(key, str):
			key = [key]
		config = {k: v for k, v in zip(entity_key, key)}
		# pprint(config)
		return config

	def exists(self, entity_type: str, key: Optional[str] = None, **kwargs) -> bool:
		""" Wrapper around self.select(entity_type, expression).exists() """
		entity_class = self._getEntityClass(entity_type)
		primary_key = self._getEntityPrimaryKey(entity_type, key, **kwargs)
		response = entity_class.exists(**primary_key)
		return response

	@db_session
	def getRegion(self, key: str) -> EntityType:
		"""Requests a region based on its name or namespace.
			Parameters
			----------
			key: str
				The code or name of a region.

			Returns
			-------
			region: Region; default None
		"""
		# Get region by string
		region = self.Region.get(code = key)
		if region is None:
			region = self.Region.get(name = key)

		if region is None:
			message = "'{}' cannot be used to find a region.".format(key)
			raise ValueError(message)
		return region

	@db_session
	def getSeries(self, region: Union[EntityType, str], key: str, to_entity: bool = False) -> Union[
		None, EntityType, entities.DataSeries]:
		"""	Retrieves a specific series for a given region.
			Parameters
			----------
				region: str, Region
				key: str
					The name or code of a series.
				to_entity: bool; default False
					Method will return a Series entity rather than a SeriesData entity.
		"""
		series_region = self.getRegion(region)
		series = self.Series.get(region = series_region, code = key)
		if series:
			if to_entity:
				series_data = series
			else:
				series_data = series.toSeries()
		else:
			series_data = None
		return series_data

	# Methods for adding data to the database.

	def getData(self, entity_type: str, key: Optional[str] = None, **kwargs) -> Dict:
		entity = self.getEntity(entity_type, key, **kwargs)
		entity_data = entity.toDict()
		return entity_data

	@db_session
	def addEntity(self, entity_type: str, entity_data: Union[None, Dict, EntityType] = None, **kwargs) -> EntityType:
		"""
			Checks if an entity already exists before attempting to insert it.
		Parameters
		----------
		entity_type
		entity_data
		kwargs

		Returns
		-------

		"""
		SQL_ARGUMENT_VALIDATION.validateResponse(entity_type, entity_data)
		if entity_data is None:
			entity_data = kwargs
		if hasattr(entity_data, 'entity_type'):
			is_correct_entity = _checkEntityType(entity_type, entity_data)
			if is_correct_entity:
				return entity_data
			else:
				message = "'{}' does not match the expected entity type of '{}'".format(entity_data.entity_type,
																						entity_type)
				raise ValueError(message)

		arguments = entity_data


		if self.exists(entity_type, **arguments):
			entity = self.getEntity(entity_type, **arguments)
			if entity is None:
				print("addEntity", arguments)
				raise ValueError

		else:
			entity = self._insertEntity(entity_type, **arguments)

		return entity

	@db_session
	def getEntity(self, entity_type: str, key: Optional[str] = None, **kwargs) -> EntityType:

		entity_config = self._getEntityPrimaryKey(entity_type, key, **kwargs)
		# print(entity_config)
		if entity_type == 'region':
			if key is None:
				key = kwargs.get('code')
			retrieved_entity = self.getRegion(key)
		elif entity_type == 'series':

			region = kwargs['region']
			series_code = kwargs['code']
			retrieved_entity = self.getSeries(region, series_code, to_entity = True)
		else:
			entity_class = self._getEntityClass(entity_type)

			retrieved_entity = entity_class.get(**entity_config)

		return retrieved_entity

	########################################
	#   Methods for adding/updating data   #
	########################################

	def _insertRegion(self, region_key: str, region_data: Dict, report_namespace) -> EntityType:
		region_config = {
			'code':   region_key,
			'type':   region_data['regionType'],
			'name':   region_data['regionName'],
			'parent': region_data.get('regionParent')
		}
		region_parent = region_data.get('regionParent')

		region_config['parent'] = region_parent
		region_entity = self.addEntity('region', **region_config)

		identifier_data = {
			'string':    region_key,
			'namespace': report_namespace,
			'region':    region_entity
		}

		self.addEntity('identifier', **identifier_data)

		return region_entity

	def _insertSeries(self, series_key: str, region_entity: EntityType, report_entity: EntityType,
					  series_data: Dict) -> Optional[EntityType]:
		# processed_arguments = self._validateEntityArguments('series', series_data)
		series_already_exists = self.Series.exists(code = series_key, region = region_entity, report = report_entity)
		if series_already_exists:
			return self.getSeries(region_entity, series_key)
		scale_data = series_data['seriesScale']
		unit_data = series_data['seriesUnits']

		if isinstance(scale_data, str):
			scale_data = {
				'string':     scale_data.lower(),
				'multiplier': float(numbertools.getMultiplier(scale_data))
			}
		if isinstance(unit_data, str):
			unit_data = {
				'string': unit_data,
				'code':   ''
			}

		scale_entity = self.addEntity('scale', scale_data)
		unit_entity = self.addEntity('unit', unit_data)

		series_values = series_data['seriesValues']
		if len(series_values) == 0: return None
		series_values = ["{}{}{}".format(i, XY_SEPARATOR, j) for i, j in series_values if not math.isnan(j)]
		series_values = POINT_SEPARATOR.join(series_values)
		series_config = {
			'code':        series_key,
			'name':        series_data['seriesName'],
			'description': series_data['seriesDescription'],
			'notes':       series_data['seriesNotes'],

			# Relations
			'scale':       scale_entity,
			'units':       unit_entity,
			'region':      region_entity,
			'report':      report_entity,
			'strvalues':   series_values
		}


		inserted_series = self.Series(**series_config)
		return inserted_series

	@db_session
	def addFromApi(self, report: Dict, verbose: bool = False):
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
		verbose: bool; default False

		Returns
		-------

		"""
		########################## Setup #######################################

		timer = timetools.Timer()
		db_size = self.filesize
		if verbose:
			print("Importing from Api Response...", flush = True)
			print("\tsize of database before import: {:.2f} MB".format(db_size))

		ValidateApiResponse(report)

		report_namespace = self.addNamespace(report['namespace'])

		report_data: Dict = report['report']
		agency_data: Dict = report['agency']

		agency_entity: EntityType = self.addEntity('agency', **agency_data)

		report_data['reportAgency'] = agency_entity

		report_entity: EntityType = self.addEntity('report', **report_data)

		parent_region_map_cache = dict()
		for index, region_data in enumerate(report['regions']):

			# Add region
			region_key = region_data['regionCode']
			region_entity = self.getRegion(region_key, report_namespace)

			if region_entity is None:
				# Need to add the region to the database
				region_entity = self._insertEntity(region_key, region_data, report_namespace)

			parent_region_key = region_data.get('regionParent')
			parent_region_map_cache[parent_region_key] = parent_region_map_cache.get(parent_region_key, []) + [
				region_key]

			for series_data in region_data['regionSeries']:
				self._insertSeries(series_data['seriesCode'], region_entity, report_entity, series_data)

			# self._insertSeries(series_data['seriesCode'], region_entity, report_entity, series_config)
			self._main_database.commit()

		# self.addEntity('series', **series_config)
		if None in parent_region_map_cache:
			parent_region_map_cache.pop(None)
		for parent_region, children in parent_region_map_cache.items():
			parent_entity = self.getRegion(parent_region)
			for child_region in children:
				child_entity = self.getRegion(child_region)
				child_entity.parent = parent_entity
		# print("Added '{}' as the parent to '{}'".format(parent_entity, child_entity))

		db_size = self.filesize
		if verbose:
			print("\tSize of database after import: {:.2f} MB".format(db_size))
			print("\tFinished in ", timer)

	@property
	def filesize(self) -> float:
		try:
			db_size = os.path.getsize(self.filename) / 1024 ** 2
		except FileNotFoundError:
			db_size = 0.0

		return db_size

	@db_session
	def rollback(self):
		self._main_database.rollback()
