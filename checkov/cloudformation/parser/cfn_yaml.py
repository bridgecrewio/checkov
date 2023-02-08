"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

import json
import logging
import platform
from collections.abc import Hashable
from enum import Enum
from pathlib import Path
from typing import Any, TYPE_CHECKING, NoReturn, Callable

from yaml import MappingNode
from yaml import ScalarNode
from yaml import SequenceNode
from yaml.composer import Composer
from yaml.constructor import ConstructorError
from yaml.constructor import SafeConstructor
from yaml.reader import Reader
from yaml.resolver import Resolver
from yaml.scanner import Scanner
from charset_normalizer import from_path

from checkov.common.parsers.json.decoder import SimpleDecoder
from checkov.common.parsers.node import StrNode, DictNode, ListNode
from checkov.common.util.consts import MAX_IAC_FILE_SIZE

try:
    from yaml.cyaml import CParser as Parser  # type:ignore[attr-defined]

    cyaml = True
except ImportError:
    from yaml.parser import Parser  # type:ignore[assignment]

    cyaml = False

if TYPE_CHECKING:
    from yaml import Node

UNCONVERTED_SUFFIXES = ['Ref', 'Condition']
FN_PREFIX = 'Fn::'

LOGGER = logging.getLogger(__name__)


class ContentType(str, Enum):
    CFN = "CFN"
    SLS = "SLS"
    TFPLAN = "TFPLAN"


class CfnParseError(ConstructorError):
    """
    Error thrown when the template contains Cfn Error
    """

    def __init__(self, filename: str, message: str, line_number: int, column_number: int) -> None:
        # Call the base class constructor with the parameters it needs
        super(CfnParseError, self).__init__(message)

        # Now for your custom code...
        self.filename = filename
        self.line_number = line_number
        self.column_number = column_number
        self.message = message


class NodeConstructor(SafeConstructor):
    """
    Node Constructors for loading different types in Yaml
    """

    def __init__(self, filename: str, content_type: ContentType | None = None) -> None:
        # Call the base class constructor
        super().__init__()
        self.add_constructor(  # type:ignore[type-var]
            u'tag:yaml.org,2002:map',
            NodeConstructor.construct_yaml_map,
        )

        self.add_constructor(  # type:ignore[type-var]
            u'tag:yaml.org,2002:str',
            NodeConstructor.construct_yaml_str,
        )

        self.add_constructor(  # type:ignore[type-var]
            u'tag:yaml.org,2002:seq',
            NodeConstructor.construct_yaml_seq,
        )
        if content_type != ContentType.TFPLAN:
            NodeConstructor.add_constructor(  # type:ignore[type-var]
                u'tag:yaml.org,2002:null',
                NodeConstructor.construct_yaml_null_error,
            )
        self.filename = filename

    # To support lazy loading, the original constructors first yield
    # an empty object, then fill them in when iterated. Due to
    # laziness we omit this behaviour (and will only do "deep
    # construction") by first exhausting iterators, then yielding
    # copies.
    def construct_yaml_map(self, node: MappingNode) -> DictNode:
        # Check for duplicate keys on the current level, this is not desirable
        # because a dict does not support this. It overwrites it with the last
        # occurance, which can give unexpected results
        mapping = {}
        self.flatten_mapping(node)
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, False)  # type:ignore[no-untyped-call]
            value = self.construct_object(value_node, False)  # type:ignore[no-untyped-call]
            try:
                if isinstance(key, dict):
                    key = frozenset(key.keys()), frozenset(key.values())
                if isinstance(key, list):
                    key = frozenset(key)
            except TypeError:
                raise CfnParseError(
                    filename=self.filename,
                    message=f'Unable to construct key {key} (line {key_node.start_mark.line + 1})',
                    line_number=key_node.start_mark.line,
                    column_number=key_node.start_mark.column,
                ) from None
            if key in mapping:
                raise CfnParseError(
                    filename=self.filename,
                    message=f'Duplicate resource found "{key}" (line {key_node.start_mark.line + 1})',
                    line_number=key_node.start_mark.line,
                    column_number=key_node.start_mark.column,
                )
            mapping[key] = value

        obj, = SafeConstructor.construct_yaml_map(self, node)  # type:ignore[no-untyped-call]
        return DictNode(obj, node.start_mark, node.end_mark)

    def construct_yaml_str(self, node: ScalarNode) -> StrNode:
        obj = SafeConstructor.construct_yaml_str(self, node)  # type:ignore[no-untyped-call]
        assert isinstance(obj, str)  # nosec
        return StrNode(obj, node.start_mark, node.end_mark)

    def construct_yaml_seq(self, node: SequenceNode) -> ListNode:
        obj, = SafeConstructor.construct_yaml_seq(self, node)  # type:ignore[no-untyped-call]
        assert isinstance(obj, list)  # nosec
        return ListNode(obj, node.start_mark, node.end_mark)  # nosec

    def construct_yaml_null_error(self, node: Node) -> NoReturn:
        """Throw a null error"""
        raise CfnParseError(
            filename=self.filename,
            message=f"Null value at line {node.start_mark.line + 1} column {node.start_mark.column + 1}",
            line_number=node.start_mark.line,
            column_number=node.start_mark.column,
        )


