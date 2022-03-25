from __future__ import annotations

import re

from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import (
    integration as metadata_integration,
)
from checkov.common.comment.enum import COMMENT_REGEX
from checkov.common.models.enums import CheckResult
from checkov.common.typing import _CheckResult, _SkippedCheck


def collect_suppressions_for_report(code_lines: list[tuple[int, str]]) -> dict[str, _CheckResult]:
    """Searches for suppressions in a config block to be used in a report"""

    suppressions = {}

    for _, line in code_lines:
        skip_search = re.search(COMMENT_REGEX, line)
        if skip_search:
            check_result: _CheckResult = {
                "result": CheckResult.SKIPPED,
                "suppress_comment": skip_search.group(3)[1:] if skip_search.group(3) else "No comment provided",
            }
            suppressions[skip_search.group(2)] = check_result

    return suppressions


def collect_suppressions_for_context(code_lines: list[tuple[int, int | str]]) -> list[_SkippedCheck]:
    """Searches for suppressions in a config block to be used in a context"""

    skipped_checks = []
    bc_id_mapping = metadata_integration.bc_to_ckv_id_mapping
    for _, line in code_lines:
        skip_search = re.search(COMMENT_REGEX, str(line))
        if skip_search:
            skipped_check: _SkippedCheck = {
                "id": skip_search.group(2),
                "suppress_comment": skip_search.group(3)[1:] if skip_search.group(3) else "No comment provided",
            }
            # No matter which ID was used to skip, save the pair of IDs in the appropriate fields
            if bc_id_mapping and skipped_check["id"] in bc_id_mapping:
                skipped_check["bc_id"] = skipped_check["id"]
                skipped_check["id"] = bc_id_mapping[skipped_check["id"]]
            elif metadata_integration.check_metadata:
                skipped_check["bc_id"] = metadata_integration.get_bc_id(skipped_check["id"])

            skipped_checks.append(skipped_check)

    return skipped_checks
