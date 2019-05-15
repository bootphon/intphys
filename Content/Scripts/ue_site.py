"""The ue_site.py module is loaded at startup by the Unreal Engine.

It initializes the Python path with absolute paths only, and adds the
.../Content/Scripts directory containing the intphys Python code.

"""

import os
import sys

# add the absolute path to .../intphys/Content/Scripts
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# remove all paths that are not absolute/existing paths and a .zip
# file automatically added by the UnrealEnginePython plugin
# sys.path = [p for p in sys.path
#             if os.path.isabs(p) and os.path.isdir(p)
#             and not p.endswith('zip')]

# # Display the Python path in the UE output log
# print('The Python path is: {}'.format(', '.join(sys.path)))
