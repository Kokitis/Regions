from .._converters import ConvertTable
def _addWorldEconomicOutlook(dataset, filename):
	"""
	"""

	report = {
		'agency': 'IMF',
		'name': 'World Economic Outlook, April 2017',
		'code': 'WEO2017B',
		'publishDate': "April 2017",
		'url': "http://www.imf.org/en/Publications/WEO/Issues/2017/04/04/world-economic-outlook-april-2017"
	}

	blacklist = [
		'NGDP_RPCH', 'NGDP_R', 'NGDP_D', 'PPPSH', 'NID_NGDP',
		'NGSD_NGDP','PCPI','PCPIPCH', 'PCPIE', 'PCPIEPCH',
		'GGSB', 'GGSB_NPGDP', 'GGXONLB', 'GGXONLB_NGDP', 'BCA',
		'BCA_NGDPD'
	]

	tag_map = lambda rc,sc: 'POP' if sc == 'LP' else None

	ConvertTable(dataset, filename, 'ISO', report, blacklist = blacklist, seriesTagMap = tag_map)

	return None