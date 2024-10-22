from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list
from checkov.cloudformation.parser.cfn_keywords import ConditionFunctions, IntrinsicFunctions

supported_policy_prefixes = {
    # ALBs support TLS v1.2 and 1.3
    'HTTPS': ("ELBSecurityPolicy-FS-1-2", "ELBSecurityPolicy-TLS-1-2", "ELBSecurityPolicy-TLS13-1-2",
              "ELBSecurityPolicy-TLS13-1-3"),
    # NLBs support TLS v1.2 and 1.3
    'TLS': ("ELBSecurityPolicy-TLS13-1-3-2021-06", "ELBSecurityPolicy-TLS13-1-2", "ELBSecurityPolicy-FS-1-2",
            "ELBSecurityPolicy-TLS-1-2")
}


class ALBListenerTLS12(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Load Balancer Listener is using at least TLS v1.2"
        id = "CKV_AWS_103"
        supported_resources = ('AWS::ElasticLoadBalancingV2::Listener',)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        """
            validates that ElasticLoadBalancing V2 Listener is using at least TLS v1.2
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-listener.html
        :param conf: aws_alb_listener configuration
        :return: <CheckResult>
        """

        if 'Properties' in conf.keys():
            if 'Protocol' in conf['Properties'].keys():
                # Check SslPolicy only if protocol is HTTPS (ALB) or TLS (NLB).
                # Other protocols are not interesting within the context of this check.
                protocol = conf['Properties']['Protocol']
                if protocol in ('HTTPS', 'TLS'):
                    if 'SslPolicy' in conf['Properties'].keys():
                        if isinstance(conf['Properties']['SslPolicy'], str) and conf['Properties']['SslPolicy'].startswith(supported_policy_prefixes[protocol]):
                            return CheckResult.PASSED
                    return CheckResult.FAILED
                elif conf['Properties']['Protocol'] in ('TCP', 'UDP', 'TCP_UDP'):
                    return CheckResult.PASSED
                actions = conf['Properties'].get('DefaultActions', [])
                for action in actions:
                    if action in ConditionFunctions.__dict__.values() or action in IntrinsicFunctions.__dict__.values():
                        return CheckResult.UNKNOWN
                    redirects = action.get("RedirectConfig", [])
                    for redirect in force_list(redirects):
                        if redirect.get("Protocol", []) == 'HTTPS':
                            return CheckResult.PASSED
        return CheckResult.FAILED


check = ALBListenerTLS12()
