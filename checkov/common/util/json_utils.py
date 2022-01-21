import datetime
import json
from typing import Any

from lark import Tree
from packaging.version import LegacyVersion, Version


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, set):
            return list(o)
        elif isinstance(o, Tree):
            return str(o)
        elif isinstance(o, datetime.date):
            return str(o)
        elif isinstance(o, (Version, LegacyVersion)):
            return str(o)
        else:
            return json.JSONEncoder.default(self, o)
