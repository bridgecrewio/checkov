from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck

class SecurityGroupRuleDescription(BaseResourceCheck):
    def __init__(self):
        name = "Ensure every security groups rule has a description"
        id = "CKV_AWS_23"
        supported_resource = ['AWS::EC2::SecurityGroup', 'AWS::EC2::SecurityGroupIngress', 'AWS::EC2::SecurityGroupEgress']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)

    def scan_resource_conf(self, conf):
        """
            Looks for description in security group rules :
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
        :param conf: aws_security_group configuration
        :return: <CheckResult>
        """

        if conf['Type'] == 'AWS::EC2::SecurityGroup':
            if 'Properties' in conf:
                if 'SecurityGroupIngress' in conf['Properties']:
                    for rule in conf['Properties']['SecurityGroupIngress']:
                        if isinstance(rule, dict) and ('Description' not in rule or not rule['Description']):
                            return CheckResult.FAILED
                if 'SecurityGroupEgress' in conf['Properties']:
                    for rule in conf['Properties']['SecurityGroupEgress']:
                        if isinstance(rule, dict) and ('Description' not in rule.keys() or not rule['Description']):
                            return CheckResult.FAILED
                return CheckResult.PASSED

        elif conf['Type'] == 'AWS::EC2::SecurityGroupIngress' or conf['Type'] == 'AWS::EC2::SecurityGroupEgress':
            if 'Properties' in conf.keys() and 'Description' in conf['Properties'] and conf['Properties']['Description']:
                return CheckResult.PASSED

        return CheckResult.FAILED


check = SecurityGroupRuleDescription()
