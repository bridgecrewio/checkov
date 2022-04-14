from __future__ import annotations

import logging
from typing import Any

from yaml import YAMLError

import checkov.common.parsers.yaml.loader as loader

logger = logging.getLogger(__name__)


def parse(filename: str) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
    template = None
    template_lines = None
    try:
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            (template, template_lines) = loader.load(filename)

        if template:
            if isinstance(template, list):
                for t in template:
                    if t and (isinstance(t, dict) or isinstance(t, list)):
                        return t, template_lines
            else:
                return None
        else:
            return None
    except IOError as e:
        if e.errno == 2:
            logger.error('Template file not found: %s', filename)
            return None
        elif e.errno == 21:
            logger.error('Template references a directory, not a file: %s',
                         filename)
            return None
        elif e.errno == 13:
            logger.error('Permission denied when accessing template file: %s',
                         filename)
            return None
    except UnicodeDecodeError:
        logger.error('Cannot read file contents: %s', filename)
        return None
    except YAMLError:
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            logger.debug('Cannot read file contents: %s - is it a yaml?', filename)
        return None

    return None
