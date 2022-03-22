from __future__ import annotations

import logging
from typing import Any

from yaml.parser import ScannerError
from yaml import YAMLError

from checkov.arm.parser import cfn_yaml
from checkov.common.parsers.json import parse as json_parse
from checkov.common.parsers.node import DictNode


LOGGER = logging.getLogger(__name__)


def parse(filename: str) -> tuple[dict[str, Any], tuple[int, str]] | tuple[None, None]:
    """ Decode filename into an object """

    template = None
    template_lines = None
    try:
        (template, template_lines) = cfn_yaml.load(filename)
    except IOError as e:
        if e.errno == 2:
            LOGGER.error(f"Template file not found: {filename}")
        elif e.errno == 21:
            LOGGER.error(f"Template references a directory, not a file: {filename}")
        elif e.errno == 13:
            LOGGER.error(f"Permission denied when accessing template file: {filename}")
    except UnicodeDecodeError:
        LOGGER.error(f"Cannot read file contents: {filename}")
    except cfn_yaml.CfnParseError:
        pass
    except ScannerError as err:
        if err.problem in ("found character '\\t' that cannot start any token", "found unknown escape character"):
            try:
                (template, template_lines) = json_parse(filename, allow_nulls=False)
            except Exception:
                LOGGER.error(f"Template {filename} is malformed: {err.problem}")
                LOGGER.error(f"Tried to parse {filename} as JSON", exc_info=True)
    except YAMLError:
        pass

    if template is not None and isinstance(template, DictNode) and "$schema" in template and "resources" in template:
        return template, template_lines
    return None, None
