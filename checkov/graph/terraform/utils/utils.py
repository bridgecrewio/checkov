import base64
import builtins
import concurrent.futures
import hashlib
import io
import json
import pickle  # nosec
import re

from checkov.graph.terraform.graph_builder.graph_components.block_types import BlockType

from checkov.graph.terraform.graph_builder.graph_components.attribute_names import CustomAttributes

BLOCK_TYPES_STRINGS = ['var', 'local', 'module', 'data']
FUNC_CALL_PREFIX_PATTERN = r'([.a-zA-Z]+)\('
INTERPOLATION_PATTERN = '[${}]'
INTERPOLATION_EXPR = r'\$\{([^\}]*)\}'
BRACKETS_PATTERN = r'[\[\]\)\(\{\}]+'
INDEX_PATTERN = r'\[([0-9]+)\]'
IDENTIFIER_PATTERN = r'^[^\d\W]\w*\Z'
MAP_ATTRIBUTE_PATTERN = r'\[\"([^\d\W]\w*)\"\]'


class VertexReference:
    def __init__(self, block_type, sub_parts, origin_value):
        self.block_type = block_type_str_to_enum(block_type) if type(block_type) is str else block_type
        self.sub_parts = sub_parts
        self.origin_value = origin_value

    def __eq__(self, other):
        if not isinstance(other, VertexReference):
            return NotImplemented
        return self.block_type == other.block_type and self.sub_parts == other.sub_parts and self.origin_value == other.origin_value


def get_vertices_references(str_value, aliases, resources_types):
    vertices_references = []
    words_in_str_value = str_value.split()

    for word in words_in_str_value:
        if word.startswith('.') or word.startswith('/.'):
            # check if word is a relative path
            continue

        interpolations = re.split(INTERPOLATION_EXPR, word)
        for interpolation_content in interpolations:
            for w in interpolation_content.split(','):
                word_sub_parts = w.split('.')
                if len(word_sub_parts) <= 1 or word_sub_parts[0].isnumeric():
                    # if the word doesn't contain a '.' char, or if the first part before the dot is a number
                    continue

                suspected_block_type = word_sub_parts[0]
                if suspected_block_type in BLOCK_TYPES_STRINGS:
                    # matching cases like 'var.x'
                    vertex_reference = VertexReference(block_type=suspected_block_type, sub_parts=word_sub_parts[1:], origin_value=w)
                    if vertex_reference not in vertices_references:
                        vertices_references.append(vertex_reference)
                    continue

                vertex_reference = get_vertex_reference_from_alias(suspected_block_type, aliases, word_sub_parts)
                if vertex_reference and vertex_reference not in vertices_references:
                    vertex_reference.origin_value = w
                    # matching cases where the word is referring an alias
                    vertices_references.append(vertex_reference)
                    continue

                # matching cases like 'aws_vpc.main'
                if word_sub_parts[0] in resources_types:
                    block_name = word_sub_parts[0] + '.' + word_sub_parts[1]
                    word_sub_parts = [block_name] + word_sub_parts[2:]
                    vertex_reference = VertexReference(block_type=BlockType.RESOURCE, sub_parts=word_sub_parts,
                                                       origin_value=w)
                    if vertex_reference not in vertices_references:
                        vertices_references.append(vertex_reference)

    return vertices_references


def block_type_str_to_enum(block_type_str):
    if block_type_str == 'var':
        return BlockType.VARIABLE
    if block_type_str == 'local':
        return BlockType.LOCALS
    try:
        return BlockType(block_type_str)
    except Exception:
        return None


def block_type_enum_to_str(block_type):
    if block_type == BlockType.VARIABLE:
        return 'var'
    if block_type == BlockType.LOCALS:
        return 'local'
    return block_type


def get_vertex_reference_from_alias(block_type_str, aliases, val):
    block_type = ''
    if block_type_str in aliases:
        block_type = aliases[block_type_str][CustomAttributes.BLOCK_TYPE]
    aliased_provider = ".".join(val)
    if aliased_provider in aliases:
        block_type = aliases[aliased_provider][CustomAttributes.BLOCK_TYPE]
    if block_type:
        return VertexReference(block_type=block_type, sub_parts=val,
                               origin_value='')
    return None


