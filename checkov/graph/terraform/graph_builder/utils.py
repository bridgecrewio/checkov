import base64
import builtins
import hashlib
import io
import json
import os
import re
import pickle # nosec

MODULE_DEPENDENCY_PATTERN_IN_PATH = r'\[.+\#.+\]'


def is_local_path(root_dir, source):
    # https://www.terraform.io/docs/modules/sources.html#local-paths
    return source.startswith('./') or \
            source.startswith('/./') or \
            source.startswith('../') or \
            source in os.listdir(root_dir)


def remove_module_dependency_in_path(path):
    """
    :param path: path that looks like "dir/main.tf[other_dir/x.tf#0]
    :return: separated path from module dependency: dir/main.tf, other_dir/x.tf
    """
    module_dependency = re.findall(MODULE_DEPENDENCY_PATTERN_IN_PATH, path)
    if re.findall(MODULE_DEPENDENCY_PATTERN_IN_PATH, path):
        path = re.sub(MODULE_DEPENDENCY_PATTERN_IN_PATH, '', path)
    return path, extract_module_dependency_path(module_dependency)


def extract_module_dependency_path(module_dependency):
    """
    :param module_dependency: a list looking like ['[path_to_module.tf#0]']
    :return: the path without enclosing array and index: 'path_to_module.tf'
    """
    if not module_dependency:
        return ''
    if type(module_dependency) is list and len(module_dependency) > 0:
        module_dependency = module_dependency[0]
    return module_dependency[1:-1].split('#')[0]


def encode_graph_property_value(value, encode_values=True):
    if not encode_values:
        return value
    if isinstance(value, bool):
        # Encode boolean into Terraform's lower case convention
        value = str(value).lower()
    elif isinstance(value, (float, int)):
        value = str(value)
    return json.dumps(value, cls=PythonObjectEncoder, indent=4)


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        # Only allow safe classes from builtins.
        if module == "builtins" or module.startswith("lark."):
            return getattr(builtins, name)
        # Forbid everything else.
        raise pickle.UnpicklingError("global '%s.%s' is forbidden" %
                                     (module, name))


def restricted_loads(s):
    """Helper function analogous to pickle.loads()."""
    return RestrictedUnpickler(io.BytesIO(s)).load()


class PythonObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        return {'_python_object':
                base64.b64encode(pickle.dumps(obj)).decode('utf-8') }


def as_python_object(dct):
    if '_python_object' in dct:
        return restricted_loads(base64.b64decode(dct['_python_object']))
    return dct


def calculate_hash(data):
    encoded_attributes = encode_graph_property_value(data)
    sha256 = hashlib.sha256()
    sha256.update(repr(encoded_attributes).encode('utf-8'))

    return sha256.hexdigest()