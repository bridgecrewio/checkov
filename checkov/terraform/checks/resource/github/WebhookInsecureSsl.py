from typing import Dict, List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class WebhookInsecureSsl(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Repository Webhook uses secure Ssl"
        id = "CKV_GIT_2"
        supported_resources = ["github_repository_webhook"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        configuration = conf.get("configuration")
        ssl_insecure = configuration.get("insecure_ssl")
        if ssl_insecure == [False]:
            return CheckResult.PASSED
        return CheckResult.FAILED

check = WebhookInsecureSsl()
