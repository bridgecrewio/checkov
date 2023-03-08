from __future__ import annotations

import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, cast

from charset_normalizer import from_path

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import FileToPersist
    from checkov.common.typing import _SkippedCheck, _ScaSuppressions

CVE_COMMENT_PATTERN = re.compile(r"(checkov:skip=|bridgecrew:skip=) *(CVE-[\-\d]+)(:[^\n]+)?")
PACKAGE_COMMENT_PATTERN = re.compile(r"(checkov:skip=|bridgecrew:skip=) *([^\n]+)?")
PACKAGE_CVE_PATTERN = re.compile(r"(?P<package_name>.+)\[(?P<cves>[\w\-,]+)]")
SUPPORTED_SKIP_PACKAGE_FILES = {
    "requirements.txt",
}


def extract_inline_suppressions(uploaded_files: list[FileToPersist], rootless_file_path: str) -> _ScaSuppressions:
    """Extracts inline suppression

    ex. response
    suppressions = {
        "cve": {
            "CVE-2023-123": {
                "suppress_comment": "bla bla",
                "line_number": 1,
            }
        },
        "package": {
            "django": {
                "CVE-2023-456": {
                    "suppress_comment": "bla bla",
                    "line_number": 1,
                }
            }
            "flask": {
                "suppress_comment": "bla bla",
                "line_number": 1,
            }
        }
    }
    """

    full_file_path = next(
        (file.full_file_path for file in uploaded_files if file.s3_file_key == rootless_file_path), None
    )
    if not full_file_path:
        logging.debug(f"Package file {rootless_file_path} could not be found in uploaded files")
        return {}

    file_path = Path(full_file_path)
    if file_path.name not in PACKAGE_TYPE_EXTRACTOR:
        logging.debug(f"Package file type {file_path} not supported for skip comments")
        return {}

    try:
        content = file_path.read_text()
    except UnicodeDecodeError:
        logging.debug(f"Encoding for file {file_path} is not UTF-8, trying to detect it")
        content = str(from_path(file_path).best())
    except Exception:
        logging.debug(f"Error while trying to read file {file_path}", exc_info=True)
        return {}

    suppressions = PACKAGE_TYPE_EXTRACTOR[file_path.name](content)

    return suppressions


def extract_requirements_txt_suppressions(content: str) -> _ScaSuppressions:
    suppressions: _ScaSuppressions = defaultdict(dict)  # type:ignore[assignment]

    for line_number, line_text in enumerate(content.splitlines()):
        package_skip = re.search(PACKAGE_COMMENT_PATTERN, line_text)
        if package_skip:
            # check if it is just a CVE skip
            cve_skip = re.search(CVE_COMMENT_PATTERN, line_text)
            if cve_skip:
                suppression: _SkippedCheck = {
                    "suppress_comment": cve_skip.group(3)[1:] if cve_skip.group(3) else "No comment provided",
                    "line_number": line_number,
                }
                suppressions["cve"][cve_skip.group(2)] = suppression
            else:
                package_name = package_skip.group(2)
                suppress_comment = None
                if ":" in package_name:
                    # could result in incorrect splitting, if the package name has a colon
                    package_name, suppress_comment = package_name.rsplit(":", maxsplit=1)

                if "[" in package_name and "]" in package_name:
                    # specific CVEs should be suppressed for the package
                    package_cves = re.search(PACKAGE_CVE_PATTERN, package_name)
                    if package_cves:
                        package_cve_suppressions = {
                            package_cve: cast(
                                "_SkippedCheck",
                                {
                                    "suppress_comment": suppress_comment if suppress_comment else "No comment provided",
                                    "line_number": line_number,
                                },
                            )
                            for package_cve in package_cves.group("cves").split(",")
                        }
                        suppressions["package"][package_cves.group("package_name")] = package_cve_suppressions
                        continue

                suppression = {
                    "suppress_comment": suppress_comment if suppress_comment else "No comment provided",
                    "line_number": line_number,
                }
                suppressions["package"][package_name] = suppression

    return suppressions


PACKAGE_TYPE_EXTRACTOR = {
    "requirements.txt": extract_requirements_txt_suppressions,
}
