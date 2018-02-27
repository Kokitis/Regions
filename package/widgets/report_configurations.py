""" Contains default configurations for common tables used in the database such as
	the World Economic Outlook and Word Development Indicators
"""

from package.github import tabletools, timetools
import re

from package.utilities import TableApi
import os

import pandas
from .configuration_tools import *
from pprint import pprint
from functools import partial
from typing import Dict, Any, List, Union

ConfigurationValueTypes = Union[str,Dict[str,str], List[str], bool]
ConfigurationTypes = Dict[str,ConfigurationValueTypes]

pprint = partial(pprint, width = 180)


def getReport(report_key: str, filename: str) ->ConfigurationTypes:
	if report_key in {'WEO' or 'World Economic Outlook'}:
		report_configuration = getWorldEconomicOutlookConfiguration()
	elif report_key in {'WDI', 'World Economic Outlook'}:
		report_configuration = getWorldDevelopmentIndicatorsConfiguration(filename)
	else:
		raise NotImplementedError

	parsed_table = TableApi(**report_configuration)
	parsed_report = parsed_table.data
	return parsed_report


def getWorldEconomicOutlookConfiguration() ->ConfigurationTypes:
	configuration_filename = getFilename('weo_configuration')
	configuration = loadConfiguration(configuration_filename)

	if configuration is None:
		report: Dict[str, str] = {
			'reportName': 'World Economic Outlook, April 2017',
			'reportCode': '2017B',
			'reportDate': "April 2017",
			'reportUrl':  "http://www.imf.org/en/Publications/WEO/Issues/2017/04/04/world-economic-outlook-april-2017"
		}
		agency: Dict[str, str] = {
			'agencyCode':    "IMF",
			'agencyName':    "International Monetary Fund",
			'agencyUrl':     "http://www.imf.org/external/index.htm|http://www.imf.org/en/data",
			'agencyAddress': "700 19th Street, N.W., Washington, D.C. 20431|1900 Pennsylvania Ave NW, Washington, DC, 20431"
		}

		blacklist: List[str] = [
			'NGDP_RPCH', 'NGDP_R', 'NGDP_D', 'PPPSH', 'NID_NGDP',
			'NGSD_NGDP', 'PCPI', 'PCPIPCH', 'PCPIE', 'PCPIEPCH',
			'GGSB', 'GGSB_NPGDP', 'GGXONLB', 'GGXONLB_NGDP', 'BCA',
			'BCA_NGDPD', 'FLIBOR6'
		]

		configuration = {
			'report':         report,
			'agency':         agency,
			'namespace':      'ISO',
			'seriesTagMap':   {'LP': ['POP']},  # lambda row: ['POP'] if 'LP' in row.values else None,
			'blacklist':      blacklist,
			'jsonCompatible': False
			# 'saveTo': r"C:\Users\Progi\Documents\GitHub\Regions\package\test_api.json"
		}

		saveConfiguration(configuration, configuration_filename)

	return configuration


