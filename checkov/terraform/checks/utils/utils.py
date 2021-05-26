import concurrent.futures
import hashlib
import json
import logging
import os
import re
from copy import deepcopy
from typing import Union, List, Any, Dict, Optional, Callable

from checkov.common.graph.graph_builder import Edge
from checkov.terraform.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.terraform.graph_builder.graph_components.block_types import BlockType

BLOCK_TYPES_STRINGS = ["var", "local", "module", "data"]
FUNC_CALL_PREFIX_PATTERN = r"([.a-zA-Z]+)\("
INTERPOLATION_PATTERN = "[${}]"
INTERPOLATION_EXPR = r"\$\{([^\}]*)\}"
BRACKETS_PATTERN = r"[\[\]\)\(\{\}]+"
INDEX_PATTERN = r"\[([0-9]+)\]"
IDENTIFIER_PATTERN = r"^[^\d\W]\w*\Z"
MAP_ATTRIBUTE_PATTERN = r"\[\"([^\d\W]\w*)\"\]"


class VertexReference:
    def __init__(self, block_type: Union[str, BlockType], sub_parts: List[str], origin_value: str) -> None:
        self.block_type: BlockType = block_type_str_to_enum(block_type) if isinstance(block_type, str) else block_type
        self.sub_parts = sub_parts
        self.origin_value = origin_value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, VertexReference):
            return NotImplemented
        return (
            self.block_type == other.block_type
            and self.sub_parts == other.sub_parts
            and self.origin_value == other.origin_value
        )

    def __str__(self) -> str:
        return f"{self.block_type} sub_parts = {self.sub_parts}, origin = {self.origin_value}"


def get_vertices_references(
    str_value: str, aliases: Dict[str, Dict[str, BlockType]], resources_types: List[str]
) -> List[VertexReference]:
    vertices_references = []
    words_in_str_value = str_value.split()

    for word in words_in_str_value:
        if word.startswith(".") or word.startswith("/."):
            # check if word is a relative path
            continue

        interpolations = re.split(INTERPOLATION_EXPR, word)
        for interpolation_content in interpolations:
            for w in interpolation_content.split(","):
                word_sub_parts = w.split(".")
                if len(word_sub_parts) <= 1 or word_sub_parts[0].isnumeric():
                    # if the word doesn't contain a '.' char, or if the first part before the dot is a number
                    continue

                suspected_block_type = word_sub_parts[0]
                if suspected_block_type in BLOCK_TYPES_STRINGS:
                    # matching cases like 'var.x'
                    vertex_reference = VertexReference(
                        block_type=suspected_block_type, sub_parts=word_sub_parts[1:], origin_value=w
                    )
                    if vertex_reference not in vertices_references:
                        vertices_references.append(vertex_reference)
                    continue

                vertex_reference_alias = get_vertex_reference_from_alias(suspected_block_type, aliases, word_sub_parts)
                if vertex_reference_alias and vertex_reference_alias not in vertices_references:
                    vertex_reference_alias.origin_value = w
                    # matching cases where the word is referring an alias
                    vertices_references.append(vertex_reference_alias)
                    continue

                # matching cases like 'aws_vpc.main'
                if word_sub_parts[0] in resources_types:
                    block_name = word_sub_parts[0] + "." + word_sub_parts[1]
                    word_sub_parts = [block_name] + word_sub_parts[2:]
                    vertex_reference = VertexReference(
                        block_type=BlockType.RESOURCE, sub_parts=word_sub_parts, origin_value=w
                    )
                    if vertex_reference not in vertices_references:
                        vertices_references.append(vertex_reference)

    return vertices_references


def block_type_str_to_enum(block_type_str: str) -> BlockType:
    if block_type_str == "var":
        return BlockType.VARIABLE
    if block_type_str == "local":
        return BlockType.LOCALS
    return BlockType(block_type_str)


def block_type_enum_to_str(block_type: BlockType) -> str:
    if block_type == BlockType.VARIABLE:
        return "var"
    if block_type == BlockType.LOCALS:
        return "local"
    return block_type


