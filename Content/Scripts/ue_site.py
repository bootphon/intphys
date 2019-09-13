"""The ue_site.py module is loaded at startup by the Unreal Engine.

It adds the intphys/Content/Scripts directory to the Python path.

"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