def getWorldDevelopmentIndicatorsConfiguration(filename):
	configuration_filename = getFilename('wdi_configuration')
	configuration = loadConfiguration(configuration_filename)
	if filename is None:
		filename = os.path.expanduser(
			'~\\Google Drive\\Region Data\\Global\\World Development Indicators\WDIEXCEL.xlsx')
	if configuration is None:
		whitelist: List[str] = [
			'PA.NUS.PPP.05', 'PA.NUS.PRVT.PP.05', 'NY.ADJ.NNTY.KD.ZG', 'NY.ADJ.NNTY.KD', 'NY.ADJ.NNTY.CD',
			'NY.ADJ.NNTY.PC.KD.ZG', 'NY.ADJ.NNTY.PC.KD', 'NY.ADJ.NNTY.PC.CD', 'NY.ADJ.DCO2.GN.ZS', 'NY.ADJ.DCO2.CD',
			'AG.LND.AGRI.ZS', 'AG.LND.AGRI.K2', 'EG.USE.COMM.CL.ZS', 'AG.LND.ARBL.ZS', 'AG.LND.ARBL.HA.PC',
			'AG.LND.ARBL.HA', 'MS.MIL.TOTL.TF.ZS', 'MS.MIL.TOTL.P1', 'MS.MIL.XPRT.KD', 'MS.MIL.MPRT.KD',
			'SP.DYN.CBRT.IN', 'SH.STA.BRTC.ZS', 'GC.DOD.TOTL.GD.ZS', 'GC.DOD.TOTL.CN', 'EN.ATM.CO2E.KD.GD',
			'EN.ATM.CO2E.PP.GD.KD', 'EN.ATM.CO2E.PP.GD', 'EN.ATM.CO2E.KT', 'EN.ATM.CO2E.PC', 'EN.CO2.ETOT.ZS',
			'EN.ATM.CO2E.GF.ZS', 'EN.ATM.CO2E.GF.KT', 'EN.ATM.CO2E.LF.ZS', 'EN.ATM.CO2E.LF.KT', 'EN.CO2.MANF.ZS',
			'EN.CO2.OTHX.ZS', 'EN.CO2.BLDG.ZS', 'EN.ATM.CO2E.SF.ZS', 'EN.ATM.CO2E.SF.KT', 'EN.CO2.TRAN.ZS',
			'EN.ATM.CO2E.EG.ZS', 'SE.COM.DURS', 'FP.CPI.TOTL', 'IC.REG.COST.PC.ZS', 'IC.EXP.COST.CD',
			'IC.IMP.COST.CD', 'AG.PRD.CROP.XD', 'BN.CAB.XOKA.GD.ZS', 'BN.CAB.XOKA.CD', 'SP.DYN.CDRT.IN',
			'PA.NUS.ATLS', 'NY.GDP.DISC.KN', 'NY.GDP.DISC.CN', 'IC.BUS.DFRN.XQ', 'IC.EXP.DOCS',
			'IC.IMP.DOCS', 'IC.BUS.EASE.XQ', 'SE.TER.CUAT.BA.ZS', 'SE.SEC.CUAT.LO.ZS', 'SE.SEC.CUAT.PO.ZS',
			'SE.PRM.CUAT.ZS', 'SE.TER.CUAT.ST.ZS', 'SE.SEC.CUAT.UP.ZS', 'SE.TER.CUAT.MS.ZS', 'SE.TER.CUAT.DO.ZS',
			'EG.USE.ELEC.KH.PC', 'EG.ELC.LOSS.ZS', 'EG.ELC.COAL.ZS', 'EG.ELC.HYRO.ZS', 'EG.ELC.NGAS.ZS',
			'EG.ELC.NUCL.ZS', 'EG.ELC.PETR.ZS', 'EG.ELC.FOSL.ZS', 'EG.ELC.RNWX.ZS', 'EG.ELC.RNWX.KH',
			'SL.EMP.TOTL.SP.ZS', 'SL.EMP.TOTL.SP.NE.ZS', 'SL.EMP.1524.SP.ZS', 'SL.EMP.1524.SP.NE.ZS', 'EG.IMP.CONS.ZS',
			'EG.USE.PCAP.KG.OE', 'EG.USE.COMM.GD.PP.KD', 'SE.XPD.PRIM.ZS', 'SE.XPD.SECO.ZS', 'SE.XPD.TERT.ZS',
			'NE.EXP.GNFS.ZS', 'NE.EXP.GNFS.KD.ZG', 'BX.GSR.GNFS.CD', 'NE.EXP.GNFS.KD', 'NE.EXP.GNFS.KN',
			'NE.EXP.GNFS.CN', 'NE.EXP.GNFS.CD', 'SP.DYN.TFRT.IN', 'BN.KLT.DINV.CD', 'BX.KLT.DINV.WD.GD.ZS',
			'BX.KLT.DINV.CD.WD', 'BM.KLT.DINV.WD.GD.ZS', 'BM.KLT.DINV.CD.WD', 'AG.LND.FRST.ZS', 'AG.LND.FRST.K2',
			'NY.GDP.MKTP.KD', 'NY.GDP.MKTP.KN', 'NY.GDP.MKTP.CN', 'NY.GDP.MKTP.CD', 'NY.GDP.MKTP.KD.ZG',
			'NY.GDP.PCAP.KD', 'NY.GDP.PCAP.KN', 'NY.GDP.PCAP.CN', 'NY.GDP.PCAP.CD', 'NY.GDP.PCAP.KD.ZG',
			'NY.GDP.PCAP.PP.KD', 'NY.GDP.PCAP.PP.CD', 'SL.GDP.PCAP.EM.KD', 'EG.GDP.PUSE.KO.PP.KD', 'EG.GDP.PUSE.KO.PP',
			'NY.GDP.MKTP.PP.KD', 'NY.GDP.MKTP.PP.CD', 'NY.GDP.MKTP.CN.AD', 'SI.POV.GINI', 'NY.GNP.MKTP.KD',
			'NY.GNP.MKTP.KN', 'NY.GNP.MKTP.CN', 'NY.GNP.MKTP.CD', 'NY.GNP.MKTP.KD.ZG', 'NY.GNP.PCAP.KD',
			'NY.GNP.PCAP.KN', 'NY.GNP.PCAP.CN', 'NY.GNP.PCAP.KD.ZG', 'NY.GNP.PCAP.CD', 'NY.GNP.PCAP.PP.KD',
			'NY.GNP.PCAP.PP.CD', 'NY.GNP.ATLS.CD', 'NY.GNP.MKTP.PP.KD', 'NY.GNP.MKTP.PP.CD', 'BX.GSR.MRCH.CD',
			'BM.GSR.MRCH.CD', 'SH.XPD.PCAP', 'SH.XPD.PCAP.PP.KD', 'SH.XPD.PRIV.ZS', 'SH.XPD.PUBL.ZS',
			'SH.XPD.PUBL.GX.ZS', 'SH.XPD.PUBL', 'SH.XPD.TOTL.ZS', 'EN.ATM.HFCG.KT.CE', 'TX.VAL.TECH.MF.ZS',
			'TX.VAL.TECH.CD', 'SH.MED.BEDS.ZS', 'NE.IMP.GNFS.ZS', 'NE.IMP.GNFS.KD.ZG', 'BM.GSR.GNFS.CD',
			'NE.IMP.GNFS.KD', 'NE.IMP.GNFS.KN', 'NE.IMP.GNFS.CN', 'NE.IMP.GNFS.CD', 'SH.STA.ACSN',
			'SH.H2O.SAFE.ZS', 'SI.DST.04TH.20', 'SI.DST.10TH.10', 'SI.DST.05TH.20', 'SI.DST.FRST.10',
			'SI.DST.FRST.20', 'SI.DST.02ND.20', 'SI.DST.03RD.20', 'IT.NET.USER.ZS', 'VC.IHR.PSRC.P5',
			'SM.POP.TOTL.ZS', 'SM.POP.TOTL', 'ST.INT.XPND.MP.ZS', 'ST.INT.XPND.CD', 'ST.INT.TRNX.CD',
			'ST.INT.TVLX.CD', 'ST.INT.ARVL', 'ST.INT.DPRT', 'ST.INT.RCPT.XP.ZS', 'ST.INT.RCPT.CD',
			'ST.INT.TRNR.CD', 'ST.INT.TVLR.CD', 'SL.TLF.CACT.FE.ZS', 'SL.TLF.CACT.FE.NE.ZS', 'SL.TLF.CACT.MA.ZS',
			'SL.TLF.CACT.MA.NE.ZS', 'SL.TLF.CACT.ZS', 'SL.TLF.CACT.NE.ZS', 'SL.TLF.TOTL.FE.ZS', 'SL.TLF.TOTL.IN',
			'AG.LND.TOTL.K2', 'FR.INR.LEND', 'SP.DYN.LE00.FE.IN', 'SP.DYN.LE00.MA.IN', 'SP.DYN.LE00.IN',
			'SH.MMR.RISK.ZS', 'SH.MMR.RISK', 'CM.MKT.LDOM.NO', 'CM.MKT.LCAP.GD.ZS', 'CM.MKT.LCAP.CD',
			'EN.ATM.METH.KT.CE', 'MS.MIL.XPND.ZS', 'MS.MIL.XPND.GD.ZS', 'MS.MIL.XPND.CN', 'SP.DYN.AMRT.FE',
			'SP.DYN.AMRT.MA', 'SP.DYN.IMRT.IN', 'GC.NLD.TOTL.GD.ZS', 'GC.NLD.TOTL.CN', 'SM.POP.NETM',
			'EN.ATM.NOXE.KT.CE', 'PA.NUS.FCRF', 'IP.PAT.NRES', 'IP.PAT.RESD', 'EN.POP.DNST',
			'SP.POP.GROW', 'EN.URB.LCTY', 'EN.URB.LCTY.UR.ZS', 'EN.URB.MCTY', 'EN.URB.MCTY.TL.ZS',
			'SP.POP.TOTL.FE.ZS', 'SP.POP.TOTL', 'PA.NUS.PPP', 'PA.NUS.PRVT.PP', 'PA.NUS.PPPC.RF',
			'IQ.WEF.PORT.XQ', 'IS.RRS.TOTL.KM', 'IS.RRS.GOOD.MT.K6', 'IS.RRS.PASG.KM', 'SL.TLF.CACT.FM.ZS',
			'SL.TLF.CACT.FM.NE.ZS', 'PX.REX.REER', 'FR.INR.RINR', 'SM.POP.REFG', 'SM.POP.REFG.OR',
			'EG.ELC.RNEW.ZS', 'GB.XPD.RSDV.GD.ZS', 'SP.POP.SCIE.RD.P6', 'SP.RUR.TOTL.ZS', 'SP.RUR.TOTL.ZG',
			'IP.JRN.ARTC.SC', 'BX.GSR.NFSV.CD', 'BM.GSR.NFSV.CD', 'EN.ATM.SF6G.KT.CE', 'GC.REV.SOCL.ZS',
			'GC.REV.SOCL.CN', 'SH.STA.SUIC.P5', 'AG.SRF.TOTL.K2', 'GC.TAX.TOTL.GD.ZS', 'GC.TAX.TOTL.CN',
			'EN.ATM.GHGT.ZG', 'EN.ATM.GHGT.KT.CE', 'IC.TAX.TOTL.CP.ZS', 'NE.TRD.GNFS.ZS', 'BG.GSR.NFSV.GD.ZS',
			'SL.UEM.TOTL.ZS', 'SL.UEM.TOTL.NE.ZS', 'SL.EMP.VULN.FE.ZS', 'SL.EMP.VULN.MA.ZS', 'SL.EMP.VULN.ZS',
			'SL.EMP.WORK.FE.ZS', 'SL.EMP.WORK.MA.ZS', 'SL.EMP.WORK.ZS', 'NV.IND.MANF.CD'
		]

		print("Preparing to import the World Development Indicators...")

		print("Loading data from ", filename)

		# data_sheet = tabletools.Table(filename, sheetname = 'Data')

		print("Loading notes sheet...")
		notes_sheet = tabletools.Table(filename, sheetname = 'Country-Series')

		print("Loading series sheet...")
		series_sheet = tabletools.Table(filename, sheetname = 'Series')

		series_description_map = dict()
		series_tag_map = dict()

		def _getWDIUnits(unitstring):

			# string = [i.strip() for i in string.split('\n')]
			regex = re.compile("\(([^)]+)\)$")
			match = regex.search(unitstring)
			if match:
				return match.groups()[0]
			else:
				return ""

		series_unit_map = dict()

		print("Parsing metadata...")

		for index, row in enumerate(series_sheet):
			subject_code = row['Series Code']
			subject_name = row['Indicator Name']

			definition = row['Long definition']
			limitations = row['Limitations and exceptions']
			methodology = row['Statistical concept and methodology']
			relevance = row['Development relevance']

			series_description_map[subject_code] = definition
			_unit = _getWDIUnits(subject_name)
			_tags = list()
			if not isinstance(limitations, float):
				_tags.append(("Limitations", str(limitations)))
			if not isinstance(methodology, float):
				_tags.append(("Methodology", str(methodology)))
			if not isinstance(relevance, float):
				_tags.append(("Development Relevance", str(relevance)))

			_tags = ['|'.join(i) for i in _tags]
			series_tag_map[subject_code] = _tags
			series_unit_map[subject_code] = _unit

		series_notes_map = dict()
		print("Parsings notes sheet...")
		for index, row in enumerate(notes_sheet):
			region_code = row['CountryCode']
			subject_code = row['SeriesCode']
			string = row['DESCRIPTION']

			series_notes_map["{}|{}".format(region_code, subject_code)] = string

		report: Dict[str, str] = {
			'name':        "World Development Indicators",
			'code':        "WDI",
			'publishDate': "2017-09-15",
			'url':         "https://data.worldbank.org/data-catalog/world-development-indicators",
		}

		agency: Dict[str, str] = {
			'code':    'WB',
			'name':    'World Bank',
			'url':     "http://data.worldbank.org",
			# 'wiki': "https://en.wikipedia.org/wiki/World_Bank"
			'address': "1818 H Street, NW Washington, DC 20433 USA"
		}

		configuration = {
			'report':               report,
			'agency':               agency,
			'regionNameColumn':     "Country Name",
			'regionCodeColumn':     "Country Code",
			'subjectNameColumn':    "Indicator Name",
			'subjectCodeColumn':    "Indicator Code",
			'whitelist':            whitelist,
			'seriesNotesMap':       series_notes_map,
			'seriesDescriptionMap': series_description_map,
			'seriesTagMap':         series_tag_map,
			'seriesUnitMap':        series_unit_map
		}

		saveConfiguration(configuration, configuration_filename)
	return configuration


