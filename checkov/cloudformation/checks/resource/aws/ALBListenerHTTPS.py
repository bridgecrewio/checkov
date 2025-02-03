from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.cloudformation.parser.cfn_keywords import ConditionFunctions, IntrinsicFunctions


class ALBListenerHTTPS(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure ALB protocol is HTTPS"
        id = "CKV_AWS_2"
        supported_resources = ("AWS::ElasticLoadBalancingV2::Listener",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        """
            validates ALB protocol is HTTPS
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-listener.html
        :param conf: aws_alb_listener configuration
        :return: <CheckResult>
        """
        properties = conf.get("Properties")
        if properties and isinstance(properties, dict):
            protocol = properties.get("Protocol")
            if protocol:
                if protocol in ("HTTPS", "TLS", "TCP", "UDP", "TCP_UDP"):
                    return CheckResult.PASSED
                else:
                    if isinstance(properties.get("DefaultActions", {}), dict):
                        default_actions = properties.get("DefaultActions", {}).keys()
                        if any(
                            action in ConditionFunctions.__dict__.values()
                            or action in IntrinsicFunctions.__dict__.values()
                            for action in default_actions
                        ):
                            return CheckResult.UNKNOWN
                    if (
                        "DefaultActions" in properties.keys()
                        and properties["DefaultActions"][0].get("Type") == "redirect"
                        and properties["DefaultActions"][0].get("RedirectConfig", {}).get("Protocol") == "HTTPS"
                    ):
                        return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["Properties/Protocol", "Properties/DefaultActions"]


check = ALBListenerHTTPS()
