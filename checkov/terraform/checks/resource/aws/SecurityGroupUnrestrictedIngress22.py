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

        if 'ingress' in conf:
            ingress_conf = conf['ingress']
            for ingress in ingress_conf:
                # It's not clear why these are double-nested list
                for rule in ingress:
                    from_port = int(force_list(rule['from_port'])[0])
                    to_port = int(force_list(rule['to_port'])[0])


                    if from_port <= PORT and to_port >= PORT:
                        # It's not clear whether these can ever be a type other
                        # than an empty list but just in case…
                        cidr_blocks = rule.get('cidr_blocks', [])
                        security_groups = rule.get('security_groups', [])
                        print(rule, cidr_blocks, security_groups)

                        if "0.0.0.0/0" in cidr_blocks and not security_groups:
                                return CheckResult.FAILED

        return CheckResult.PASSED


check = SecurityGroupUnrestrictedIngress22()
