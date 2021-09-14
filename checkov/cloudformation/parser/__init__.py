import logging
from typing import Tuple, Optional, List, Union

from checkov.cloudformation.parser import cfn_yaml
from checkov.common.parsers.json import parse as json_parse
from checkov.common.parsers.node import dict_node
from checkov.cloudformation.parser.cfn_keywords import TemplateSections
from yaml.parser import ScannerError
from yaml import YAMLError

LOGGER = logging.getLogger(__name__)


def parse(filename: str) -> Union[Tuple[dict_node, List[Tuple[int, str]]], Tuple[None, None]]:
    """
        Decode filename into an object
    """
    template = None
    template_lines = None
    try:
        (template, template_lines) = cfn_yaml.load(filename)
    except IOError as e:
        if e.errno == 2:
            LOGGER.error("Template file not found: %s", filename)
        elif e.errno == 21:
            LOGGER.error("Template references a directory, not a file: %s", filename)
        elif e.errno == 13:
            LOGGER.error("Permission denied when accessing template file: %s", filename)
    except UnicodeDecodeError as err:
        LOGGER.error("Cannot read file contents: %s", filename)
    except cfn_yaml.CfnParseError as err:
        pass
    except ScannerError as err:
        if err.problem in ["found character '\\t' that cannot start any token", "found unknown escape character"]:
            try:
                (template, template_lines) = json_parse(filename, allow_nulls=False)
            except Exception as json_err:  # pylint: disable=W0703
                LOGGER.error("Template %s is malformed: %s", filename, err.problem)
                LOGGER.error("Tried to parse %s as JSON but got error: %s", filename, str(json_err))
    except YAMLError as err:
        pass

    if isinstance(template, dict):
        resources = template.get(TemplateSections.RESOURCES.value, None)
        if resources:
            if '__startline__' in resources:
                del resources['__startline__']
            if '__endline__' in resources:
                del resources['__endline__']
    return template, template_lines
