import json

from checkov.cloudformation.parser.node import str_node
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
        if 'Properties' in conf.keys():
            if 'RepositoryPolicyText' in conf['Properties'].keys():
                policy_text = conf['Properties']['RepositoryPolicyText']
                if type(policy_text) in (str, str_node):
                    policy_text = json.loads(str(policy_text))
                if 'Statement' in policy_text.keys():
                    for statement in policy_text['Statement']:
                        if 'Principal' in statement.keys():
                            for principal in statement['Principal']:
                                if principal == "*":
                                    return CheckResult.FAILED
        return CheckResult.PASSED


check = ECRPolicy()
