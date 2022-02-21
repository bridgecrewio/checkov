import logging
import os
import re
from typing import Tuple
from typing import Union, List, Any, Dict, Optional, Callable

from checkov.common.util.type_forcers import force_int
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.variable_rendering.vertex_reference import TerraformVertexReference

MODULE_DEPENDENCY_PATTERN_IN_PATH = re.compile(r"\[.+\#.+\]")
CHECKOV_RENDER_MAX_LEN = force_int(os.getenv("CHECKOV_RENDER_MAX_LEN", "10000"))


def is_local_path(root_dir: str, source: str) -> bool:
    # https://www.terraform.io/docs/modules/sources.html#local-paths
    return (
        source.startswith("./")
        or source.startswith("/./")
        or source.startswith("../")
        or source in os.listdir(root_dir)
    )


def remove_module_dependency_in_path(path: str) -> Tuple[str, str, str]:
    """
    :param path: path that looks like "dir/main.tf[other_dir/x.tf#0]
    :return: separated path from module dependency: dir/main.tf, other_dir/x.tf
    """
    module_dependency = re.findall(MODULE_DEPENDENCY_PATTERN_IN_PATH, path)
    if re.findall(MODULE_DEPENDENCY_PATTERN_IN_PATH, path):
        path = re.sub(MODULE_DEPENDENCY_PATTERN_IN_PATH, "", path)
    module_and_num = extract_module_dependency_path(module_dependency)
    return path, module_and_num[0], module_and_num[1]


def extract_module_dependency_path(module_dependency: List[str]) -> List[str]:
    """
    :param: module_dependency: a list looking like ['[path_to_module.tf#0]']
    :return: the path without enclosing array and index: 'path_to_module.tf'
    """
    if not module_dependency:
        return ["", ""]
    if isinstance(module_dependency, list) and len(module_dependency) > 0:
        module_dependency = module_dependency[0]
    return [
        module_dependency[1:module_dependency.index('.tf#') + len('.tf')],
        module_dependency[module_dependency.index('.tf#') + len('.tf#'):-1]
    ]


BLOCK_TYPES_STRINGS = ["var", "local", "module", "data"]
FUNC_CALL_PREFIX_PATTERN = re.compile(r"([.a-zA-Z]+)\(")
INTERPOLATION_PATTERN = re.compile(r"[${}]")
INTERPOLATION_EXPR = re.compile(r"\$\{([^\}]*)\}")
INDEX_PATTERN = re.compile(r"\[([0-9]+)\]")
MAP_ATTRIBUTE_PATTERN = re.compile(r"\[\"([^\d\W]\w*)\"\]")

def get_vertices_references(
    str_value: str, aliases: Dict[str, Dict[str, BlockType]], resources_types: List[str]
) -> List[TerraformVertexReference]:
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
                    vertex_reference = TerraformVertexReference(
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
                    vertex_reference = TerraformVertexReference(
                        block_type=BlockType.RESOURCE, sub_parts=word_sub_parts, origin_value=w
                    )
                    if vertex_reference not in vertices_references:
                        vertices_references.append(vertex_reference)

    return vertices_references


def get_vertex_reference_from_alias(
    block_type_str: str, aliases: Dict[str, Dict[str, BlockType]], val: List[str]
) -> Optional[TerraformVertexReference]:
    block_type = ""
    if block_type_str in aliases:
        block_type = aliases[block_type_str][CustomAttributes.BLOCK_TYPE]
    aliased_provider = ".".join(val)
    if aliased_provider in aliases:
        block_type = aliases[aliased_provider][CustomAttributes.BLOCK_TYPE]
    if block_type:
        return TerraformVertexReference(block_type=block_type, sub_parts=val, origin_value="")
    return None


def remove_function_calls_from_str(str_value: str) -> str:
    # remove start of function calls:: 'length(aws_vpc.main) > 0 ? aws_vpc.main[0].cidr_block : ${var.x}' --> 'aws_vpc.main) > 0 ? aws_vpc.main[0].cidr_block : ${var.x}'
    str_value = re.sub(FUNC_CALL_PREFIX_PATTERN, "", str_value)
    # remove ')'
    return re.sub(re.compile(r"[)]+"), "", str_value)


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
) -> List[TerraformVertexReference]:
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
        if CHECKOV_RENDER_MAX_LEN and 0 < CHECKOV_RENDER_MAX_LEN < len(value):
            logging.info(f'Rendering was skipped for a {len(value)}-character-long string. If you wish to have it '
                         f'evaluated, please set the environment variable CHECKOV_RENDER_MAX_LEN '
                         f'to {str(len(value) + 1)} or to 0 to allow rendering of any length')
        else:
            if cleanup_functions:
                for func in cleanup_functions:
                    value = func(value)
            references_vertices = get_vertices_references(value, aliases, resources_types)

    return references_vertices


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
    prefixes_with_attribute_key = [a for a in attributes.keys() if a.startswith(attribute_key) and a != attribute_key]
    if not any(re.findall(re.compile(r"\.\d+"), a) for a in prefixes_with_attribute_key):
        # if there aro no numeric parts in the key such as key1.0.key2
        return isinstance(attributes[attribute_key], dict)
    return isinstance(attributes[attribute_key], list) or isinstance(attributes[attribute_key], dict)
