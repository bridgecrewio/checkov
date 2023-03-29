from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ECSContainerHostProcess(BaseResourceCheck):
    def __init__(self):
        """
        NIST.800-53.r5 CA-9(1), NIST.800-53.r5 CM-2
        ECS task definitions should not share the host's process namespace
        """
        name = "Ensure ECS task definitions should not share the host's process namespace"
        id = "CKV_AWS_335"
        supported_resources = ["aws_ecs_task_definition"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if 'container_definitions' in conf.keys():
            if conf.get("container_definitions") and isinstance(conf.get("container_definitions"), list):
                containers = conf.get("container_definitions")[0]
                if len(containers) > 0:
                    for container in containers:
                        if isinstance(container, dict) and container.get("pidMode"):
                            pidmode = container.get("pidMode")
                            if pidmode == "host":
                                return CheckResult.FAILED
                    return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = ECSContainerHostProcess()
