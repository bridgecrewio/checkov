from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AccessControlGroupRuleDescription(BaseResourceCheck):
    def __init__(self):
        name = "Ensure every access control groups rule has a description"
        id = "CKV_NCP_2"
        supported_resource = [
            'ncloud_access_control_group',
            'ncloud_access_control_group_rule',
        ]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)

    def scan_resource_conf(self, conf):
        """
        https://registry.terraform.io/providers/NaverCloudPlatform/ncloud/latest/docs/resources/access_control_group
        :return: <CheckResult>
        """
        group_result = self.check_rule(rule_type='group_or_rule_description', conf=conf)
        if 'type' not in conf.keys():
            outbound_result = self.check_rule(rule_type='outbound', conf=conf)
            inbound_result = self.check_rule(rule_type='inbound', conf=conf)
            if group_result == CheckResult.PASSED or (outbound_result == CheckResult.PASSED and inbound_result == CheckResult.PASSED):
                return CheckResult.PASSED
            return CheckResult.FAILED

        return group_result

    def check_rule(self, rule_type, conf):

        if rule_type == 'group_or_rule_description':
            self.evaluated_keys = ['description']
            if conf.get('description'):
                return CheckResult.PASSED
            return CheckResult.FAILED

        if rule_type in conf.keys():
            for rule in conf[rule_type]:
                if isinstance(rule, dict) and rule.get('description'):
                    self.evaluated_keys.append(f'{rule_type}/[{conf[rule_type].index(rule)}]')
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = AccessControlGroupRuleDescription()
