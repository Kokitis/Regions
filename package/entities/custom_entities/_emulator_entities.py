from ._abstract_entities import AbstractRegion, AbstractSeries

class EmulatorRegion(AbstractRegion):
	""" Defines a class that should operate as a drop-in replacement
		for any other Region entity. 
	"""

	def __init__(self, template, db = None, **kwargs):
		"""
			Parameters
			----------
				db: pony.orm.Database; default None
					If provided, the emulator object will be able to
					use classmethods as implemented by the
					basic database entities (ex. .get(), .select())
				region: Region, dict<>
					A Region object or a dict with valid Region arguments. 
			
			Keyword Arguments
			-----------------
				Any valid argument that can be used to create a Region entity.
		"""
		arguments = self._parseInputArguments(template, **kwargs)
		self._series 		= arguments['series']
		self._name 			= arguments['name']
		self._identifiers 	= arguments['identifiers']
		self._subregions 	= arguments['subRegions']
		self._parentRegion 	= arguments['parentRegion']

		if db is not None:
			self.get = db.Region.get 
			self.select = db.Region.select
		else:
			self.get = self._get 
			self.select = self._select

	@staticmethod
	def _parseInputArguments(region, **kwargs):
		if region:
			arguments = dict()
			arguments['name'] 		= region.name
			arguments['series'] 	= region.series
			arguments['identifiers']= region.identifiers
			arguments['subRegions'] = region.subRegions
			arguments['parentRegion'] = region.parentRegion

		else:
			arguments = {i:None for i in ['name', 'series', 'identifiers', 'subRegions', 'parentRegion']}
		
		arguments = {**arguments, **kwargs}

		return arguments
	@property
	def name(self):
		return self._name

	@property
	def series(self):
		return self._series

	@property
	def identifiers(self):
		return self._identifiers

	@property
	def subRegions(self):
		return self._subregions

	@property
	def parentRegion(self):
		return self._parentRegion

	@classmethod
	def _get(cls, *args, **kwargs):
		raise NotImplementedError

	@classmethod 
	def _select(cls, *args, **kwargs):
		raise NotImplementedError


class EmulatorSeries(AbstractSeries):
	""" Defines a Series class that should work as a drop-in replacement for
		any other Serise entity. 
	"""
	def __init__(self, template, values = None, db = None, **kwargs):
		"""
			Stores the combination of multiple series.
			Parameters
			----------
				template: Series
					The series-specific values will be populated from the template.
				values: list; default None
					If 'values' is not provided, the template values will be used.
			Keyword Arguments
			-----------------
				*'region': A region to assign to the composite series. Ex. EU
				
				Keywords that may come from the template series
				* 'report'
				* 'notes'
				* 'units'
				* 'scale'
				* 'commonCode'
				* 'name'
				* 'code'
		"""
		if values is None:
			values = list(template)

		_input_arguments = self._parseAttributes(template, **kwargs)

		self._code 	 = _input_arguments['code']
		self._report = _input_arguments['report']
		self._region = _input_arguments['region']
		self._name 	 = _input_arguments['name']
		self._tags = _input_arguments['tags']
		self._notes = _input_arguments['notes']
		self._unit = _input_arguments['units']
		self._scale = _input_arguments['scale']

		self._values = self._parseInputValues(values)

		if db is not None:
			self.get = db.Series.get 
			self.select = db.Series.select 
		else:
			self.get = self._get 
			self.select = self._select


	def __repr__(self):
		string = "SeriesEmulator['{}', {}, {}]".format(self.code, self.region, self.report)
		return string
	
	@staticmethod
	def _parseAttributes(template, **kwargs):
		""" parses the template series and kwargs in order to assign values to 
			each attribute related to this series.

		"""
		if template:
			code 	= template.code 
			name 	= template.name 

			tags    = template.tags
			notes 	= template.notes 
			units 	= template.unit
			scale 	= template.scale
			report 	= template.report

			if 'region' in kwargs:
				region = kwargs['region']
			else:
				region 	= template.region
			
			result = {
				'code': code,
				'name': name,
				'report': report,
				'region': region,
				'tags': tags,
				'notes': notes,
				'units': units,
				'scale': scale
			}

		else:
			result = dict()
			"""
			code = kwargs.get('code')
			name = kwargs.get('name')
			report=kwargs.get('report')
			region=kwargs.get('region')

			notes = kwargs.get('notes')
			units = kwargs.get('units')
			scale = kwargs.get('scale')
			tags = kwargs.get('tags', [])
			"""
		result = {**result, **kwargs}


		return result
	
	@staticmethod
	def _parseInputValues(values):
		""" Parses the input values.
		"""
		values = [i for i in values]
		return values

	@classmethod
	def emulate(cls, template, values, **kwargs):
		return cls(template, values, **kwargs)

	@property
	def values(self):
		return self._values

	@property
	def code(self):
		return self._code 

	@property
	def region(self):
		return self._region

	@property
	def report(self):
		return self._report

	@property
	def name(self):
		return self._name

	@property
	def notes(self):
		return self._notes

	@property 
	def tags(self):
		return self._tags

	@property
	def unit(self):
		return self._unit

	@property
	def scale(self):
		return self._scale

	@property
	def strvalues(self):
		return "||".join(["{}|{}".format(x, y) for x, y in self.values])

	@classmethod 
	def _get(cls, *args, **kwargs):
		raise NotImplementedError

	@classmethod
	def _select(cls, *arsg, **kwargs):
		raise NotImplementedError
