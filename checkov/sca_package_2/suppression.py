from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

from charset_normalizer import from_path

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import FileToPersist
    from checkov.common.typing import _SkippedCheck

CVE_COMMENT_REGEX = re.compile(r"(checkov:skip=|bridgecrew:skip=) *(CVE-[\-\d]+)(:[^\n]+)?")
SUPPORTED_SKIP_PACKAGE_FILES = {
    "requirements.txt",
}


def extract_inline_suppressions(uploaded_files: list[FileToPersist], rootless_file_path: str) -> list[_SkippedCheck]:
    """Extracts inline suppression"""

    full_file_path = next(
        (file.full_file_path for file in uploaded_files if file.s3_file_key == rootless_file_path), None
    )
    if not full_file_path:
        logging.debug(f"Package file {rootless_file_path} could not be found in uploaded files")
        return []

    file_path = Path(full_file_path)
    if file_path.name not in PACKAGE_TYPE_EXTRACTOR:
        logging.debug(f"Package file type {file_path} not supported for skip comments")
        return []

    try:
        content = file_path.read_text()
    except UnicodeDecodeError:
        logging.debug(f"Encoding for file {file_path} is not UTF-8, trying to detect it")
        content = str(from_path(file_path).best())
    except Exception:
        logging.debug(f"Error while trying to read file {file_path}", exc_info=True)
        return []

    suppressions = PACKAGE_TYPE_EXTRACTOR[file_path.name](content)

    return suppressions


def extract_requirements_txt_suppressions(content: str) -> list[_SkippedCheck]:
    suppressions = []

    for line_number, line_text in enumerate(content.splitlines()):
        skip_search = re.search(CVE_COMMENT_REGEX, line_text)
        if skip_search:
            suppression: _SkippedCheck = {
                "id": skip_search.group(2),
                "suppress_comment": skip_search.group(3)[1:] if skip_search.group(3) else "No comment provided",
                "line_number": line_number,
            }
            suppressions.append(suppression)

    return suppressions


PACKAGE_TYPE_EXTRACTOR = {
    "requirements.txt": extract_requirements_txt_suppressions,
}
