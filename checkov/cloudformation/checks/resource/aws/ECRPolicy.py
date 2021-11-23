import json
from typing import List

from checkov.common.parsers.node import StrNode
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class ECRPolicy(BaseResourceCheck):
    def __init__(self):
        name = "Ensure ECR policy is not set to public"
        id = "CKV_AWS_32"
        supported_resources = ['AWS::ECR::Repository']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for public * policy for ecr repository:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecr-repository.html
        :param conf: aws_ecr_repository configuration
        :return: <CheckResult>
        """
        self.evaluated_keys = ["Properties/RepositoryPolicyText/Statement"]
        if 'Properties' in conf.keys():
            if 'RepositoryPolicyText' in conf['Properties'].keys():
                policy_text = conf['Properties']['RepositoryPolicyText']
                if type(policy_text) in (str, StrNode):
                    policy_text = json.loads(str(policy_text))
                if 'Statement' in policy_text.keys():
                    for statement_index, statement in enumerate(policy_text['Statement']):
                        if 'Principal' in statement.keys():
                            for principal_index, principal in enumerate(statement['Principal']):
                                if principal == "*":
                                    self.evaluated_keys = [f"Properties/RepositoryPolicyText/Statement/[{statement_index}]/Principal/[{principal_index}]"]
                                    return CheckResult.FAILED
        return CheckResult.PASSED

check = ECRPolicy()
