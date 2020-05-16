from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list
from checkov.common.util.type_forcers import force_int


class AbsSecurityGroupUnrestrictedIngress(BaseResourceCheck):
    def __init__(self, check_id, port):
        name = "Ensure no security groups allow ingress from 0.0.0.0:0 to port %d" % port
        supported_resources = ['aws_security_group']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)
        self.port = port

    def scan_resource_conf(self, conf):
        """
            Looks for configuration at security group ingress rules :
            https://www.terraform.io/docs/providers/aws/r/security_group.html
        :param conf: aws_security_group configuration
        :return: <CheckResult>
        """
        if 'ingress' in conf:
            ingress_conf = conf['ingress']
            for ingress_rule in ingress_conf:
                ingress_rules = force_list(ingress_rule)
                for rule in ingress_rules:
                    if isinstance(rule, dict):
                        from_port = force_int(force_list(rule['from_port'])[0])
                        to_port = force_int(force_list(rule['to_port'])[0])

                        if from_port is not None and to_port is not None and from_port <= self.port <= to_port:
                            # It's not clear whether these can ever be a type other
                            # than an empty list but just in case…
                            cidr_blocks = force_list(rule.get('cidr_blocks', [[]])[0])
                            security_groups = rule.get('security_groups', [])

                            if "0.0.0.0/0" in cidr_blocks and not security_groups:
                                return CheckResult.FAILED

        return CheckResult.PASSED
