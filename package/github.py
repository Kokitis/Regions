import os
import sys

github_folder = os.path.join(os.getenv("USERPROFILE"), "Documents", "Github")

sys.path.append(github_folder)

import pytools.tabletools as tabletools
import pytools.timetools as timetools
import pytools.numbertools as numbertools
from texttable import Texttable

__all__ = [tabletools, timetools, numbertools]