def get_vertex_reference_from_alias(
    block_type_str: str, aliases: Dict[str, Dict[str, BlockType]], val: List[str]
) -> Optional[VertexReference]:
    block_type = ""
    if block_type_str in aliases:
        block_type = aliases[block_type_str][CustomAttributes.BLOCK_TYPE]
    aliased_provider = ".".join(val)
    if aliased_provider in aliases:
        block_type = aliases[aliased_provider][CustomAttributes.BLOCK_TYPE]
    if block_type:
        return VertexReference(block_type=block_type, sub_parts=val, origin_value="")
    return None


def remove_function_calls_from_str(str_value: str) -> str:
    # remove start of function calls:: 'length(aws_vpc.main) > 0 ? aws_vpc.main[0].cidr_block : ${var.x}' --> 'aws_vpc.main) > 0 ? aws_vpc.main[0].cidr_block : ${var.x}'
    str_value = re.sub(FUNC_CALL_PREFIX_PATTERN, "", str_value)
    # remove ')'
    return re.sub(r"[)]+", "", str_value)


def remove_index_pattern_from_str(str_value: str) -> str:
    str_value = re.sub(INDEX_PATTERN, "", str_value)
    str_value = str_value.replace("[", " [ ")
    str_value = str_value.replace("]", " ] ")
    return str_value


def remove_interpolation(str_value: str, replace_str: str = " ") -> str:
    return re.sub(INTERPOLATION_PATTERN, replace_str, str_value)


def replace_map_attribute_access_with_dot(str_value: str) -> str:
    split_by_identifiers = re.split(MAP_ATTRIBUTE_PATTERN, str_value)
    new_split = []
    for split_part in split_by_identifiers:
        if split_part.startswith("."):
            split_part = split_part[1:]
        if split_part.endswith("."):
            split_part = split_part[:-1]
        new_split.append(split_part)

    return ".".join(new_split)


DEFAULT_CLEANUP_FUNCTIONS: List[Callable[[str], str]] = [
    remove_function_calls_from_str,
    remove_index_pattern_from_str,
    replace_map_attribute_access_with_dot,
    remove_interpolation,
]


def get_referenced_vertices_in_value(
    value: Union[str, List[str], Dict[str, str]],
    aliases: Dict[str, Dict[str, BlockType]],
    resources_types: List[str],
    cleanup_functions: Optional[List[Callable[[str], str]]] = None,
) -> List[VertexReference]:
    if cleanup_functions is None:
        cleanup_functions = DEFAULT_CLEANUP_FUNCTIONS
    references_vertices = []

    if isinstance(value, list):
        for sub_value in value:
            references_vertices += get_referenced_vertices_in_value(
                sub_value, aliases, resources_types, cleanup_functions
            )

    if isinstance(value, dict):
        for sub_value in value.values():
            references_vertices += get_referenced_vertices_in_value(
                sub_value, aliases, resources_types, cleanup_functions
            )

    if isinstance(value, str):
        if cleanup_functions:
            for func in cleanup_functions:
                value = func(value)
        references_vertices = get_vertices_references(value, aliases, resources_types)

    return references_vertices


def encode_graph_property_value(value: Union[bool, int, float, str, Dict[str, Any]]) -> str:
    if isinstance(value, bool):
        # Encode boolean into Terraform's lower case convention
        value = str(value).lower()
    elif isinstance(value, (float, int)):
        value = str(value)
    return json.dumps(value, indent=4, default=str)


def decode_graph_property_value(value: Any, leave_str: bool = False) -> Any:
    if type(value) not in (str, bytes, bytearray):
        return value
    if "python_object" in value:
        raise Exception(f"checkov does not allow arbitrary code execution, found here: {value}")
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    if not leave_str:
        if value.isnumeric():
            value = int(value)
        else:
            try:
                value = json.loads(value)
            except (ValueError, AttributeError):
                logging.debug(f"Failed to decode graph value {value}")
    return value


def calculate_hash(data: Union[bool, int, float, str, Dict[str, Any]]) -> str:
    encoded_attributes = encode_graph_property_value(data)
    sha256 = hashlib.sha256()
    sha256.update(repr(encoded_attributes).encode("utf-8"))

    return sha256.hexdigest()


