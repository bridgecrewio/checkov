from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list

PORT = 22


class SecurityGroupUnrestrictedIngress22(BaseResourceCheck):
    def __init__(self):
        name = "Ensure no security groups allow ingress from 0.0.0.0:0 to port %d" % PORT
        id = "CKV_AWS_24"
        supported_resources = ['aws_security_group']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for configuration at security group ingress rules :
            https://www.terraform.io/docs/providers/aws/r/security_group.html
        :param conf: aws_security_group configuration
        :return: <CheckResult>
        """
        if 'ingress' in conf.keys():
            ingress_conf = conf['ingress']
            for rule in ingress_conf:
                if isinstance(rule, dict):
                    if isinstance(force_list(rule['from_port'])[0],int) and isinstance(force_list(rule['to_port'])[0],int):
                        if rule['from_port'] == [PORT] and rule['to_port'] == [PORT]:
                            if 'cidr_blocks' in rule.keys():
                                if rule['cidr_blocks'] == [["0.0.0.0/0"]] and 'security_groups' not in rule.keys():
                                    return CheckResult.FAILED

        return CheckResult.PASSED


check = SecurityGroupUnrestrictedIngress22()
