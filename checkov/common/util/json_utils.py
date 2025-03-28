import datetime
import json
from json import JSONDecodeError
from typing import Any, Dict

from lark import Tree
from bc_jsonpath_ng import parse, JSONPath

from checkov.common.bridgecrew.severities import Severity
from checkov.common.output.common import ImageDetails
from checkov.common.packaging.version import LegacyVersion, Version
from checkov.common.sast.report_types import MatchMetadata, DataFlow, MatchLocation, Point
from detect_secrets.core.potential_secret import PotentialSecret

from checkov.common.util.data_structures_utils import pickle_deepcopy

type_of_function = type(lambda x: x)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        from checkov.terraform.modules.module_objects import TFModule, TFDefinitionKey
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
        elif isinstance(o, TFDefinitionKey):
            return str(o)
        elif isinstance(o, TFModule):
            return dict(o)
        elif isinstance(o, PotentialSecret):
            return o.json()
        elif isinstance(o, MatchMetadata):
            return o.serialize_model()
        elif isinstance(o, DataFlow):
            return o.serialize_model()
        elif isinstance(o, MatchLocation):
            return o.serialize_model()
        elif isinstance(o, Point):
            return o.serialize_model()
        else:
            return json.JSONEncoder.default(self, o)

    def encode(self, obj: Any) -> str:
        return super().encode(self._encode(obj))

    def _encode(self, obj: Any) -> Any:
        if isinstance(obj, dict):
            return {self.encode_key(k): v for k, v in obj.items()}
        else:
            return obj

    @staticmethod
    def encode_key(key: Any) -> Any:
        from checkov.terraform.modules.module_objects import TFModule, TFDefinitionKey
        if isinstance(key, TFDefinitionKey):
            return str(key)
        if isinstance(key, TFModule):
            return str(key)
        if isinstance(key, tuple):
            return ",".join(key)
        else:
            return key


def object_hook(dct: Dict[Any, Any]) -> Any:
    from checkov.terraform.modules.module_objects import TFModule, TFDefinitionKey
    from checkov.common.util.consts import RESOLVED_MODULE_ENTRY_NAME
    try:
        if dct is None:
            return None
        if isinstance(dct, dict):
            dct_obj = pickle_deepcopy(dct)
            if 'tf_source_modules' in dct and 'file_path' in dct:
                return TFDefinitionKey(file_path=dct["file_path"],
                                       tf_source_modules=object_hook(dct["tf_source_modules"]))
            if 'path' in dct and 'name' in dct and 'foreach_idx' in dct and 'nested_tf_module' in dct:
                return TFModule(path=dct['path'], name=dct['name'], foreach_idx=dct['foreach_idx'],
                                nested_tf_module=object_hook(dct['nested_tf_module']))
            for key, value in dct.items():
                if key == RESOLVED_MODULE_ENTRY_NAME:
                    resolved_classes = []
                    for resolved_module in dct[RESOLVED_MODULE_ENTRY_NAME]:
                        if isinstance(resolved_module, str):
                            resolved_classes.append(object_hook(json.loads(resolved_module)))
                    dct_obj[RESOLVED_MODULE_ENTRY_NAME] = resolved_classes
                if isinstance(key, str) and 'tf_source_modules' in key and 'file_path' in key:
                    tf_definition_key = json.loads(key)
                    tf_definition_key_obj = TFDefinitionKey(file_path=tf_definition_key["file_path"], tf_source_modules=object_hook(
                        tf_definition_key["tf_source_modules"]))
                    dct_obj[tf_definition_key_obj] = value
                    del dct_obj[key]
            return dct_obj
        return dct
    except (KeyError, TypeError, JSONDecodeError):
        return dct


def get_jsonpath_from_evaluated_key(evaluated_key: str) -> JSONPath:
    evaluated_key = evaluated_key.replace("/", ".")
    return parse(f"$..{evaluated_key}")  # type:ignore[no-any-return]
