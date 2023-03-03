from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SecurityGroupRuleDescription(BaseResourceCheck):
    def __init__(self):
        name = "Ensure every security groups rule has a description"
        id = "CKV_AWS_23"
        supported_resource = [
            'aws_security_group',
            'aws_security_group_rule',
            'aws_db_security_group',
            'aws_elasticache_security_group',
            'aws_redshift_security_group',
            'aws_vpc_security_group_egress_rule',
            'aws_vpc_security_group_ingress_rule'
        ]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)

    def scan_resource_conf(self, conf):
        """
            Looks for description at security group  rules :
            https://www.terraform.io/docs/providers/aws/r/security_group.html
        :param conf: aws_security_group configuration
        :return: <CheckResult>
        """
        group_result = self.check_rule(rule_type='group_or_rule_description', conf=conf)
        if 'type' not in conf.keys():
            # 'type' attribute only exists and is required for aws_security_group_rule resources.
            # Therefore, only if 'type' is not present, ingress and egress blocks must be checked in the resource.
            egress_result = self.check_rule(rule_type='egress', conf=conf)
            ingress_result = self.check_rule(rule_type='ingress', conf=conf)
            if group_result == CheckResult.PASSED and egress_result == CheckResult.PASSED and ingress_result == CheckResult.PASSED:
                return CheckResult.PASSED
            return CheckResult.FAILED

        return group_result

    def check_rule(self, rule_type, conf):
        if rule_type == 'group_or_rule_description':
            if 'description' in conf.keys():
                self.evaluated_keys = ['description']
                if conf['description']:
                    return CheckResult.PASSED
            return CheckResult.FAILED

        if rule_type in conf.keys():
            for rule in conf[rule_type]:
                if isinstance(rule, dict) and ('description' not in rule.keys() or not rule['description']):
                    self.evaluated_keys.append(f'{rule_type}/[{conf[rule_type].index(rule)}]')
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = SecurityGroupRuleDescription()