def run_function_multithreaded(
    func: Callable[..., Any], data: List[List[Edge]], max_group_size: int, num_of_workers: Optional[int] = None
) -> None:
    groups_of_data = [data[i : i + max_group_size] for i in range(0, len(data), max_group_size)]
    if not num_of_workers:
        num_of_workers = len(groups_of_data)
    if num_of_workers > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_of_workers) as executor:
            futures = {executor.submit(func, data_group): data_group for data_group in groups_of_data}
            wait_result = concurrent.futures.wait(futures)
            if wait_result.not_done:
                raise Exception(f"failed to perform {func.__name__}")
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    raise e


def update_dictionary_attribute(
    config: Union[List[Any], Dict[str, Any]], key_to_update: str, new_value: Any
) -> Union[List[Any], Dict[str, Any]]:
    key_parts = key_to_update.split(".")
    if isinstance(config, dict):
        if config.get(key_parts[0]) is not None:
            key = key_parts[0]
            if len(key_parts) == 1:
                if isinstance(config[key], list) and not isinstance(new_value, list):
                    new_value = [new_value]
                config[key] = new_value
                return config
            else:
                config[key] = update_dictionary_attribute(config[key], ".".join(key_parts[1:]), new_value)
        else:
            for key in config:
                config[key] = update_dictionary_attribute(config[key], key_to_update, new_value)
    if isinstance(config, list):
        for i in range(len(config)):
            config[i] = update_dictionary_attribute(config[i], key_to_update, new_value)

    return config


def join_trimmed_strings(char_to_join: str, str_lst: List[str], num_to_trim: int) -> str:
    return char_to_join.join(str_lst[: len(str_lst) - num_to_trim])


def filter_sub_keys(key_list: List[str]) -> List[str]:
    filtered_key_list = []
    for key in key_list:
        if not any(other_key != key and other_key.startswith(key) for other_key in key_list):
            filtered_key_list.append(key)
    return filtered_key_list


def generate_possible_strings_from_wildcards(origin_string: str, max_entries: int = 10) -> List[str]:
    max_entries = int(os.environ.get("MAX_WILDCARD_ARR_SIZE", max_entries))
    generated_strings = [origin_string]
    if not origin_string:
        return []
    if "*" not in origin_string:
        return generated_strings

    locations_of_wildcards = []
    for i, char in enumerate(origin_string):
        if char == "*":
            locations_of_wildcards.append(i)
    locations_of_wildcards.reverse()

    for wildcard_index in locations_of_wildcards:
        new_generated_strings = []
        for s in generated_strings:
            before_wildcard = s[:wildcard_index]
            after_wildcard = s[wildcard_index + 1 :]
            for i in range(max_entries):
                new_generated_strings.append(before_wildcard + str(i) + after_wildcard)
        generated_strings = new_generated_strings

    # if origin_string == "ingress.*.cidr_blocks", check for "ingress.cidr_blocks" too
    generated_strings.append("".join(origin_string.split(".*")))
    return generated_strings


def attribute_has_nested_attributes(attribute_key: str, attributes: Dict[str, Any]) -> bool:
    """
    :param attribute_key: key inside the  `attributes` dictionary
    :param attributes:
    :return: True if attribute_key has inner attributes.
    Example 1: if attributes.keys == [key1, key.key2], type(attributes[key1]) is dict and return True for key1
    Example 2: if attributes.keys == [key1, key1.0], type(attributes[key1]) is list and return True for key1
    """
    copy_of_attributes = deepcopy(attributes)
    copy_of_attributes.pop(attribute_key)
    prefixes_with_attribute_key = [a for a in copy_of_attributes.keys() if a.startswith(attribute_key)]
    if not any(re.findall(r"\.\d+", a) for a in prefixes_with_attribute_key):
        # if there aro no numeric parts in the key such as key1.0.key2
        return isinstance(attributes[attribute_key], dict)
    return isinstance(attributes[attribute_key], list) or isinstance(attributes[attribute_key], dict)
