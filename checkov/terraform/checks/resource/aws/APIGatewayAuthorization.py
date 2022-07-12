from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import List


class APIGatewayAuthorization(BaseResourceCheck):

    def __init__(self):
        name = "Ensure there is no open access to back-end resources through API"
        id = "CKV_AWS_59"
        supported_resources = ['aws_api_gateway_method']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'http_method' in conf and conf['http_method'][0] != "OPTIONS" and conf['authorization'][0] == "NONE" \
                and ('api_key_required' not in conf or conf['api_key_required'][0] is False):
            return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['http_method', 'authorization', 'api_key_required']


check = APIGatewayAuthorization()
