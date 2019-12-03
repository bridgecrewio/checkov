from checkov.terraformscanner.models.enums import ScanResult, ScanCategories
from checkov.terraformscanner.resource_scanner import ResourceScanner


class SecurityGroupRuleDescription(ResourceScanner):
    def __init__(self):
        name = "Ensure every security groups rule has a description"
        scan_id = "BC_AWS_NETWORKING_28"
        supported_resource = ['aws_security_group', 'aws_security_group_rule', 'aws_db_security_group',
                              'aws_elasticache_security_group', 'aws_redshift_security_group']
        categories = [ScanCategories.NETWORKING]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resource)

    def scan_resource_conf(self, conf):
        """
            Looks for description at security group  rules :
            https://www.terraform.io/docs/providers/aws/r/security_group.html
        :param conf: aws_security_group configuration
        :return: <ScanResult>
        """
        if 'description' in conf.keys():
            if conf['description']:
                return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = SecurityGroupRuleDescription()
