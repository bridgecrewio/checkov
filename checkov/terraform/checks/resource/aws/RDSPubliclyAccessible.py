from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class RDSPubliclyAccessible(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the RDS bucket is not public accessible"
        id = "CKV_AWS_17"
        supported_resources = ['aws_db_instance','aws_rds_cluster_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for publicly_accessible configuration at aws_db_instance:
            https://www.terraform.io/docs/providers/aws/d/db_instance.html
        :param conf: publicly_accessible configuration
        :return: <CheckResult>
        """
        if 'publicly_accessible' in conf.keys():
            key = conf['publicly_accessible'][0]
            if key:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = RDSPubliclyAccessible()
