from .._data_containers import DataRegion

class CompositeRegion(DataRegion):
	""" A region composed of a number of smaller regions.
		Parameters
		----------
		union_data = dict<>
			* 'unionName': str
			* 'unionCode': str
		regions: list<dict>, list<DataRegion>
			* 'entityType':        'region',
			* 'entityKey':         self.key,
			* 'regionType':        self.regionType,
			* 'regionName':        self.name,

			# Relations

			* 'regionIdentifiers': region_identifiers,
			* 'regionParent':      parent_region,
			* 'regionSubregions':  subregions,
			* 'regionSeries':      region_series,
			* 'regionTags':        list()
		Keyword Arguments
		-----------------
		name: str [Required]
			The name of the composite region

		Notes
		-----
			Composite Regions are only generated when requested.


	"""
	entity_type = 'union'

	def __init__(self, union_data, regions, **kwargs):
		self.members = regions
		if isinstance(regions[0], list):
			regions = [DataRegion(i) for i in regions]

		union_identifiers = [union_data['unionCode'] + kwargs.get('identifiers', [])]
		union_subregions = [i.key for i in regions]
		region_key = union_data['unionCode']
		union_series = self._combineMemberSeries(region_key, regions)

		composite_series_data = {
			'entityType': 'region',
			'entityKey': union_data['unionCode'],
			'regionType': 'union',
			'regionName': union_data['unionName'],

			'regionIdentifiers': union_identifiers,
			'regionParent': None,
			'regionSubregions': union_subregions,
			'regionSeries': union_series,
			'regionTags': list()

		}
		super().__init__(composite_series_data)

	def __str__(self):
		string = "CompositeRegion({})".format(self.data['regionName'])
		return string

	def _combineMemberSeries(self, region_key, regions):
		raise NotImplementedError