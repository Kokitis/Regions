from pony.orm import *
from pony.orm.core import Entity, EntityMeta, EntityIter
import pony.orm.core
from pprint import pprint

if __name__ == "__main__":
	create = True
	_database = Database()


	class Region(_database.Entity):
		@classmethod
		def getPrimaryKey(cls):
			return 'id'
		@classmethod
		def get_primary_key(cls):
			return 'id'
	_database.bind("sqlite", ":memory:", create_db = create)  # create_tables
	_database.generate_mapping(create_tables = create)
	with db_session:
		r = Region()

		pprint(dir(r))