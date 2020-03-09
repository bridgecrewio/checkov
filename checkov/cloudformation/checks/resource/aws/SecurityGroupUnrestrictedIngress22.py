from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck

PORT = 22

class SecurityGroupUnrestrictedIngress22(BaseResourceCheck):
    def __init__(self):
        name = "Ensure no security groups allow ingress from 0.0.0.0:0 to port %d" % PORT
        id = "CKV_AWS_24"
        supported_resources = ['AWS::EC2::SecurityGroup', 'AWS::EC2::SecurityGroupIngress']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for configuration at security group ingress rules :
            https://www.terraform.io/docs/providers/aws/r/security_group.html
        :param conf: aws_security_group configuration
        :return: <CheckResult>
        """
        rules = []
        if conf['Type'] == 'AWS::EC2::SecurityGroup':
            if 'Properties' in conf.keys():
                if 'SecurityGroupIngress' in conf['Properties'].keys():
                    rules = conf['Properties']['SecurityGroupIngress']
        elif conf['Type'] == 'AWS::EC2::SecurityGroupIngress':
            if 'Properties' in conf.keys():
                rules = []
                rules.append(conf['Properties'])

        for rule in rules:
            if int(rule['FromPort']) == int(PORT) and int(rule['ToPort']) == int(PORT):
                if 'CidrIp' in rule.keys() and rule['CidrIp'] == '0.0.0.0/0':
                    return CheckResult.FAILED
                elif 'CidrIpv6' in rule.keys() and rule['CidrIpv6'] == '::/0':
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = SecurityGroupUnrestrictedIngress22()
