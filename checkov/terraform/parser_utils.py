from __future__ import annotations

import json
import logging
import os
import platform
import threading
from pathlib import Path
from typing import Any, cast, Optional, TextIO, Type

import hcl2

from checkov.common.util.env_vars_config import env_vars_config
from checkov.common.util.stopit import ThreadingTimeout, SignalTimeout
from checkov.common.util.stopit.utils import BaseTimeout
from checkov.terraform import validate_malformed_definitions, clean_bad_definitions
from checkov.terraform.modules.module_utils import _Hcl2Payload


def load_or_die_quietly(
    file: str | Path | os.DirEntry[str], parsing_errors: dict[str, Exception], clean_definitions: bool = True
) -> Optional[_Hcl2Payload]:
    """
    Load JSON or HCL, depending on filename.
    :return: None if the file can't be loaded
    """
    file_path = os.fspath(file)
    file_name = os.path.basename(file_path)

    if file_name.endswith(".tfvars"):
        clean_definitions = False

    try:
        logging.debug(f"Parsing {file_path}")

        with open(file_path, "r", encoding="utf-8-sig") as f:
            if file_name.endswith(".json"):
                return cast("_Hcl2Payload", json.load(f))
            else:
                raw_data = __parse_with_timeout(f)
                non_malformed_definitions = validate_malformed_definitions(raw_data)
                if clean_definitions:
                    return clean_bad_definitions(non_malformed_definitions)
                else:
                    return non_malformed_definitions
    except Exception as e:
        logging.debug(f"failed while parsing file {file_path}", exc_info=True)
        parsing_errors[file_path] = e
        return None


# if we are not running in a thread, run the hcl2.load function with a timeout, to prevent from getting stuck in parsing.
def __parse_with_timeout(f: TextIO) -> dict[str, list[dict[str, Any]]]:
    # setting up timeout class
    timeout_class: Optional[Type[BaseTimeout]] = None
    if platform.system() == "Windows":
        timeout_class = ThreadingTimeout
    elif threading.current_thread() is threading.main_thread():
        timeout_class = SignalTimeout

    # if we're not running on the main thread, don't use timeout
    parsing_timeout = env_vars_config.HCL_PARSE_TIMEOUT_SEC or 0
    if not timeout_class or not parsing_timeout:
        return hcl2.load(f)

    with timeout_class(parsing_timeout) as to_ctx_mgr:
        raw_data = hcl2.load(f)
    if to_ctx_mgr.state == to_ctx_mgr.TIMED_OUT:
        logging.debug(f"reached timeout when parsing file {f} using hcl2")
        raise Exception(f"file took more than {parsing_timeout} seconds to parse")
    return raw_data
