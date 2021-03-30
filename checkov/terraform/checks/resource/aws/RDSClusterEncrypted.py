from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class RDSClusterEncrypted(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that RDS global clusters are encrypted"
        id = "CKV_AWS_140"
        supported_resources = ['aws_rds_global_cluster']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for storage_encrypted at aws_rds_global_cluster:
            https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/rds_global_cluster
        :param conf: aws_rds_global_cluster configuration
        :return: <CheckResult>
        """
        self.evaluated_keys = 'aws_rds_global_cluster'
        if "source_db_cluster_identifier" in conf.keys():
            return CheckResult.UNKNOWN
        if "storage_encrypted" in conf.keys():
            if conf["storage_encrypted"][0]:
                return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.FAILED


check = RDSClusterEncrypted()
