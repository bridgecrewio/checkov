from __future__ import annotations

import logging
from typing import Dict, Optional, Any

from checkov.cloudformation.parser import cfn_yaml
from checkov.common.parsers.json import parse as json_parse
from checkov.cloudformation.parser.cfn_keywords import TemplateSections
from yaml.scanner import ScannerError
from yaml import YAMLError

from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger

LOGGER = logging.getLogger(__name__)
add_resource_code_filter_to_logger(LOGGER)


def parse(
    filename: str, out_parsing_errors: Optional[Dict[str, str]] = None
) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | tuple[None, None]:
    """
    Decode filename into an object
    """
    template: "dict[str, Any] | list[dict[str, Any]] | None" = None
    template_lines = None
    error = None

    if out_parsing_errors is None:
        out_parsing_errors = {}

    try:
        (template, template_lines) = cfn_yaml.load(filename, cfn_yaml.ContentType.CFN)
    except FileNotFoundError as e:
        error = f'Template file not found: {e.filename}'
        LOGGER.error(error)
    except IsADirectoryError as e:
        error = f'Template references a directory, not a file: {e.filename}'
        LOGGER.error(error)
    except PermissionError as e:
        error = f'Permission denied when accessing {e.filename}'
        LOGGER.error(error)
    except UnicodeDecodeError as err:
        error = f"Cannot read file contents: {filename} - {err}"
        LOGGER.error(error)
    except cfn_yaml.CfnParseError as err:
        if "Null value at" in err.message:
            LOGGER.info(f"Null values do not exist in CFN templates: {filename} - {err}")
            return None, None

        error = f"Parsing error in file: {filename} - {err}"
        LOGGER.info(error)
    except ValueError as err:
        error = f"Parsing error in file: {filename} - {err}"
        LOGGER.info(error)
    except ScannerError as err:
        if err.problem in ["found character '\\t' that cannot start any token", "found unknown escape character"]:
            try:
                result = json_parse(filename, allow_nulls=False)
                if result:
                    template, template_lines = result
            except Exception as json_err:  # pylint: disable=W0703
                error = f"Template {filename} is malformed: {err.problem}. Tried to parse {filename} as JSON but got error: {json_err}"
                LOGGER.info(error)
    except YAMLError as err:
        if hasattr(err, 'problem') and err.problem in ["expected ',' or '}', but got '<scalar>'"]:
            try:
                result = json_parse(filename, allow_nulls=False)
                if result:
                    template, template_lines = result
            except Exception as json_err:  # pylint: disable=W0703
                error = f"Template {filename} is malformed: {err.problem}. Tried to parse {filename} as JSON but got error: {json_err}"
                LOGGER.info(error)
        else:
            error = f"Parsing error in file: {filename} - {err}"
            LOGGER.info(error)

    if error:
        out_parsing_errors[filename] = error

    if isinstance(template, dict):
        resources = template.get(TemplateSections.RESOURCES.value, None)
        if resources and isinstance(resources, dict):
            if '__file__' in resources:
                del resources['__file__']
            if "__startline__" in resources:
                del resources["__startline__"]
            if "__endline__" in resources:
                del resources["__endline__"]

    if template is None or template_lines is None:
        return None, None

    return template, template_lines
