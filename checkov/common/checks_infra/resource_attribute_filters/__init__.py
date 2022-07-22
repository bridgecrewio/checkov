from os.path import dirname, basename, isfile, join
from importlib import import_module
import glob
from typing import Dict, List

modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith("__init__.py")]

attribute_resources: Dict[str, Dict[str, List[str]]] = {}

for file in __all__:
    attr_module = import_module(__name__ + '.' + file)
    attribute_to_types: Dict[str, Dict[str, List[str]]] = getattr(attr_module, 'resource_types')
    for attribute, providers_to_types in attribute_to_types.items():
        all_types = []
        for resource_types in providers_to_types.values():
            all_types.extend(resource_types)
        providers_to_types['__all__'] = all_types

        attribute_resources[attribute] = providers_to_types
