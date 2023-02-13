from __future__ import annotations

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class DatasyncLocationExposesSecrets(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Datasync Location object storage doesn't expose secrets"
        id = "CKV_AWS_295"
        supported_resources = ("aws_datasync_location_object_storage",)
        categories = (CheckCategories.SECRETS,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        self.evaluated_keys = ['secret_key']
        if 'secret_key' in conf:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = DatasyncLocationExposesSecrets()
