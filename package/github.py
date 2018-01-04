import os
import sys

github_folder = os.path.join(os.getenv("USERPROFILE"), "Documents", "Github")

sys.path.append(github_folder)

# noinspection PyUnresolvedReferences
from pytools import tabletools, numbertools, timetools

