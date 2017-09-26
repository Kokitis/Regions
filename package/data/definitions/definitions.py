
import os

from . import common


DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)))
DRIVE_FOLDER = os.path.join(os.getenv("USERPROFILE"), "Google Drive", "Data")

def _listAvailable():

	print("Agencies")
	for agency in common.agencies:
		print("\t{}\t{}".format(agency['code'], agency['name']))
	
	for ns in common.namespaces:
		print("\t{}\t{}".format(ns['code'], ns['name']))


def getDefinition(kind, key, available = False):
	"""	Retrieves a pre-defined definition of an entity.
		Parameters
		----------
			kind: {'agency', 'namespace'}
			key: str
				The code or name of an entity to retrieve.
			available: bool; default False
				Lists all available keys.
	"""
	result = None

	if kind == 'agency':
		for agency in common.agencies:
			agency_name = agency['name']
			agency_code = agency['code']

			if agency_code == key or agency_name == key:
				result = agency 
				break 
	elif kind == 'namespace':
		for ns in common.namespaces:
			ns_name = ns['name']
			ns_code = ns['code']

			if ns_code == key or ns_name == key:
				result = ns 
				break
	elif kind == 'file':
		
		for element in common.files:
			fn, *identifiers = element

			if key in identifiers:
				if fn.startswith('spreadsheets') or fn.startswith('namespaces'):
					fn = os.path.join(DATA_FOLDER, fn)
				elif not fn.startswith('C:'):
					fn = os.path.join(DRIVE_FOLDER, fn)
				result = fn
				break

	if result is None:
		message = "Missing definition for ('{}', '{}')".format(kind, key)
		raise ValueError(message)

	return result
