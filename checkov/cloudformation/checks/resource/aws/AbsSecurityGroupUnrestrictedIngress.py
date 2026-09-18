from typing import Optional

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class AbsSecurityGroupUnrestrictedIngress(BaseResourceCheck):
    def __init__(self, check_id, port) -> None:
        name = "Ensure no security groups allow ingress from 0.0.0.0:0 to port %d" % port
        supported_resources = ['AWS::EC2::SecurityGroup', 'AWS::EC2::SecurityGroupIngress']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)
        self.port = port

    def scan_resource_conf(self, conf) -> CheckResult:
        """
        Looks for configuration at security group ingress rules:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html
        :param conf: aws_security_group configuration
        :return: <CheckResult>
        """
        rules = []
        if conf['Type'] == 'AWS::EC2::SecurityGroup':
            if 'Properties' in conf.keys():
                if 'SecurityGroupIngress' in conf['Properties'].keys():
                    self.evaluated_keys = ['Properties/SecurityGroupIngress']
                    rules = conf['Properties']['SecurityGroupIngress']
        elif conf['Type'] == 'AWS::EC2::SecurityGroupIngress':
            if 'Properties' in conf.keys():
                self.evaluated_keys = ['Properties']
                rules = []
                rules.append(conf['Properties'])

        if not isinstance(rules, list):
            return CheckResult.UNKNOWN

        # Track whether every rule was skipped due to unparseable ports so we can
        # fall back to UNKNOWN only when there is no evaluable rule left. A single
        # bad parameter must not mask a definitive FAILED verdict on a sibling rule.
        saw_evaluable_rule = False

        for rule in rules:
            if rule.__contains__('FromPort') and rule.__contains__('ToPort'):
                if (isinstance(rule['FromPort'], int) and isinstance(rule['ToPort'], int)) or \
                        isinstance(rule['FromPort'], str) and isinstance(rule['ToPort'], str):
                    in_range = self.range(rule)
                    if in_range is None:
                        # Unparseable port bound (e.g. empty Default on a Ref'd
                        # parameter). Skip this rule and let the next one speak;
                        # if nothing is evaluable, we will report UNKNOWN below.
                        continue
                    saw_evaluable_rule = True
                    if in_range:
                        if 'CidrIp' in rule.keys():
                            cidr = rule['CidrIp']
                            if cidr == '0.0.0.0/0':  # nosec  # nosec
                                return CheckResult.FAILED
                        elif 'CidrIpv6' in rule.keys() and \
                                rule['CidrIpv6'] in ['::/0', '0000:0000:0000:0000:0000:0000:0000:0000/0']:
                            return CheckResult.FAILED
        if not saw_evaluable_rule:
            return CheckResult.UNKNOWN
        return CheckResult.PASSED

    def range(self, rule) -> Optional[bool]:
        """Whether self.port falls inside the rule's port range.

        Returns None when either bound does not resolve to an integer, which
        happens when a Ref points at a parameter whose value is not a port
        (an empty Default, for example). The caller skips the rule in that
        case rather than letting the ValueError escape, which would leave
        the resource with no result at all.
        """
        try:
            from_port = int(rule['FromPort'])
            to_port = int(rule['ToPort'])
        except (TypeError, ValueError):
            return None
        return from_port <= int(self.port) <= to_port
