from checkov.terraformscanner.models.enums import ScanResult, ScanCategories
from checkov.terraformscanner.resource_scanner import ResourceScanner

PORT = 22


class SecurityGroupUnrestrictedIngress22(ResourceScanner):
    def __init__(self):
        name = "Ensure no security groups allow ingress from 0.0.0.0:0 to port %d" % PORT
        scan_id = "BC_AWS_NETWORKING_1"
        supported_resources = ['aws_security_group']
        categories = [ScanCategories.NETWORKING]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for configuration at security group ingress rules :
            https://www.terraform.io/docs/providers/aws/r/security_group.html
        :param conf: aws_security_group configuration
        :return: <ScanResult>
        """
        if 'ingress' in conf.keys():
            ingress_conf = conf['ingress']
            for rule in ingress_conf:
                if rule['from_port'] == [PORT] and rule['to_port'] == [PORT] and rule['cidr_blocks'] == [[
                    "0.0.0.0/0"]] and 'self' not in rule.keys() and 'security_groups' not in rule.keys():
                    return ScanResult.FAILURE

        return ScanResult.SUCCESS


scanner = SecurityGroupUnrestrictedIngress22()
