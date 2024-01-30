from __future__ import annotations
from typing import Any
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class RDSEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the RDS is securely encrypted at rest"
        id = "CKV_AWS_000"
        supported_resources = ['aws_db_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "storage_encrypted"

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        result = super().scan_resource_conf(conf=conf)
        provider_name = conf.get("provider")
        if provider_name and isinstance(provider_name, list):
            providers = [g[1] for g in self.graph.nodes() if g[1].get('block_type_') == 'provider']
            provider = next((prov for prov in providers if prov[CustomAttributes.BLOCK_NAME] == provider_name[0]), None)
            if provider and provider.get("use_fips_endpoint") is True:
                return CheckResult.PASSED
        return result


check = RDSEncryption()
