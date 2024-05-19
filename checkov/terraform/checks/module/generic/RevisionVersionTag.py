from __future__ import annotations

import re
from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.module.base_module_check import BaseModuleCheck
from .RevisionHash import check as RevisionHashCheck

VERSION_PATTERN = re.compile(r"[?&](ref=).*(\d\.\d).*")


class RevisionVersionTag(BaseModuleCheck):
    def __init__(self) -> None:
        name = "Ensure Terraform module sources use a tag with a version number"
        id = "CKV_TF_2"
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(name=name, id=id, categories=categories)

    def scan_module_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # this check is a more lenient version of the hash check, so if that one passes (or is unknown due to a local module),
        # then we are done
        hash_result = RevisionHashCheck.scan_module_conf(conf)
        if hash_result != CheckResult.FAILED:
            return hash_result

        source = conf.get("source")
        if source and isinstance(source, list):
            source_url = source[0]
            if ("?ref" in source_url or "&ref" in source_url) and re.search(VERSION_PATTERN, source_url):
                return CheckResult.PASSED

        return CheckResult.FAILED


check = RevisionVersionTag()
