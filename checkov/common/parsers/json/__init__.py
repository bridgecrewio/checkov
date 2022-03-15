"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

import json
import logging
from typing import Any

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


def parse(filename: str, allow_nulls: bool = True) -> tuple[dict[str, Any], tuple[int, str]] | tuple[None, None]:
    template = None
    template_lines = None
    try:
        (template, template_lines) = load(filename, allow_nulls)
    except DecodeError:
        pass
    except json.JSONDecodeError:
        # Most parsing errors will get caught by the exception above. But, if the file
        # is totally empty, and perhaps in other specific cases, the json library will
        # not even begin parsing with our custom logic that throws the exception above,
        # and will fail with this exception instead.
        pass
    except UnicodeDecodeError:
        pass

    return (template, template_lines)