def addWorldPopulationProspects(filename:str)->ConfigurationTypes:
	# For reference
	configuration_filename = getFilename('wpp_configuration')
	configuration = loadConfiguration(configuration_filename)

	if configuration is None:
		subject_keymap: Dict[str, str] = {
			'ESTIMATES':           'POP.EST',
			'MEDIUM VARIANT':      'POP.PROJ.MID',
			'HIGH VARIANT':        'POP.PROJ.MAX',
			'LOW VARIANT':         'POP.PROJ.MIN',
			'CONSTANT-FERTILITY':  'POP.PROJ.CONST.FERT',
			'ZERO-MIGRATION':      'POP.PROJ.ZERO',
			'NO CHANGE':           'POP.PROJ.STATIC',
			'MOMENTUM':            'POP.PROJ.MOM',
			'INSTANT-REPLACEMENT': 'POP.PROJ.INST',
			'CONSTANT-MORTALITY':  'POP.PROJ.CONST.MORT'
		}

		table_dict = pandas.read_excel(filename, sheetname = None, skiprows = 16)  # Creates a dict of dataframes.
		table_dict.pop('NOTES')
		notes_table = tabletools.Table(filename, sheetname = 'NOTES')
		print("Extracting notes...")
		notes_dict = dict()

		for row in notes_table:
			regex = re.compile("[(](?P<num>.*)[)](?P<char>.*)")
			match = regex.search(row[0])
			if match:
				match = match.groupdict()

				notes_dict[match['num']] = match['char'].strip()

		print("Configuring table...")

		for subject_name, sheet in table_dict.items():
			# print(subject_name, '\t', sheet.columns)
			sheet.columns = [(i[1:] if i.startswith("'") else i) for i in sheet.columns]
			subject_code = subject_keymap[subject_name]
			notes_values = sheet['Notes'].values
			sheet['subjectCode'] = [subject_code for _ in notes_values]
			sheet['subjectName'] = [subject_name for _ in notes_values]
			sheet['seriesNotes'] = [(notes_dict.get(i) if isinstance(i, str) else None) for i in notes_values]
			sheet['regionCode'] = ["{:>03}".format(i) for i in sheet['Country code'].values]

		print("Combining table...")
		full_table = pandas.concat(table_dict.values())  # instead of adding another import statement pandas directly.

		series_description_map: Dict[str, str] = {
			'POP.PROJ.MID':
								   """Medium fertility variant, 2015 - 2100|"""
								   """Total fertility in high-fertility countries is generally assumed to decline at an average pace of nearly one child per decade starting in 2005 or later. """
								   """Consequently, some of these countries do not reach replacement level by 2050. """
								   """Total fertility in medium-fertility countries is assumed to reach replacement level before 2050. """
								   """Total fertility in low-fertility countries is generally assumed to remain below the replacement level during the projection period, """
								   """reaching by 2045-2050 the total fertility of the cohort of women born in the early 1960s or, if """
								   """that information is lacking, reaching 1.7 children per woman if current total fertility is below 1.5 children per woman or 1.9 children """
								   """per woman if current total fertility is equal or higher than 1.5 children per woman.""",
			'POP.PROJ.MAX':
								   """High fertility variant, 2015 - 2100|"""
								   """Total fertility in high and medium-fertility countries remains above the total fertility in """
								   """the medium-fertility assumption and eventually reaches a value 0.5 children above that """
								   """reached by total fertility in the mediumfertility assumption in 2045-2050. """
								   """For low-fertility countries, total fertility eventually reaches a value 0.4 children above that """
								   """reached by total fertility in the mediumfertility assumption in 2045-2050.""",
			'POP.PROJ.MIN':
								   """Low fertility variant, 2015 - 2100|"""
								   """Total fertility in high and medium-fertility countries remains below the total fertility in """
								   """the medium-fertility assumption and eventually reaches a value 0.5 children below that """
								   """reached by total fertility in the mediumfertility assumption in 2045-2050. """
								   """ For low-fertility countries, total fertility eventually reaches a value 0.4 children below that """
								   """ reached by total fertility in the mediumfertility assumption in 2045-2050. """,
			'POP.PROJ.CONST.FERT': "Constant-fertility variant, 2015 - 2100|For each country, total fertility remains constant at the level estimated for 1995-2000.",
			'POP.PROJ.INST':
								   """Instant-replacement-fertility variant, 2015 - 2100|"""
								   """For each country and each quinquennium of the """
								   """projection period (2000-2050), total fertility is set """
								   """to a level that ensures a net reproduction rate of """
								   """one. That is, total fertility is set to the level that """
								   """would ensure population replacement in the long """
								   """run in light of the sex ratio at birth and level of """
								   """mortality of the country concerned at each particular period.""",
			'POP.PROJ.ZERO':       "Zero-migration variant, 2015 - 2100|For each country, international migration is set to zero for the period 2000-2050.",
			'POP.PROJ.MOM':        "Momentum variant (instant-replacement-fertility, constant-mortality and zero-migration), 2015 - 2100",
			'POP.PROJ.STATIC':     "No change variant (constant-fertility and constant-mortality), 2015 - 2100",
			'POP.PROJ.CONST.MORT': "Constant-mortality variant, 2015 - 2100"
		}

		# series_unit_map = defaultdict(lambda: 'Thousand')
		# series_scale_map = defaultdict(lambda: 'Persons')
		series_unit_map = {k: 'Thousand' for k in series_description_map.keys()}
		series_scale_map = {k: 'Persons' for k in series_description_map.keys()}
		report: Dict[str, str] = {
			'name':        "World Population Prospects, The 2017 Revision",
			'code':        "WPP2017",
			'agency':      'United Nations',
			'publishDate': "2017-06-21",
			'url':         "https://esa.un.org/unpd/wpp/Download/Standard/Population/"
		}

		agency: Dict[str, str] = {
			'code':    'UN',
			'name':    'United Nations',
			'url':     'http://www.un.org/en/index.html',
			'address': "902 Broadway, 4th Floor New York, NY 10010"
		}

		configuration = {
			'report':               report,
			'agency':               agency,
			'seriesNameColumn':     'subjectName',
			'seriesCodeColumn':     'subjectCode',
			'regionCodeColumn':     'regionCode',
			'regionNameColumn':     'Region, subregion, country or area *',

			'namespace':            'ISO',

			'seriesUnitMap':        series_unit_map,
			'seriesScaleMap':       series_scale_map,
			'seriesDescriptionMap': series_description_map
		}
		pprint(configuration)
		saveConfiguration(configuration, configuration_filename)
		configuration['filename'] = full_table

	return configuration
