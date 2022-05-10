from __future__ import annotations

from typing import Any

from checkov.common.util.type_forcers import force_int
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class BranchProtectionReviewNumTwo(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure at least two approving reviews for PRs"
        id = "CKV_GIT_5"
        supported_resources = ["github_branch_protection_v3", "github_branch_protection"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if conf.get("required_pull_request_reviews") and isinstance(conf.get("required_pull_request_reviews"), list):
            review = conf.get("required_pull_request_reviews")[0]
            if review.get("required_approving_review_count") and isinstance(review.get("required_approving_review_count"),list):
                count = force_int(review.get("required_approving_review_count")[0])
                if count and count >= 2:
                    return CheckResult.PASSED
        self.evaluated_keys = ["required_pull_request_reviews/[0]/required_approving_review_count"]
        return CheckResult.FAILED


check = BranchProtectionReviewNumTwo()
