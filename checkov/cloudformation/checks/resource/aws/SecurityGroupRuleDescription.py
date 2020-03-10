from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck

class SecurityGroupRuleDescription(BaseResourceCheck):
    def __init__(self):
        name = "Ensure every security groups rule has a description"
        id = "CKV_AWS_23"
        supported_resource = ['AWS::EC2::SecurityGroup', 'AWS::EC2::SecurityGroupIngress', 'AWS::EC2::SecurityGroupEgress', 'AWS::RDS::DBSecurityGroup',
                              'AWS::ElastiCache::SecurityGroup', 'AWS::Redshift::ClusterSecurityGroup']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)

    def scan_resource_conf(self, conf):
        """
            Looks for group description and description in security group rules :
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
        :param conf: aws_security_group configuration
        :return: <CheckResult>
        """

        if conf['Type'] == 'AWS::EC2::SecurityGroup':
            if 'Properties' in conf.keys():
                if 'GroupDescription' in conf['Properties'].keys():
                    if 'SecurityGroupIngress' in conf['Properties'].keys():
                        for rule in conf['Properties']['SecurityGroupIngress']:
                            if 'Description' not in rule.keys():
                                return CheckResult.FAILED
                    if 'SecurityGroupEgress' in conf['Properties'].keys():
                        for rule in conf['Properties']['SecurityGroupEgress']:
                            if 'Description' not in rule.keys():
                                return CheckResult.FAILED
                    return CheckResult.PASSED
                else:
                    return CheckResult.FAILED
        elif conf['Type'] == 'AWS::EC2::SecurityGroupIngress' or conf['Type'] == 'AWS::EC2::SecurityGroupEgress':
            if 'Properties' in conf.keys() and 'Description' in conf['Properties'].keys():
                return CheckResult.PASSED
        elif conf['Type'] == 'AWS::RDS::DBSecurityGroup':
            if 'Properties' in conf.keys() and 'GroupDescription' in conf['Properties'].keys():
                return CheckResult.PASSED
        elif conf['Type'] == 'AWS::ElastiCache::SecurityGroup' or conf['Type'] == 'AWS::Redshift::ClusterSecurityGroup':
            if 'Properties' in conf.keys() and 'Description' in conf['Properties'].keys():
                return CheckResult.PASSED

        return CheckResult.FAILED


check = SecurityGroupRuleDescription()
