"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict

from charset_normalizer import from_path

from checkov.common.parsers.json.decoder import Decoder
from checkov.common.parsers.json.errors import DecodeError

LOGGER = logging.getLogger(__name__)


def load(filename: str, allow_nulls: bool = True) -> tuple[dict[str, Any], tuple[int, str]]:
    """
    Load the given JSON file
    """

    try:
        with open(filename) as fp:
            content = fp.read()
    except UnicodeDecodeError:
        LOGGER.info(f"Encoding for file {filename} is not UTF-8, trying to detect it")
        content = str(from_path(filename).best())

    file_lines = [(idx + 1, line) for idx, line in enumerate(content.splitlines(keepends=True))]

    return (json.loads(content, cls=Decoder, allow_nulls=allow_nulls), file_lines)


def parse(filename: str, allow_nulls: bool = True, out_parsing_errors: Dict[str, str] = {}) -> tuple[dict[str, Any], tuple[int, str]] | tuple[None, None]:
    template = None
    template_lines = None
    error = None
    try:
        (template, template_lines) = load(filename, allow_nulls)
    except DecodeError as e:
        logging.debug(f'Got DecodeError parsing file {filename}', exc_info=True)
        error = e
    except json.JSONDecodeError as e:
        # Most parsing errors will get caught by the exception above. But, if the file
        # is totally empty, and perhaps in other specific cases, the json library will
        # not even begin parsing with our custom logic that throws the exception above,
        # and will fail with this exception instead.
        logging.debug(f'Got JSONDecodeError parsing file {filename}', exc_info=True)
        error = e
    except UnicodeDecodeError as e:
        logging.debug(f'Got UnicodeDecodeError parsing file {filename}', exc_info=True)
        error = e

    if error:
        out_parsing_errors[filename] = str(error)

    return (template, template_lines)
