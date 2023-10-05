import re
from typing import Union, List, Dict

from checkov.cloudformation.graph_builder.variable_rendering.vertex_reference import CloudformationVertexReference
from checkov.cloudformation.parser.cfn_keywords import IntrinsicFunctions

REMOVE_INTERPOLATION_PATTERN = re.compile("[${}]")
FIND_INTERPOLATION_PATTERN = re.compile(r"\${([a-zA-Z0-9.]*?)}")
GLOBALS_RESOURCE_TYPE_MAP = {
    "Function": "AWS::Serverless::Function",
    "Api": "AWS::Serverless::Api",
    "HttpApi": "AWS::Serverless::HttpApi",
    "SimpleTable": "AWS::Serverless::SimpleTable",
}


def get_vertices_references(str_value: str, vertices_block_name_map: Dict[str, Dict[str, List[int]]]) -> List[CloudformationVertexReference]:
    vertices_references = []
    words_in_str_value = str_value.split()
    for word in words_in_str_value:
        word_sub_parts = word.split(".")
        suspected_block = word_sub_parts[0]
        for block_type, blocks_dict in vertices_block_name_map.items():
            if suspected_block in blocks_dict:
                vertex_reference = CloudformationVertexReference(
                    block_type=block_type, sub_parts=word_sub_parts, origin_value=suspected_block
                )
                if vertex_reference not in vertices_references:
                    vertices_references.append(vertex_reference)
                break
    return vertices_references


def remove_interpolation(str_value: str, replace_str: str = " ") -> str:
    if "${" not in str_value:
        # otherwise it is not an interpolation
        return str_value
    return re.sub(REMOVE_INTERPOLATION_PATTERN, replace_str, str_value)


def find_all_interpolations(str_value: str) -> List[str]:
    return re.findall(FIND_INTERPOLATION_PATTERN, str_value)


def get_referenced_vertices_in_value(
    value: Union[str, List[str], Dict[str, str]],
    vertices_block_name_map: Dict[str, Dict[str, List[int]]],
) -> List[CloudformationVertexReference]:
    references_vertices = []

    if isinstance(value, list):
        for sub_value in value:
            references_vertices += get_referenced_vertices_in_value(
                sub_value, vertices_block_name_map
            )

    if isinstance(value, dict):
        for key, sub_value in value.items():
            if key == IntrinsicFunctions.GET_ATT:
                sub_value = '.'.join(sub_value) if \
                    isinstance(sub_value, list) and all(isinstance(s, str) for s in sub_value) else sub_value
            references_vertices += get_referenced_vertices_in_value(
                sub_value, vertices_block_name_map
            )

    if isinstance(value, str):
        value = remove_interpolation(value)
        references_vertices = get_vertices_references(value, vertices_block_name_map)

    return references_vertices
