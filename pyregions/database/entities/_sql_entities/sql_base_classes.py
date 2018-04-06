from pony.orm import db_session
from typing import *
from .._data_containers import DataRegion, DataSeries
from ....github import timetools

SeriesList = List[Tuple[timetools.Timestamp, float]]


class CustomSqlRegion:
	def getSeries(self, string, report = None):
		""" Retrieves a specific series for this region.
			If more than one series is found, raises a ValueError.
			Parameters
			----------
				string: str
					The name or code of a series to retrieve.
				report: str; default None
					The name or code of a report in the database. If not provided,
					the first series found will be returned.

			Returns
			-------
				series: Series
		"""

		result = self.series.select(lambda s: s.code == string or s.name == string)
		if report:
			result = result.filter(lambda s: s.report.name == report or s.report.code == report)
		result = result.first()
		return result

	@property
	def series(self):
		raise NotImplementedError

	@property
	def report(self):
		raise NotImplementedError


class SqlRegion:
	entity_type: str = 'region'

	def __init__(self, *args, **kwargs):
		raise NotImplementedError

	def get(self, *args, **kwargs):
		raise NotImplementedError

	def select(self, *args, **kwargs):
		raise NotImplementedError

	def getPrimaryKey(self) -> Dict[str, Any]:
		raise NotImplementedError

	def exists(self, *args, **kwargs):
		raise NotImplementedError
	@classmethod
	def getEntity(cls, key: str):
		return cls.get(region_code = key)

	@property
	def key(self):
		region_key = self.region_code
		return region_key

	@db_session
	def toDict(self, compact = False):

		parent_region = self.region_parent
		if compact:
			if parent_region:
				region_parent = parent_region.toDict()
			else:
				region_parent = None
			region_identifiers = [i.string for i in self.region_identifiers]
			subregions = list()
			region_series = list()

		else:
			region_series = [i.key for i in self.region_series]
			if parent_region:
				region_parent = parent_region.key
			else:
				region_parent = None
			region_identifiers = [i.key for i in self.region_identifiers]
			subregions = [i.key for i in self.region_children]

		data = {
			'entityType':        'region',
			'entityKey':         self.key,
			'regionType':        self.region_type,
			'regionCode':        self.region_code,
			'regionName':        self.region_name,

			# Relations
			'regionIdentifiers': region_identifiers,
			'regionParent':      region_parent,
			'regionSubregions':  subregions,
			'regionSeries':      region_series,
			'regionTags':        list()
		}

		return data

	def toSeries(self) -> DataRegion:
		region_data = self.toDict()
		return DataRegion(region_data)

	@classmethod
	def fromDict(cls, data: Dict[str, Any]) -> 'SqlRegion':

		entity_data = {
			'region_type':   data['regionType'],
			'region_name':   data['regionName'],
			'region_code':   data['regionCode'],
			'region_parent': data.get('regionParent')
		}

		return cls(**entity_data)

	@property
	def region_name(self):
		raise NotImplementedError

	@property
	def region_type(self):
		raise NotImplementedError

	@property
	def region_code(self):
		raise NotImplementedError

	@property
	def region_parent(self):
		raise NotImplementedError

	@property
	def region_children(self):
		raise NotImplementedError

	@property
	def region_series(self):
		raise NotImplementedError

	@property
	def region_tags(self):
		raise NotImplementedError


