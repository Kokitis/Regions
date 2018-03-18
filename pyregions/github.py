import os
import sys

github_folder = os.path.join(os.getenv("USERPROFILE"), "Documents", "Github")

sys.path.append(github_folder)

# noinspection PyUnresolvedReferences
from pprint import pprint
from functools import partial
pprint = partial(pprint, width = 200)
tabletools = numbertools = timetools = None # So pylint ignores the unresolved references.
# noinspection PyUnresolvedReferences
from pytools import tabletools, numbertools, timetools

