from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from yaml.scanner import ScannerError
from yaml import YAMLError

from checkov.common.parsers.json import parse as json_parse
from checkov.common.parsers.yaml import loader
from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.common.util.file_utils import read_file_with_any_encoding

LOGGER = logging.getLogger(__name__)
add_resource_code_filter_to_logger(LOGGER)


def parse(filename: str) -> tuple[dict[str, Any], list[tuple[int, str]]] | tuple[None, None]:
    """Decode filename into an object"""

    template = None
    template_lines = None
    try:
        template, template_lines = load(filename)
    except IOError as e:
        if e.errno == 2:
            LOGGER.error(f"Template file not found: {filename}")
        elif e.errno == 21:
            LOGGER.error(f"Template references a directory, not a file: {filename}")
        elif e.errno == 13:
            LOGGER.error(f"Permission denied when accessing template file: {filename}")
    except UnicodeDecodeError:
        LOGGER.error(f"Cannot read file contents: {filename}")
    except ScannerError as err:
        if err.problem in ("found character '\\t' that cannot start any token", "found unknown escape character"):
            try:
                result = json_parse(filename, allow_nulls=False)
                if result:
                    template, template_lines = result  # type:ignore[assignment]  # this is handled by the next line
                    if isinstance(template, list):
                        # should not happen and is more relevant for type safety
                        template = template[0]
            except Exception:
                LOGGER.error(f"Template {filename} is malformed: {err.problem}")
                LOGGER.error(f"Tried to parse {filename} as JSON", exc_info=True)
    except YAMLError:
        LOGGER.info(f"Failed to parse {filename}")
        LOGGER.debug("With Exception", exc_info=True)

    if template is None or template_lines is None:
        return None, None

    return template, template_lines


def load(filename: Path | str) -> tuple[dict[str, Any], list[tuple[int, str]]]:
    """
    Load the given JSON/YAML file
    """

    content = read_file_with_any_encoding(file_path=filename)

    if not all(key in content for key in ("$schema", "contentVersion")):
        return {}, []

    file_lines = [(idx + 1, line) for idx, line in enumerate(content.splitlines(keepends=True))]

    template: "dict[str, Any] | list[dict[str, Any]]" = loader.loads(content=content)
    if not template:
        template = {}
    if isinstance(template, list):
        template = template[0]

    return template, file_lines
