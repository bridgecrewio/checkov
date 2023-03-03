import datetime
import json
from typing import Any

from lark import Tree
from bc_jsonpath_ng import parse, JSONPath

from checkov.common.bridgecrew.severities import Severity
from checkov.common.output.common import ImageDetails
from checkov.common.packaging.version import LegacyVersion, Version

type_of_function = type(lambda x: x)


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
        elif isinstance(o, Severity):
            return o.name
        elif isinstance(o, complex):
            return str(o)
        elif isinstance(o, ImageDetails):
            return o.__dict__
        elif isinstance(o, type_of_function):
            return str(o)
        else:
            return json.JSONEncoder.default(self, o)


def get_jsonpath_from_evaluated_key(evaluated_key: str) -> JSONPath:
    evaluated_key = evaluated_key.replace("/", ".")
    return parse(f"$..{evaluated_key}")  # type:ignore[no-any-return]
