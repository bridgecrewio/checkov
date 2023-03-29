from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ECSContainerReadOnlyRoot(BaseResourceCheck):
    def __init__(self):
        """
        NIST.800-53.r5 AC-2(1), NIST.800-53.r5 AC-3, NIST.800-53.r5 AC-3(15), NIST.800-53.r5 AC-3(7),
        NIST.800-53.r5 AC-5, NIST.800-53.r5 AC-6
        ECS containers should be limited to read-only access to root filesystems
        """
        name = "Ensure ECS containers are limited to read-only access to root filesystems"
        id = "CKV_AWS_336"
        supported_resources = ["aws_ecs_task_definition"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if 'container_definitions' in conf.keys():
            if conf.get("container_definitions") and isinstance(conf.get("container_definitions"), list):
                containers = conf.get("container_definitions")[0]
                if len(containers) > 0:
                    for container in containers:
                        if isinstance(container, dict) and container.get("readonlyRootFilesystem"):
                            if not container.get("readonlyRootFilesystem"):
                                return CheckResult.FAILED
                            continue
                        return CheckResult.FAILED
                    return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = ECSContainerReadOnlyRoot()
