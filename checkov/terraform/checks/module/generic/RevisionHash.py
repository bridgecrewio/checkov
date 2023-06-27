from __future__ import annotations

import re
from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.module.base_module_check import BaseModuleCheck

COMMIT_ID_PATTERN = re.compile(r"\?(ref=)(?P<commit_id>([0-9a-f]{5,40}))")


class RevisionHash(BaseModuleCheck):
    def __init__(self) -> None:
        name = "Ensure Terraform module sources use a commit hash"
        id = "CKV_TF_1"
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(name=name, id=id, categories=categories)

    def scan_module_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        source = conf.get("source")
        if source and isinstance(source, list):
            source_url = source[0]
            if source_url.startswith(("./", "../")):
                # local modules can't be pinned to a commit hash
                return CheckResult.UNKNOWN
            if "?ref" in source_url and re.search(COMMIT_ID_PATTERN, source_url):
                # do first a quick lookup, if '?ref' exists in the string before actually searching for the commit hash
                return CheckResult.PASSED

        return CheckResult.FAILED


check = RevisionHash()
