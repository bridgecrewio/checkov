from __future__ import annotations
from typing import Any
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class JustForTest(BaseResourceValueCheck):
    def __init__(self):
        name = "Just for test (Like CKV2_GCP_18)"
        id = "CKV_AWS_99999"
        supported_resources = ['google_compute_network']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "storage_encrypted"

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        result = super().scan_resource_conf(conf=conf)
        # For RustworkX Framework -
        resources = [g[1] for g in self.graph.nodes() if g[1].get('block_type_') == 'resource']

        # Do something here.
        if resources:
            return CheckResult.PASSED
        return result


check = JustForTest()
