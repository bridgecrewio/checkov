from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class LBTargetGroupDefinesHealthCheck(BaseResourceCheck):
    def __init__(self) -> None:

        """
        PCI v3.2.1
        """

        name = "Ensure HTTP HTTPS Target group defines Healthcheck"
        id = "CKV_AWS_261"
        supported_resources = ["aws_lb_target_group", "aws_alb_target_group"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get('protocol') == ['HTTP'] or conf.get('protocol') == ['HTTPS']:
            if conf.get('health_check') and isinstance(conf.get('health_check'), list):
                healthcheck = conf.get('health_check')[0]
                if healthcheck.get('path'):
                    return CheckResult.PASSED
            self.evaluated_keys = ['health_check']
            return CheckResult.FAILED
        return CheckResult.UNKNOWN


check = LBTargetGroupDefinesHealthCheck()