class SqlReport:
	entity_type: str = 'report'

	def __init__(self, *args, **kwargs):
		raise NotImplementedError

	def get(self, *args, **kwargs):
		raise NotImplementedError

	def select(self, *args, **kwargs):
		raise NotImplementedError

	def getPrimaryKey(self) -> Dict[str, Any]:
		raise NotImplementedError

	def exists(self, *args, **kwargs):
		raise NotImplementedError

	@property
	def key(self):
		report_key = self.report_name
		return report_key

	@db_session
	def toDict(self, compact = False) -> Dict[str, Any]:
		if compact and False:
			report_agency = self.report_agency.key

		else:
			report_agency = self.report_agency.toDict(True)
		report_data = list()

		data = {
			'entityType':   'report',
			'reportName':   self.report_name,
			'reportCode':   self.report_code,
			'reportUrl':    self.report_url,
			'reportDate':   self.report_date,
			'data':         report_data,
			'reportAgency': report_agency,
			'reportTags':   list()
		}

		return data

	@classmethod
	def fromDict(cls, data: Dict[str, Any]) -> 'SqlReport':

		entity_data = {
			'report_name':   data['reportName'],
			'report_code':   data['reportCode'],
			'report_url':    data['reportUrl'],
			'report_data':   data['reportData'],
			'report_date':   data['reportDate'],
			'report_agency': data['reportAgency']
		}

		return cls(**entity_data)

	@property
	def report_name(self):
		raise NotImplementedError

	@property
	def report_code(self):
		raise NotImplementedError

	@property
	def report_url(self):
		raise NotImplementedError

	@property
	def report_date(self):
		raise NotImplementedError

	@property
	def report_data(self):
		raise NotImplementedError

	@property
	def report_agency(self):
		raise NotImplementedError

	@property
	def report_tags(self):
		raise NotImplementedError


class SqlSeries:
	entity_type: str = 'series'

	def __init__(self, *args, **kwargs):
		raise NotImplementedError

	def get(self, *args, **kwargs):
		raise NotImplementedError

	def select(self, *args, **kwargs):
		raise NotImplementedError

	def getPrimaryKey(self) -> Dict[str, Any]:
		raise NotImplementedError

	def exists(self, *args, **kwargs):
		raise NotImplementedError

	@classmethod
	def fromDict(cls, data: Dict[str, Any]) -> 'SqlSeries':

		entity_data = {
			'series_region':      data['seriesRegion'],
			'series_report':      data['seriesReport'],
			'series_code':        data['seriesCode'],
			'series_name':        data['seriesName'],
			'series_description': data['seriesDescription'],
			'series_notes':       data.get('seriesNotes'),
			'series_units':       data['seriesUnits'],
			'series_scale':       data['seriesScale']
		}
		return cls(entity_data)

	def _splitStringValues(self) -> SeriesList:
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
		series_key = (self.series_region.key, self.series_report.key, self.series_code)
		return series_key

	@db_session
	def toDict(self, compact = False, **kwargs) -> Dict[str, Any]:
		to_json = kwargs.get('to_json', False)
		if compact:
			series_region = self.series_region.key
			series_report = self.series_report.key
			series_units = self.series_units.key
			series_scale = self.series_scale.key
		else:
			series_region = self.series_region.toDict(True)
			series_report = self.series_report.toDict(True)
			series_units = self.series_units.toDict()
			series_scale = self.series_scale.toDict()

		if to_json:
			series_values = self.fvalues
		else:
			series_values = self.values

		data = {
			'entityType':        'series',
			'entityKey':         self.key,
			'seriesRegion':      series_region,
			'seriesReport':      series_report,
			'seriesCode':        self.series_code,
			'seriesName':        self.series_name,
			'seriesDescription': self.series_description,
			'seriesNotes':       self.series_notes,
			'seriesUnits':       series_units,
			'seriesScale':       series_scale,
			'seriesValues':      series_values,
			'seriesTags':        list(),
		}
		return data

	def toSeries(self) -> DataSeries:
		series_data = self.toDict()
		return DataSeries(series_data)

	@property
	def series_region(self):
		raise NotImplementedError

	@property
	def series_report(self):
		raise NotImplementedError

	@property
	def series_code(self):
		raise NotImplementedError

	@property
	def series_name(self):
		raise NotImplementedError

	@property
	def series_description(self):
		raise NotImplementedError

	@property
	def series_notes(self):
		raise NotImplementedError

	@property
	def series_units(self):
		raise NotImplementedError

	@property
	def series_scale(self):
		raise NotImplementedError

	@property
	def series_tags(self):
		raise NotImplementedError

	@property
	def strvalues(self):
		raise NotImplementedError


