from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ECSTaskDefinitionRoleCheck(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that the Execution Role ARN and the Task Role ARN are different in ECS Task definitions"
        id = "CKV_AWS_249"
        supported_resources = ("aws_ecs_task_definition",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        self.evaluated_keys = ["execution_role_arn", "task_role_arn"]
        if "execution_role_arn" in conf.keys() and "task_role_arn" in conf.keys():
            execution_role_arn = conf["execution_role_arn"]
            if not execution_role_arn or execution_role_arn == [None]:
                # this occurs in TF plan files, when no role was set, very unlikely
                return CheckResult.PASSED

            if conf["execution_role_arn"] == conf["task_role_arn"]:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = ECSTaskDefinitionRoleCheck()
