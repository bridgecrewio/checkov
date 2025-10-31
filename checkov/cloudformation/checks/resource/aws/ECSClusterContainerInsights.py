from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class ECSClusterContainerInsights(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure container insights are enabled on ECS cluster"
        id = "CKV_AWS_65"
        supported_resources = ("AWS::ECS::Cluster",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        """
            Looks for container insights configuration on ECS cluster:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-cluster.html#cfn-ecs-cluster-clustersettings
        :param conf: AWS::ECS::Cluster configuration
        :return: <CheckResult>
        """
        self.evaluated_keys = ["Properties"]
        properties = conf.get("Properties")
        if properties and isinstance(properties, dict):
            settings = properties.get("ClusterSettings")
            if settings and isinstance(settings, list):
                self.evaluated_keys = ["Properties/ClusterSettings"]
                for setting in settings:
                    if setting["Name"] == "containerInsights" and setting["Value"] in ["enhanced", "enabled"]:
                        return CheckResult.PASSED
        return CheckResult.FAILED


check = ECSClusterContainerInsights()
