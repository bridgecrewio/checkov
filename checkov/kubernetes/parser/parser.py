from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from yaml import YAMLError

from checkov.kubernetes.parser import k8_yaml, k8_json

logger = logging.getLogger(__name__)


def parse(filename: str) -> tuple[list[dict[str, Any]], list[tuple[int, str]]] | None:
    template = None
    template_lines: "list[tuple[int, str]]" = []
    valid_templates = []
    try:
        if filename.endswith((".yaml", ".yml")):
            (template, template_lines) = k8_yaml.load(Path(filename))
        if filename.endswith(".json"):
            (template, template_lines) = k8_json.load(Path(filename))
        if template:
            if isinstance(template, list):
                for t in template:
                    if t and isinstance(t, dict) and 'apiVersion' in t.keys() and 'kind' in t.keys():
                        valid_templates.append(t)
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

    return valid_templates, template_lines
