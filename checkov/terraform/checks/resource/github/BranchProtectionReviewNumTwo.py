from __future__ import annotations

from typing import Any

from checkov.common.util.type_forcers import force_int
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class BranchProtectionReviewNumTwo(BaseResourceCheck):
    def __init__(self) -> None:
        name = "GitHub pull requests should require at least 2 approvals"
        id = "CKV_GIT_5"
        supported_resources = ("github_branch_protection_v3", "github_branch_protection")
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        reviews = conf.get("required_pull_request_reviews")
        if reviews and isinstance(reviews, list):
            review_count = reviews[0].get("required_approving_review_count")
            if review_count and isinstance(review_count, list):
                count = force_int(review_count[0])
                if count and count >= 2:
                    return CheckResult.PASSED
        self.evaluated_keys = ["required_pull_request_reviews/[0]/required_approving_review_count"]
        return CheckResult.FAILED


check = BranchProtectionReviewNumTwo()
