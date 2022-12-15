from __future__ import annotations

import datetime
from typing import Any

from bc_jsonpath_ng import parse

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.github.base_github_configuration_check import BaseGithubCheck
from checkov.github.schemas.branch import schema as branch_schema
from checkov.json_doc.enums import BlockType


class GithubDisallowInactiveBranch60Days(BaseGithubCheck):
    def __init__(self) -> None:
        name = "Ensure inactive branches are reviewed and removed periodically"
        id = "CKV_GITHUB_15"
        categories = (CheckCategories.SUPPLY_CHAIN,)
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=("*",),
            block_type=BlockType.DOCUMENT,
        )

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult:  # type:ignore[override]
        if branch_schema.validate(conf):
            evaluated_key = self.get_evaluated_keys()[0].replace("/", ".")
            jsonpath_expression = parse(f"$..{evaluated_key}")
            matches = jsonpath_expression.find(conf)
            if matches:
                last_commit = matches[0].value.get('date', '')
                if last_commit:
                    two_months_ago = datetime.datetime.today() - datetime.timedelta(days=60)
                    last_commit_date = datetime.datetime.strptime(last_commit, "%Y-%m-%dT%H:%M:%SZ")
                    if last_commit_date < two_months_ago:
                        return CheckResult.FAILED
                    return CheckResult.PASSED
        return CheckResult.UNKNOWN

    def get_evaluated_keys(self) -> list[str]:
        return ['commit/commit/author']


check = GithubDisallowInactiveBranch60Days()
