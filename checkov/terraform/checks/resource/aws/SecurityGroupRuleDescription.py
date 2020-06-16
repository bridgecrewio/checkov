from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SecurityGroupRuleDescription(BaseResourceCheck):
    def __init__(self):
        name = "Ensure every security groups rule has a description"
        id = "CKV_AWS_23"
        supported_resource = ['aws_security_group', 'aws_security_group_rule', 'aws_db_security_group',
                              'aws_elasticache_security_group', 'aws_redshift_security_group']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)

    def scan_resource_conf(self, conf):
        """
            Looks for description at security group  rules :
            https://www.terraform.io/docs/providers/aws/r/security_group.html
        :param conf: aws_security_group configuration
        :return: <CheckResult>
        """
        rule_confs = [conf]
        if 'egress' in conf or 'ingress' in conf:
            rule_confs = conf.get('egress', []) + conf.get('ingress', [])

        for rule_conf in rule_confs:
            if 'description' not in rule_conf:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = SecurityGroupRuleDescription()