class SqlAgency:
	entity_type: str = 'agency'

	def __init__(self, *args, **kwargs):
		raise NotImplementedError

	def get(self, *args, **kwargs):
		raise NotImplementedError

	def select(self, *args, **kwargs):
		raise NotImplementedError

	def getPrimaryKey(self) -> Dict[str, Any]:
		raise NotImplementedError

	def exists(self, *args, **kwargs):
		raise NotImplementedError

	@db_session
	def toDict(self, compact = False) -> Dict[str, Any]:
		if compact:
			agency_reports = list()
		else:
			agency_reports = [i.key for i in self.agency_reports]

		data = {
			'entityType':    'agency',
			'agencyCode':    self.agency_code,
			'agencyName':    self.agency_name,
			'agencyWebsite': self.agency_url,
			'agencyAddress': self.agency_address,
			'agencyReports': agency_reports
		}
		return data

	@property
	def key(self):
		return self.agency_name

	@classmethod
	def fromDict(cls, data: Dict[str, Any]) -> 'SqlAgency':

		entity_data = {
			'agency_code':    data['agencyCode'],
			'agency_name':    data['agencyName'],
			'agency_url':     data['agencyUrl'],
			'agency_address': data['agencyAddress']
		}

		return cls(entity_data)

	@property
	def agency_code(self):
		raise NotImplementedError

	@property
	def agency_name(self):
		raise NotImplementedError

	@property
	def agency_url(self):
		raise NotImplementedError

	@property
	def agency_address(self):
		raise NotImplementedError

	@property
	def agency_reports(self):
		raise NotImplementedError


class SqlUnit:
	entity_type: str = 'unit'

	def __init__(self, *args, **kwargs):
		raise NotImplementedError

	def get(self, *args, **kwargs):
		raise NotImplementedError

	def select(self, *args, **kwargs):
		raise NotImplementedError

	def getPrimaryKey(self) -> Dict[str, Any]:
		raise NotImplementedError

	def exists(self, *args, **kwargs):
		raise NotImplementedError

	@property
	def key(self):
		return self.unit_string

	@db_session
	def toDict(self) -> Dict[str, str]:
		data = {
			'entityType': 'unit',
			'entityKey':  self.key,
			'unitString': self.unit_string,
			'unitCode':   self.unit_code
		}
		return data

	@classmethod
	def fromDict(cls, data: Dict[str, str]) -> 'SqlUnit':
		entity_data = {
			'unit_string': data['unitString'],
			'unit_code':   data.get('unitCode')
		}
		return cls(**entity_data)

	@property
	def unit_string(self):
		raise NotImplementedError

	@property
	def unit_code(self):
		raise NotImplementedError


class SqlScale:
	entity_type: str = 'scale'

	def __init__(self, *args, **kwargs):
		raise NotImplementedError

	def get(self, *args, **kwargs):
		raise NotImplementedError

	def select(self, *args, **kwargs):
		raise NotImplementedError

	def getPrimaryKey(self) -> Dict[str, Any]:
		raise NotImplementedError

	def exists(self, *args, **kwargs):
		raise NotImplementedError

	@property
	def key(self):
		return self.scale_string

	@db_session
	def toDict(self) -> Dict[str, Any]:
		scale_series = list()
		data = {
			'entityType':      'scale',
			'entityKey':       self.key,
			'scaleSeries':     scale_series,
			'scaleString':     self.scale_string,
			'scaleMultiplier': self.scale_multiplier
		}
		return data

	@classmethod
	def fromDict(cls, data: Dict[str, Any]) -> 'SqlScale':
		entity_data = {
			'scale_series':     data['scaleSeries'],
			'scale_string':     data['scaleString'],
			'scale_multiplier': data['scaleMultiplier']
		}
		return cls(**entity_data)

	@property
	def scale_series(self):
		raise NotImplementedError

	@property
	def scale_string(self):
		raise NotImplementedError

	@property
	def scale_multiplier(self):
		raise NotImplementedError
