"""
DroneKit Python 3.13 Compatibility Patch
Fixes the collections.MutableMapping deprecation issue
Run this before importing dronekit
"""

import collections.abc
import collections

# Add MutableMapping to collections module for backward compatibility
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping
if not hasattr(collections, 'OrderedDict'):
    collections.OrderedDict = dict

print("[Patch] Applied DroneKit compatibility fixes for Python 3.13")
