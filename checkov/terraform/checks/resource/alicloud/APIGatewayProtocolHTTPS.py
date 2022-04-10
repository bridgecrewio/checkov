from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class APIGatewayProtocolHTTPS(BaseResourceCheck):
    def __init__(self):
        name = "Ensure API Gateway API Protocol HTTPS"
        id = "CKV_ALI_21"
        supported_resources = ['alicloud_api_gateway_api']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("request_config") and isinstance(conf.get("request_config"), list):
            configs = conf.get("request_config")
            for idx, config in enumerate(configs):
                if config.get("protocol") != ["HTTPS"]:
                    self.evaluated_keys = [f"request_config/[{idx}]/protocol"]
                    return CheckResult.FAILED
            return CheckResult.PASSED
        self.evaluated_keys = [""]
        return CheckResult.FAILED


check = APIGatewayProtocolHTTPS()
