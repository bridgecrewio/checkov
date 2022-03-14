"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
import logging
from typing import Dict

from checkov.common.parsers.json.decoder import Decoder
from checkov.common.parsers.json.errors import DecodeError

LOGGER = logging.getLogger(__name__)


def load(filename, allow_nulls=True):
    """
    Load the given JSON file
    """

    content = ''

    with open(filename) as fp:
        content = fp.read()
        fp.seek(0)
        file_lines = [(ind + 1, line) for (ind, line) in
                      list(enumerate(fp.readlines()))]

    return (json.loads(content, cls=Decoder, allow_nulls=allow_nulls), file_lines)


def parse(filename, allow_nulls=True, out_parsing_errors: Dict[str, str], ):
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
