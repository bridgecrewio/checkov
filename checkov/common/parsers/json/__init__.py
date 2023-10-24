"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from checkov.common.parsers.json.decoder import Decoder
from checkov.common.parsers.json.errors import DecodeError
from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.common.util.file_utils import read_file_with_any_encoding

LOGGER = logging.getLogger(__name__)
add_resource_code_filter_to_logger(LOGGER)


def load(
    filename: str | Path, allow_nulls: bool = True, content: str | None = None
) -> tuple[dict[str, Any], list[tuple[int, str]]]:
    """
    Load the given JSON file
    """

    if not content:
        content = read_file_with_any_encoding(file_path=filename)

    file_lines = [(idx + 1, line) for idx, line in enumerate(content.splitlines(keepends=True))]

    return json.loads(content, cls=Decoder, allow_nulls=allow_nulls), file_lines


def parse(
    filename: str | Path,
    allow_nulls: bool = True,
    out_parsing_errors: dict[str, str] | None = None,
    file_content: str | None = None,
) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
    error: Exception | None = None
    try:
        return load(filename=filename, allow_nulls=allow_nulls, content=file_content)
    except DecodeError as e:
        logging.debug(f"Got DecodeError parsing file {filename}", exc_info=True)
        error = e
    except json.JSONDecodeError as e:
        # Most parsing errors will get caught by the exception above. But, if the file
        # is totally empty, and perhaps in other specific cases, the json library will
        # not even begin parsing with our custom logic that throws the exception above,
        # and will fail with this exception instead.
        logging.debug(f"Got JSONDecodeError parsing file {filename}", exc_info=True)
        error = e
    except UnicodeDecodeError as e:
        logging.debug(f"Got UnicodeDecodeError parsing file {filename}", exc_info=True)
        error = e

    if error:
        if out_parsing_errors is None:
            out_parsing_errors = {}
        out_parsing_errors[str(filename)] = str(error)

    return None