class MarkedLoader(Reader, Scanner, Parser, Composer, NodeConstructor, Resolver):
    """
    Class for marked loading YAML
    """

    # pylint: disable=non-parent-init-called,super-init-not-called

    def __init__(self, stream: str, filename: str, content_type: ContentType | None = None) -> None:
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        if cyaml:
            Parser.__init__(self, stream)
        else:
            Parser.__init__(self)  # type:ignore[call-arg]  # cyaml checks if it is the normal or C version
        Composer.__init__(self)
        SafeConstructor.__init__(self)
        Resolver.__init__(self)
        NodeConstructor.__init__(self, filename, content_type)

    def construct_mapping(self, node: MappingNode, deep: bool = False) -> dict[Hashable, Any]:
        mapping = super(MarkedLoader, self).construct_mapping(node, deep=deep)
        # Add 1 so line numbering starts at 1
        # mapping['__line__'] = node.start_mark.line + 1
        mapping['__startline__'] = node.start_mark.line + 1
        mapping['__endline__'] = node.end_mark.line + 1
        return mapping


def multi_constructor(loader: MarkedLoader, tag_suffix: str, node: ScalarNode) -> DictNode:
    """
    Deal with !Ref style function format
    """

    constructor: Callable[[ScalarNode], Any]

    if tag_suffix not in UNCONVERTED_SUFFIXES:
        tag_suffix = f"{FN_PREFIX}{tag_suffix}"

    if tag_suffix == 'Fn::GetAtt':
        constructor = construct_getatt
    elif tag_suffix == "Ref" and (isinstance(node.value, list) or isinstance(node.value, dict)):
        raise CfnParseError(
            filename="",
            message='Invalid !Ref: {}'.format(node.value),
            line_number=0,
            column_number=0)
    elif isinstance(node, ScalarNode):
        constructor = loader.construct_scalar
    elif isinstance(node, SequenceNode):
        constructor = loader.construct_sequence
    elif isinstance(node, MappingNode):
        constructor = loader.construct_mapping
    else:
        raise 'Bad tag: !{}'.format(tag_suffix)

    return DictNode({tag_suffix: constructor(node)}, node.start_mark, node.end_mark)


def construct_getatt(node: ScalarNode) -> ListNode:
    """
    Reconstruct !GetAtt into a list
    """

    if isinstance(node.value, str):
        return ListNode(node.value.split('.'), node.start_mark, node.end_mark)
    if isinstance(node.value, list):
        return ListNode([s.value for s in node.value], node.start_mark, node.end_mark)

    raise ValueError('Unexpected node type: {}'.format(type(node.value)))


def loads(yaml_string: str, fname: str, content_type: ContentType | None = None) -> DictNode | dict[str, Any]:
    """
    Load the given YAML string
    """
    loader = MarkedLoader(yaml_string, fname, content_type)
    loader.add_multi_constructor('!', multi_constructor)  # type:ignore[no-untyped-call]

    template: "DictNode | dict[str, Any]" = loader.get_single_data()
    # Convert an empty file to an empty dict
    if template is None:
        template = {}

    return template


def load(filename: str | Path, content_type: ContentType) -> tuple[dict[str, Any], list[tuple[int, str]]]:
    """
    Load the given YAML file
    """
    file_path = filename if isinstance(filename, Path) else Path(filename)

    if platform.system() == "Windows":
        try:
            content = str(from_path(file_path).best())
        except UnicodeDecodeError as e:
            LOGGER.error(f"Encoding for file {file_path} could not be detected or read. Please try encoding the file as UTF-8.")
            raise e
    else:
        try:
            content = file_path.read_text()
        except UnicodeDecodeError:
            LOGGER.info(f"Encoding for file {file_path} is not UTF-8, trying to detect it")
            content = str(from_path(file_path).best())

    if content_type == ContentType.CFN and "Resources" not in content:
        logging.debug(f'File {file_path} is expected to be a CFN template but has no Resources attribute')
        return {}, []
    elif content_type == ContentType.SLS and "provider" not in content:
        logging.debug(f'File {file_path} is expected to be an SLS template but has no provider attribute')
        return {}, []
    elif content_type == ContentType.TFPLAN and "planned_values" not in content:
        logging.debug(f'File {file_path} is expected to be a TFPLAN file but has no planned_values attribute')
        return {}, []

    file_lines = [(idx + 1, line) for idx, line in enumerate(content.splitlines(keepends=True))]

    if file_path.suffix == ".json":
        file_size = len(content)
        if file_size > MAX_IAC_FILE_SIZE:
            # large JSON files take too much time, when parsed with `pyyaml`, compared to a normal 'json.loads()'
            # with start/end line numbers of 0 takes only a few seconds
            logging.info(
                f"File {file_path} has a size of {file_size} which is bigger than the supported 50mb, "
                "therefore file lines will default to 0."
                "This limit can be adjusted via the environment variable 'CHECKOV_MAX_IAC_FILE_SIZE'."
            )
            return json.loads(content, cls=SimpleDecoder), file_lines

    return loads(content, str(filename), content_type), file_lines
