""" Contains default configurations for common tables used in the database such as
	the World Economic Outlook and Word Development Indicators
"""
from functools import partial

from ...data import getDefinition
from ...github import tabletools
from .._converters import ConvertTable
from ._world_population_prospects import addWorldPopulationProspects
def addReport(dataset, string, *args):
	""" Adds the selected report to the dataset. """

	if string in {'WEO', 'World Economic Outlook'}:
		result = _addWorldEconomicOutlook(dataset)
	elif string in {'WDI', 'World Development Indicators'}:
		result = _addWorldDevelopmentIndicators(dataset)
	elif string.startswith('WPP'):
		result = addWorldPopulationProspects(dataset, *args)
	else:
		message = "Incorect report key: ''".format(string)
		raise ValueError(message)
	return result
def _addWorldEconomicOutlook(dataset):
	"""
	"""
	filename =  getDefinition('file', 'World Economic Outlook')

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

	namespace = 'ISO'
	ConvertTable(dataset, filename, namespace, report, blacklist = blacklist, seriesTagMap = tag_map)

def _addWorldDevelopmentIndicators(dataset, filename = None):
	""" Parameters
		----------
		dataset: ImportDatabase
			The database to add the report to.
		filename: str; default None
			Path to a newly-downloaded version of the table. 
	"""
	print("Preparing to import the World Development Indicators...")
	if filename is None:
		filename = getDefinition('file', 'World Development Indicators')

	data_sheet = tabletools.Table(filename, sheetname = 'Data')
	notes_sheet = tabletools.Table(filename, sheetname = 'Country-Series')

	series_sheet = tabletools.Table(filename, sheetname = 'Series')

	_series_description_map = dict()
	_series_tag_map = dict()
	for row in series_sheet:
		subject_code = row['Series Code']

		definition = row['Long definition']
		limitations=row['Limitations and exceptions']
		methodology = row['Statistical concept and methodology']
		relevance = row['Development relevance']

		_series_description_map[subject_code] = definition
		_tags = [
			("Definition", str(definition)),
			("Limitations", str(limitations)),
			("Methodology", str(methodology)),
			("Development Relevance", str(relevance))
		]
		_tags = ['|'.join(i) for i in _tags]
		_series_tag_map[subject_code] = _tags

	def _series_tag_map_func_mapper(mapper, region_code, subject_code):
		return mapper.get(subject_code)

	_series_tag_map_func = partial(_series_tag_map_func_mapper, _series_tag_map)

	series_notes_map = dict()
	for row in notes_sheet:
		region_code = row['CountryCode']
		subject_code = row['SeriesCode']
		string = row['DESCRIPTION']

		series_notes_map[(region_code, subject_code)] = string
		

	report = {
		'name': "World Development Indicators",
		'code': "WDI",
		'publishDate': "2017-09-15",
		'url': "https://data.worldbank.org/data-catalog/world-development-indicators",
		'agency': 'World Bank'
	}

	whitelist = [
		'PA.NUS.PPP.05',        'PA.NUS.PRVT.PP.05',    'NY.ADJ.NNTY.KD.ZG',    'NY.ADJ.NNTY.KD',       'NY.ADJ.NNTY.CD', 
		'NY.ADJ.NNTY.PC.KD.ZG', 'NY.ADJ.NNTY.PC.KD',    'NY.ADJ.NNTY.PC.CD',    'NY.ADJ.DCO2.GN.ZS',    'NY.ADJ.DCO2.CD', 
		'AG.LND.AGRI.ZS',       'AG.LND.AGRI.K2',       'EG.USE.COMM.CL.ZS',    'AG.LND.ARBL.ZS',       'AG.LND.ARBL.HA.PC', 
		'AG.LND.ARBL.HA',       'MS.MIL.TOTL.TF.ZS',    'MS.MIL.TOTL.P1',       'MS.MIL.XPRT.KD',       'MS.MIL.MPRT.KD', 
		'SP.DYN.CBRT.IN',       'SH.STA.BRTC.ZS',       'GC.DOD.TOTL.GD.ZS',    'GC.DOD.TOTL.CN',       'EN.ATM.CO2E.KD.GD', 
		'EN.ATM.CO2E.PP.GD.KD', 'EN.ATM.CO2E.PP.GD',    'EN.ATM.CO2E.KT',       'EN.ATM.CO2E.PC',       'EN.CO2.ETOT.ZS', 
		'EN.ATM.CO2E.GF.ZS',    'EN.ATM.CO2E.GF.KT',    'EN.ATM.CO2E.LF.ZS',    'EN.ATM.CO2E.LF.KT',    'EN.CO2.MANF.ZS', 
		'EN.CO2.OTHX.ZS',       'EN.CO2.BLDG.ZS',       'EN.ATM.CO2E.SF.ZS',    'EN.ATM.CO2E.SF.KT',    'EN.CO2.TRAN.ZS', 
		'EN.ATM.CO2E.EG.ZS',    'SE.COM.DURS',          'FP.CPI.TOTL',          'IC.REG.COST.PC.ZS',    'IC.EXP.COST.CD', 
		'IC.IMP.COST.CD',       'AG.PRD.CROP.XD',       'BN.CAB.XOKA.GD.ZS',    'BN.CAB.XOKA.CD',       'SP.DYN.CDRT.IN', 
		'PA.NUS.ATLS',          'NY.GDP.DISC.KN',       'NY.GDP.DISC.CN',       'IC.BUS.DFRN.XQ',       'IC.EXP.DOCS', 
		'IC.IMP.DOCS',          'IC.BUS.EASE.XQ',       'SE.TER.CUAT.BA.ZS',    'SE.SEC.CUAT.LO.ZS',    'SE.SEC.CUAT.PO.ZS', 
		'SE.PRM.CUAT.ZS',       'SE.TER.CUAT.ST.ZS',    'SE.SEC.CUAT.UP.ZS',    'SE.TER.CUAT.MS.ZS',    'SE.TER.CUAT.DO.ZS', 
		'EG.USE.ELEC.KH.PC',    'EG.ELC.LOSS.ZS',       'EG.ELC.COAL.ZS',       'EG.ELC.HYRO.ZS',       'EG.ELC.NGAS.ZS', 
		'EG.ELC.NUCL.ZS',       'EG.ELC.PETR.ZS',       'EG.ELC.FOSL.ZS',       'EG.ELC.RNWX.ZS',       'EG.ELC.RNWX.KH', 
		'SL.EMP.TOTL.SP.ZS',    'SL.EMP.TOTL.SP.NE.ZS', 'SL.EMP.1524.SP.ZS',    'SL.EMP.1524.SP.NE.ZS', 'EG.IMP.CONS.ZS', 
		'EG.USE.PCAP.KG.OE',    'EG.USE.COMM.GD.PP.KD', 'SE.XPD.PRIM.ZS',       'SE.XPD.SECO.ZS',       'SE.XPD.TERT.ZS', 
		'NE.EXP.GNFS.ZS',       'NE.EXP.GNFS.KD.ZG',    'BX.GSR.GNFS.CD',       'NE.EXP.GNFS.KD',       'NE.EXP.GNFS.KN', 
		'NE.EXP.GNFS.CN',       'NE.EXP.GNFS.CD',       'SP.DYN.TFRT.IN',       'BN.KLT.DINV.CD',       'BX.KLT.DINV.WD.GD.ZS', 
		'BX.KLT.DINV.CD.WD',    'BM.KLT.DINV.WD.GD.ZS', 'BM.KLT.DINV.CD.WD',    'AG.LND.FRST.ZS',       'AG.LND.FRST.K2', 
		'NY.GDP.MKTP.KD',       'NY.GDP.MKTP.KN',       'NY.GDP.MKTP.CN',       'NY.GDP.MKTP.CD',       'NY.GDP.MKTP.KD.ZG', 
		'NY.GDP.PCAP.KD',       'NY.GDP.PCAP.KN',       'NY.GDP.PCAP.CN',       'NY.GDP.PCAP.CD',       'NY.GDP.PCAP.KD.ZG', 
		'NY.GDP.PCAP.PP.KD',    'NY.GDP.PCAP.PP.CD',    'SL.GDP.PCAP.EM.KD',    'EG.GDP.PUSE.KO.PP.KD', 'EG.GDP.PUSE.KO.PP', 
		'NY.GDP.MKTP.PP.KD',    'NY.GDP.MKTP.PP.CD',    'NY.GDP.MKTP.CN.AD',    'SI.POV.GINI',          'NY.GNP.MKTP.KD', 
		'NY.GNP.MKTP.KN',       'NY.GNP.MKTP.CN',       'NY.GNP.MKTP.CD',       'NY.GNP.MKTP.KD.ZG',    'NY.GNP.PCAP.KD', 
		'NY.GNP.PCAP.KN',       'NY.GNP.PCAP.CN',       'NY.GNP.PCAP.KD.ZG',    'NY.GNP.PCAP.CD',       'NY.GNP.PCAP.PP.KD', 
		'NY.GNP.PCAP.PP.CD',    'NY.GNP.ATLS.CD',       'NY.GNP.MKTP.PP.KD',    'NY.GNP.MKTP.PP.CD',    'BX.GSR.MRCH.CD', 
		'BM.GSR.MRCH.CD',       'SH.XPD.PCAP',          'SH.XPD.PCAP.PP.KD',    'SH.XPD.PRIV.ZS',       'SH.XPD.PUBL.ZS', 
		'SH.XPD.PUBL.GX.ZS',    'SH.XPD.PUBL',          'SH.XPD.TOTL.ZS',       'EN.ATM.HFCG.KT.CE',    'TX.VAL.TECH.MF.ZS', 
		'TX.VAL.TECH.CD',       'SH.MED.BEDS.ZS',       'NE.IMP.GNFS.ZS',       'NE.IMP.GNFS.KD.ZG',    'BM.GSR.GNFS.CD', 
		'NE.IMP.GNFS.KD',       'NE.IMP.GNFS.KN',       'NE.IMP.GNFS.CN',       'NE.IMP.GNFS.CD',       'SH.STA.ACSN', 
		'SH.H2O.SAFE.ZS',       'SI.DST.04TH.20',       'SI.DST.10TH.10',       'SI.DST.05TH.20',       'SI.DST.FRST.10', 
		'SI.DST.FRST.20',       'SI.DST.02ND.20',       'SI.DST.03RD.20',       'IT.NET.USER.ZS',       'VC.IHR.PSRC.P5', 
		'SM.POP.TOTL.ZS',       'SM.POP.TOTL',          'ST.INT.XPND.MP.ZS',    'ST.INT.XPND.CD',       'ST.INT.TRNX.CD', 
		'ST.INT.TVLX.CD',       'ST.INT.ARVL',          'ST.INT.DPRT',          'ST.INT.RCPT.XP.ZS',    'ST.INT.RCPT.CD', 
		'ST.INT.TRNR.CD',       'ST.INT.TVLR.CD',       'SL.TLF.CACT.FE.ZS',    'SL.TLF.CACT.FE.NE.ZS', 'SL.TLF.CACT.MA.ZS', 
		'SL.TLF.CACT.MA.NE.ZS', 'SL.TLF.CACT.ZS',       'SL.TLF.CACT.NE.ZS',    'SL.TLF.TOTL.FE.ZS',    'SL.TLF.TOTL.IN', 
		'AG.LND.TOTL.K2',       'FR.INR.LEND',          'SP.DYN.LE00.FE.IN',    'SP.DYN.LE00.MA.IN',    'SP.DYN.LE00.IN', 
		'SH.MMR.RISK.ZS',       'SH.MMR.RISK',          'CM.MKT.LDOM.NO',       'CM.MKT.LCAP.GD.ZS',    'CM.MKT.LCAP.CD', 
		'EN.ATM.METH.KT.CE',    'MS.MIL.XPND.ZS',       'MS.MIL.XPND.GD.ZS',    'MS.MIL.XPND.CN',       'SP.DYN.AMRT.FE', 
		'SP.DYN.AMRT.MA',       'SP.DYN.IMRT.IN',       'GC.NLD.TOTL.GD.ZS',    'GC.NLD.TOTL.CN',       'SM.POP.NETM', 
		'EN.ATM.NOXE.KT.CE',    'PA.NUS.FCRF',          'IP.PAT.NRES',          'IP.PAT.RESD',          'EN.POP.DNST', 
		'SP.POP.GROW',          'EN.URB.LCTY',          'EN.URB.LCTY.UR.ZS',    'EN.URB.MCTY',          'EN.URB.MCTY.TL.ZS', 
		'SP.POP.TOTL.FE.ZS',    'SP.POP.TOTL',          'PA.NUS.PPP',           'PA.NUS.PRVT.PP',       'PA.NUS.PPPC.RF', 
		'IQ.WEF.PORT.XQ',       'IS.RRS.TOTL.KM',       'IS.RRS.GOOD.MT.K6',    'IS.RRS.PASG.KM',       'SL.TLF.CACT.FM.ZS', 
		'SL.TLF.CACT.FM.NE.ZS', 'PX.REX.REER',          'FR.INR.RINR',          'SM.POP.REFG',          'SM.POP.REFG.OR', 
		'EG.ELC.RNEW.ZS',       'GB.XPD.RSDV.GD.ZS',    'SP.POP.SCIE.RD.P6',    'SP.RUR.TOTL.ZS',       'SP.RUR.TOTL.ZG', 
		'IP.JRN.ARTC.SC',       'BX.GSR.NFSV.CD',       'BM.GSR.NFSV.CD',       'EN.ATM.SF6G.KT.CE',    'GC.REV.SOCL.ZS', 
		'GC.REV.SOCL.CN',       'SH.STA.SUIC.P5',       'AG.SRF.TOTL.K2',       'GC.TAX.TOTL.GD.ZS',    'GC.TAX.TOTL.CN', 
		'EN.ATM.GHGT.ZG',       'EN.ATM.GHGT.KT.CE',    'IC.TAX.TOTL.CP.ZS',    'NE.TRD.GNFS.ZS',       'BG.GSR.NFSV.GD.ZS', 
		'SL.UEM.TOTL.ZS',       'SL.UEM.TOTL.NE.ZS',    'SL.EMP.VULN.FE.ZS',    'SL.EMP.VULN.MA.ZS',    'SL.EMP.VULN.ZS', 
		'SL.EMP.WORK.FE.ZS',    'SL.EMP.WORK.MA.ZS',    'SL.EMP.WORK.ZS'
	]

	configuration = {
		'regionNameColumn': "Country Name",
		'regionCodeColumn': "Country Code",
		'subjectNameColumn': "Indicator Name",
		'subjectCodeColumn': "Indicator Code",
		'notesMap': series_notes_map,
		'whitelist': whitelist,
		'seriesDescriptionMap': _series_description_map,
		'seriesTagMap': _series_tag_map_func
	}

	ConvertTable(dataset, data_sheet, namespace = 'ISO', report = report, **configuration)


def _defaultMadisonHistoricalTables(dataset):
	pass

