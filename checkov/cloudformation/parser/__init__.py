import logging
from json.decoder import JSONDecodeError
from typing import Tuple, Optional, List, Union, Dict

from checkov.cloudformation.parser import cfn_yaml, cfn_json
from checkov.cloudformation.parser.node import dict_node
from checkov.cloudformation.parser.cfn_keywords import TemplateSections
from yaml.parser import ScannerError
from yaml import YAMLError

LOGGER = logging.getLogger(__name__)


def parse(filename: str, out_parsing_errors: Dict[str, str] = {}) -> Union[Tuple[dict_node, List[Tuple[int, str]]], Tuple[None, None]]:
    """
        Decode filename into an object
    """
    template = None
    template_lines = None
    error = None
    try:
        (template, template_lines) = cfn_yaml.load(filename)
    except IOError as err:
        if err.errno == 2:
            error = f"Template file not found: {filename} - {err}"
            LOGGER.error(error)
        elif err.errno == 21:
            error = f"Template references a directory, not a file: {filename} - {err}"
            LOGGER.error(error)
        elif err.errno == 13:
            error = f"Permission denied when accessing template file: {filename} - {err}"
            LOGGER.error(error)
    except UnicodeDecodeError as err:
        error = f"Cannot read file contents: {filename}"
        LOGGER.error(error)
    except cfn_yaml.CfnParseError as err:
        error = f"Parsing error in file {filename}"
        LOGGER.info(error)
    except ScannerError as err:
        if err.problem in ["found character '\\t' that cannot start any token", "found unknown escape character"]:
            try:
                (template, template_lines) = cfn_json.load(filename)
            except cfn_json.JSONDecodeError:
                pass
            except JSONDecodeError:
                pass
            except Exception as json_err:  # pylint: disable=W0703
                error = f"Template {filename} is malformed: {err.problem}. Tried to parse {filename} as JSON but got error: {json_err}"
                LOGGER.info(error)
    except YAMLError as err:
        error = f"Parsing error in file: {filename} - {err}"
        LOGGER.info(error)

    if error:
        out_parsing_errors[filename] = error

    if isinstance(template, dict):
        resources = template.get(TemplateSections.RESOURCES.value, None)
        if resources:
            if '__startline__' in resources:
                del resources['__startline__']
            if '__endline__' in resources:
                del resources['__endline__']
    return template, template_lines
