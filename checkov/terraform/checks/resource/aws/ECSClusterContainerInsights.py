from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class ECSClusterContainerInsights(BaseResourceCheck):
    def __init__(self):
        name = "Ensure container insights are enabled on ECS cluster"
        id = "CKV_AWS_65"
        supported_resources = ['aws_ecs_cluster']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'setting' in conf.keys():
            if conf['setting']['name'] == 'containerInsights' and conf['setting']['value'] == 'enabled':
                return CheckResult.PASSED
        return CheckResult.FAILED


check = ECSClusterContainerInsights()
