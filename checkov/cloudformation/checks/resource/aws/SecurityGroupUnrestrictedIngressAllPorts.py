from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck

class SecurityGroupUnrestrictedIngressAllPorts(BaseResourceCheck):
    def __init__(self):
        name = "Ensure no security groups allow ingress from 0.0.0.0:0 to all ports"
        id = "CKV_AWS_365"
        supported_resources = ['AWS::EC2::SecurityGroup', 'AWS::EC2::SecurityGroupIngress']
        # CheckCategories are defined in models/enums.py
        categories = [CheckCategories.NETWORKING]
        guideline = "Cheks IpProtocol and port range combination to make sure inbound traffic on all ports is not allowed from anywhere"
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, guideline=guideline)

    def scan_resource_conf(self, conf):
        """
        IpProtocol + FromPort + ToPort configuration:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-securitygroupingress.html#cfn-ec2-securitygroupingress-ipprotocol
        TCP, UDP, ICMP must have port range specified, while IPv6-ICMP can have it optionally.
        All other protocols disregard port ranges, allowing traffic on all ports.
        Protocols can be referenced by numbers too.
        :param conf: aws_security_group configuration
        :return: <CheckResult>
        """
        protocols_with_restricted_ports = (6, 17, 1, 58, 'tcp', 'udp', 'icmp', 'icmpv6')
        rules = []
        if conf['Type'] == 'AWS::EC2::SecurityGroup':
            if 'Properties' in conf.keys():
                if 'SecurityGroupIngress' in conf['Properties'].keys():
                    rules = conf['Properties']['SecurityGroupIngress']
        elif conf['Type'] == 'AWS::EC2::SecurityGroupIngress':
            if 'Properties' in conf.keys():
                rules = []
                rules.append(conf['Properties'])

        if not isinstance(rules, list):
            return CheckResult.UNKNOWN

        for rule in rules:
            if rule.__contains__('IpProtocol'):
                if rule['IpProtocol'] not in protocols_with_restricted_ports \
                or (rule['IpProtocol'] in protocols_with_restricted_ports \
                and not (rule.__contains__('FromPort') and rule.__contains__('ToPort'))):
                    if 'CidrIp' in rule.keys() and rule['CidrIp'] == '0.0.0.0/0':
                        return CheckResult.FAILED
                    elif 'CidrIpv6' in rule.keys() and rule['CidrIpv6'] in ['::/0', '0000:0000:0000:0000:0000:0000:0000:0000/0']:
                        return CheckResult.FAILED
        return CheckResult.PASSED

check = SecurityGroupUnrestrictedIngressAllPorts()