def remove_function_calls_from_str(str_value):
    # remove start of function calls:: 'length(aws_vpc.main) > 0 ? aws_vpc.main[0].cidr_block : ${var.x}' --> 'aws_vpc.main) > 0 ? aws_vpc.main[0].cidr_block : ${var.x}'
    str_value = re.sub(FUNC_CALL_PREFIX_PATTERN, '', str_value)
    # remove ')'
    return re.sub(r'[)]+', '', str_value)


def remove_index_pattern_from_str(str_value):
    return re.sub(INDEX_PATTERN, '', str_value)


def remove_interpolation(str_value):
    return re.sub(INTERPOLATION_PATTERN, ' ', str_value)


def replace_map_attribute_access_with_dot(str_value):
    split_by_identifiers = re.split(MAP_ATTRIBUTE_PATTERN, str_value)
    new_split = []
    for split_part in split_by_identifiers:
        if split_part.startswith('.'):
            split_part = split_part[1:]
        if split_part.endswith('.'):
            split_part = split_part[:-1]
        new_split.append(split_part)

    return '.'.join(new_split)


DEFAULT_CLEANUP_FUNCTIONS = [remove_function_calls_from_str, remove_index_pattern_from_str, replace_map_attribute_access_with_dot, remove_interpolation]


def get_referenced_vertices_in_value(value, aliases, resources_types, cleanup_functions=DEFAULT_CLEANUP_FUNCTIONS):
    references_vertices = []
    value_type = type(value)

    if value_type is list:
        for sub_value in value:
            references_vertices += get_referenced_vertices_in_value(sub_value, aliases, resources_types, cleanup_functions)

    if value_type is dict:
        for sub_key in value:
            references_vertices += get_referenced_vertices_in_value(value[sub_key], aliases, resources_types, cleanup_functions)

    if value_type is str:
        if cleanup_functions:
            for func in cleanup_functions:
                value = func.__call__(value)
        references_vertices = get_vertices_references(value, aliases, resources_types)

    return references_vertices


def encode_graph_property_value(value):
    if isinstance(value, bool):
        # Encode boolean into Terraform's lower case convention
        value = str(value).lower()
    elif isinstance(value, (float, int)):
        value = str(value)
    return json.dumps(value, cls=PythonObjectEncoder, indent=4)


def decode_graph_property_value(value, leave_str=False):
    try:
        if type(value) is str and value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        if not leave_str:
            if value.isnumeric():
                value = int(value)
            value = json.loads(value, object_hook=as_python_object)
        return value
    except (ValueError, AttributeError):
        try:
            if type(value) in [str, bytes, bytearray]:
                value = json.loads(value)
            return value
        except ValueError:
            pass

    finally:
        return value


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


def run_function_multithreaded(func, data, max_group_size, num_of_workers=None):
    groups_of_data = [data[i:i + max_group_size] for i in
                      range(0, len(data), max_group_size)]
    if not num_of_workers:
        num_of_workers = len(groups_of_data)
    if num_of_workers > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_of_workers) as executor:
            futures = {executor.submit(func, data_group): data_group for data_group in groups_of_data}
            wait_result = concurrent.futures.wait(futures)
            if wait_result.not_done:
                raise Exception(f'failed to perform {func.__name__}')
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    raise e


def update_dictionary_attribute(config, key_to_update, new_value):
    key_parts = key_to_update.split('.')
    if type(config) is dict:
        if config.get(key_parts[0]) is not None:
            key = key_parts[0]
            if len(key_parts) == 1:
                config[key] = new_value
                return config
            else:
                config[key] = update_dictionary_attribute(config[key], '.'.join(key_parts[1:]), new_value)
        else:
            for key in config:
                config[key] = update_dictionary_attribute(config[key], key_to_update, new_value)
    if type(config) is list:
        for i in range(len(config)):
            config[i] = update_dictionary_attribute(config[i], key_to_update, new_value)

    return config


def join_trimmed_strings(char_to_join, str_lst, num_to_trim):
    return char_to_join.join(str_lst[:len(str_lst) - num_to_trim])


def filter_sub_keys(key_list):
    filtered_key_list = []
    for key in key_list:
        if not any(other_key != key and other_key.startswith(key) for other_key in key_list):
            filtered_key_list.append(key)
    return filtered_key_list
