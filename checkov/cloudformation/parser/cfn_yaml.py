"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
from enum import Enum
from pathlib import Path
from typing import List, Tuple

from yaml import MappingNode
from yaml import ScalarNode
from yaml import SequenceNode
from yaml.composer import Composer
from yaml.constructor import ConstructorError
from yaml.constructor import SafeConstructor
from yaml.reader import Reader
from yaml.resolver import Resolver
from yaml.scanner import Scanner

from checkov.common.parsers.node import StrNode, DictNode, ListNode

try:
    from yaml.cyaml import CParser as Parser  # pylint: disable=ungrouped-imports

    cyaml = True
except ImportError:
    from yaml.parser import Parser  # pylint: disable=ungrouped-imports

    cyaml = False

UNCONVERTED_SUFFIXES = ['Ref', 'Condition']
FN_PREFIX = 'Fn::'

LOGGER = logging.getLogger(__name__)

class ContentType(str, Enum):
    CFN = "CFN"
    SLS = "SLS"


class CfnParseError(ConstructorError):
    """
    Error thrown when the template contains Cfn Error
    """

    def __init__(self, filename, message, line_number, column_number, key=' '):
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

    def __init__(self, filename):
        # Call the base class constructor
        super(NodeConstructor, self).__init__()

        self.filename = filename

    # To support lazy loading, the original constructors first yield
    # an empty object, then fill them in when iterated. Due to
    # laziness we omit this behaviour (and will only do "deep
    # construction") by first exhausting iterators, then yielding
    # copies.
    def construct_yaml_map(self, node):

        # Check for duplicate keys on the current level, this is not desirable
        # because a dict does not support this. It overwrites it with the last
        # occurance, which can give unexpected results
        mapping = {}
        self.flatten_mapping(node)
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, False)
            value = self.construct_object(value_node, False)

            if key in mapping:
                raise CfnParseError(
                    self.filename,
                    'Duplicate resource found "{}" (line {})'.format(
                        key, key_node.start_mark.line + 1),
                    key_node.start_mark.line, key_node.start_mark.column, key)
            mapping[key] = value

        obj, = SafeConstructor.construct_yaml_map(self, node)
        return DictNode(obj, node.start_mark, node.end_mark)

    def construct_yaml_str(self, node):
        obj = SafeConstructor.construct_yaml_str(self, node)
        assert isinstance(obj, str)  # nosec
        return StrNode(obj, node.start_mark, node.end_mark)

    def construct_yaml_seq(self, node):
        obj, = SafeConstructor.construct_yaml_seq(self, node)
        assert isinstance(obj, list) # nosec
        return ListNode(obj, node.start_mark, node.end_mark) # nosec

    def construct_yaml_null_error(self, node):
        """Throw a null error"""
        raise CfnParseError(
            self.filename,
            'Null value at line {0} column {1}'.format(
                node.start_mark.line + 1, node.start_mark.column + 1),
            node.start_mark.line, node.start_mark.column, ' ')


NodeConstructor.add_constructor(
    u'tag:yaml.org,2002:map',
    NodeConstructor.construct_yaml_map)

NodeConstructor.add_constructor(
    u'tag:yaml.org,2002:str',
    NodeConstructor.construct_yaml_str)

NodeConstructor.add_constructor(
    u'tag:yaml.org,2002:seq',
    NodeConstructor.construct_yaml_seq)

NodeConstructor.add_constructor(
    u'tag:yaml.org,2002:null',
    NodeConstructor.construct_yaml_null_error)


class MarkedLoader(Reader, Scanner, Parser, Composer, NodeConstructor, Resolver):
    """
    Class for marked loading YAML
    """

    # pylint: disable=non-parent-init-called,super-init-not-called

    def __init__(self, stream, filename):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        if cyaml:
            Parser.__init__(self, stream)
        else:
            Parser.__init__(self)
        Composer.__init__(self)
        SafeConstructor.__init__(self)
        Resolver.__init__(self)
        NodeConstructor.__init__(self, filename)

    def construct_mapping(self, node, deep=False):
        mapping = super(MarkedLoader, self).construct_mapping(node, deep=deep)
        # Add 1 so line numbering starts at 1
        # mapping['__line__'] = node.start_mark.line + 1
        mapping['__startline__'] = node.start_mark.line + 1
        mapping['__endline__'] = node.end_mark.line + 1
        return mapping


def multi_constructor(loader, tag_suffix, node):
    """
    Deal with !Ref style function format
    """

    if tag_suffix not in UNCONVERTED_SUFFIXES:
        tag_suffix = '{}{}'.format(FN_PREFIX, tag_suffix)

    constructor = None
    if tag_suffix == 'Fn::GetAtt':
        constructor = construct_getatt
    elif isinstance(node, ScalarNode):
        constructor = loader.construct_scalar
    elif isinstance(node, SequenceNode):
        constructor = loader.construct_sequence
    elif isinstance(node, MappingNode):
        constructor = loader.construct_mapping
    else:
        raise 'Bad tag: !{}'.format(tag_suffix)

    return DictNode({tag_suffix: constructor(node)}, node.start_mark, node.end_mark)


def construct_getatt(node):
    """
    Reconstruct !GetAtt into a list
    """

    if isinstance(node.value, str):
        return ListNode(node.value.split('.'), node.start_mark, node.end_mark)
    if isinstance(node.value, list):
        return ListNode([s.value for s in node.value], node.start_mark, node.end_mark)

    raise ValueError('Unexpected node type: {}'.format(type(node.value)))


def loads(yaml_string, fname=None):
    """
    Load the given YAML string
    """
    loader = MarkedLoader(yaml_string, fname)
    loader.add_multi_constructor('!', multi_constructor)

    template = loader.get_single_data()
    # Convert an empty file to an empty dict
    if template is None:
        template = {}

    return template


def load(filename: Path, content_type: ContentType) -> Tuple[DictNode, List[Tuple[int, str]]]:
    """
    Load the given YAML file
    """

    file_path = filename if isinstance(filename, Path) else Path(filename)
    content = file_path.read_text()

    if content_type == ContentType.CFN and "Resources" not in content:
        return {}, []
    elif content_type == ContentType.SLS and "provider" not in content:
        return {}, []

    file_lines = [(idx + 1, line) for idx, line in enumerate(content.splitlines(keepends=True))]

    return (loads(content, filename), file_lines)
