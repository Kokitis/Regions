import os
import json
import yaml
def getFilename(basename):
	path = os.path.dirname(__file__)
	filename = os.path.join(path, 'configuration_files', basename)
	return filename


def saveConfiguration(config, filename):
	"""

	Parameters
	----------
	configuration: dict<>
	filename: str

	Returns
	-------

	"""
	import yaml
	import json

	with open(filename + '.json', 'w') as file1:
		try:
			file1.write(json.dumps(config, indent = 4, sort_keys = True))
		except Exception as exception:
			for key, value in config.items():
				print(key, '\t', type(value))
			raise exception
	with open(filename + '.yaml', 'w') as file2:
		file2.write(yaml.dump(config, default_flow_style = False, indent = 4))


def loadConfiguration(basename):
	"""

	Parameters
	----------
	basename: str

	Returns
	-------

	"""
	json_filename = basename + '.json'
	yaml_filename = basename + '.yaml'

	if os.path.exists(json_filename) and os.path.getsize(json_filename) > 0:
		with open(json_filename, 'r') as file1:
			configuration = json.loads(file1.read())
	elif os.path.exists(yaml_filename) and os.path.getsize(yaml_filename) > 0:
		configuration = yaml.load(yaml_filename)
	else:
		configuration = None

	return configuration