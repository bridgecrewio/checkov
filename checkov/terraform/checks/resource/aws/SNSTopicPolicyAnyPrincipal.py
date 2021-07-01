from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list

from policyuniverse.policy import Policy

import json


class SNSTopicPolicyAnyPrincipal(BaseResourceCheck):

    def __init__(self):
        name = "Ensure SNS topic policy is not public by only allowing specific services or principals to access it"
        id = "CKV_AWS_169"
        supported_resources = ['aws_sns_topic_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        conf_policy = conf.get("policy")
        if conf_policy:
            if isinstance(conf_policy[0], dict):
                policy = Policy(conf['policy'][0])
                if policy.is_internet_accessible():
                     return CheckResult.FAILED
            else:
                return CheckResult.UNKNOWN
        return CheckResult.PASSED

check = SNSTopicPolicyAnyPrincipal()


