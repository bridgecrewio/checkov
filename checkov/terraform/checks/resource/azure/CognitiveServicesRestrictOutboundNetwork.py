from typing import Dict, List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class CognitiveServicesRestrictOutboundNetwork(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Cognitive Services accounts restrict outbound network traffic."
        id = "CKV_AZURE_247"
        supported_resources = ('azurerm_cognitive_account', )
        categories = (CheckCategories.NETWORKING, )
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if conf.get("kind", [""])[0].lower() != 'openai':
            return CheckResult.PASSED

        outbound_network_access_restricted = conf.get('outbound_network_access_restricted', [None])[0]
        fqdns = conf.get('fqdns', [[]])[0]
        if not outbound_network_access_restricted or not fqdns:
            return CheckResult.FAILED

        return CheckResult.PASSED


check = CognitiveServicesRestrictOutboundNetwork()
