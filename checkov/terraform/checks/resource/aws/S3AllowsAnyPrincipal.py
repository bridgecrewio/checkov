from json import JSONDecodeError
import re

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list
import json
from typing import List


def check_conditions(statement) -> bool:
    # Check if 'Condition' key exists
    if 'Condition' not in statement:
        return False

    condition = statement['Condition']

    # Pass if they define bad ARNs. Assumes they are not too narrow
    if any(key in condition for key in ['ArnNotEquals', 'ArnNotLike']):
        return True

    # Handling 'ArnEquals' and 'ArnLike'
    for arn_key in ['ArnEquals', 'ArnLike']:
        if arn_key in condition:
            # Pass unless it is for all IAM ARNs
            for principal_key in ['aws:PrincipalArn', 'aws:SourceArn']:
                if principal_key in condition[arn_key]:
                    principal_arn = condition[arn_key][principal_key]
                    # Fail if the  Condition is for all ARNs of any resource
                    if re.match(r'^arn:aws:[a-z0-9-]+::\*.*$', principal_arn):
                        return False
            # Passed if 'aws:PrincipalArn' or 'aws:SourceArn' do not match because then they are specific
            return True

    # Handle VPC sources. Other sources not specific enough
    # Leaves out the NOT conditions as too broad ('StringNotEquals', 'StringNotEqualsIgnoreCase', 'StringNotLike')
    string_conditions = ['StringEquals', 'StringEqualsIgnoreCase', 'StringLike']
    if any(condition_type in condition for condition_type in string_conditions):
        for condition_type in string_conditions:
            if condition_type in condition:
                if any(source in condition[condition_type] for source in ['aws:sourceVpce', 'aws:SourceVpc']):
                    return True

    # Default fail if none of the above conditions are met
    return False


class S3AllowsAnyPrincipal(BaseResourceCheck):

    def __init__(self) -> None:
        name = "Ensure S3 bucket does not allow an action with any Principal"
        id = "CKV_AWS_70"
        supported_resources = ['aws_s3_bucket', 'aws_s3_bucket_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'policy' not in conf.keys():
            return CheckResult.UNKNOWN
        if not isinstance(conf['policy'][0], str):
            policy_block = conf['policy'][0]
        else:
            if "data.aws_iam_policy_document" in conf['policy'][0]:
                return CheckResult.UNKNOWN
            else:
                try:
                    policy_block = json.loads(conf['policy'][0])
                except JSONDecodeError:  # nosec
                    return CheckResult.UNKNOWN

        if isinstance(policy_block, dict) and 'Statement' in policy_block.keys():
            for statement in force_list(policy_block['Statement']):
                if statement['Effect'] == 'Deny' or 'Principal' not in statement:
                    continue
                principal = statement['Principal']
                if principal == '*':
                    if check_conditions(statement):
                        return CheckResult.PASSED
                    return CheckResult.FAILED
                if 'AWS' in statement['Principal']:
                    # Can be a string or an array of strings
                    aws = statement['Principal']['AWS']
                    if (isinstance(aws, str) and aws == '*') or (isinstance(aws, list) and '*' in aws):
                        if check_conditions(statement):
                            return CheckResult.PASSED
                        return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['policy']


check = S3AllowsAnyPrincipal()
