from __future__ import annotations
from typing import Any
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class APIGatewayMethodWOAuth(BaseResourceCheck):
    def __init__(self):
        name = "Ensure API gateway method has authorization or API key set"
        id = "CKV2_AWS_300"
        supported_resources = ['aws_api_gateway_method']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        g = self.graph.nodes()
        return CheckResult.FAILED

        #provider_name = conf.get("provider")
        #if provider_name and isinstance(provider_name, list):
        #    providers = [g[1] for g in self.graph.nodes() if g[1].get('block_type_') == 'provider']
        #    provider = next((prov for prov in providers if prov[CustomAttributes.BLOCK_NAME] == provider_name[0]), None)
        #    if provider and provider.get("use_fips_endpoint") is True:
        #        return CheckResult.PASSED
        #return result


check = APIGatewayMethodWOAuth()