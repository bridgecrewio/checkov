from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class S3AbortIncompleteUploads(BaseResourceCheck):
    def __init__(self) -> None:
        """
        If you don't set this value in a lifecycle configuration you'll end up paying for s3
        resources you never could use
        """
        name = "Ensure S3 lifecycle configuration sets period for aborting failed uploads"
        id = "CKV_AWS_300"
        supported_resources = ("aws_s3_bucket_lifecycle_configuration",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        self.evaluated_keys = ["rule"]
        rules = conf.get("rule")
        if rules and isinstance(rules, list):
            for idx_rule, rule in enumerate(rules):
                if rule.get("abort_incomplete_multipart_upload") and rule.get("status") == ["Enabled"]:
                    self.evaluated_keys = [f"rule/[{idx_rule}]/abort_incomplete_multipart_upload"]
                    filter_list = rule.get("filter")
                    if filter_list and isinstance(filter_list, list):
                        # if filter is empty then rule applies to all paths so we pass
                        found_non_empty_parameter = False
                        for filter_item in filter_list:
                            if isinstance(filter_item, dict):       # check each filter parameter
                                connected = filter_item.get('and')
                                if connected and connected[0]:
                                    filter_item = connected[0]
                                prefix = filter_item.get('prefix')
                                if prefix and prefix[0]:
                                    found_non_empty_parameter = True
                                    continue
                                object_size_greater_than = filter_item.get('object_size_greater_than')
                                if object_size_greater_than and object_size_greater_than[0]:
                                    found_non_empty_parameter = True
                                    continue
                                object_size_less_than = filter_item.get('object_size_less_than')
                                if object_size_less_than and object_size_less_than[0]:
                                    found_non_empty_parameter = True
                                    continue
                                tag = filter_item.get('tag')
                                if tag and tag[0]:
                                    found_non_empty_parameter = True
                                    continue

                        if found_non_empty_parameter:       # continue searching for rules
                            continue

                    return CheckResult.PASSED

        return CheckResult.FAILED


check = S3AbortIncompleteUploads()
