from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class RedshiftClusterWithCommonUsernameAndPublicAccess(BaseResourceCheck):

    def __init__(self):
        name = "Avoid AWS Redshift cluster with commonly used master username and public access setting enabled"
        id = "CKV_AWS_391"
        supported_resources = ['aws_redshift_cluster']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'master_username' in conf:
            if conf['master_username'][0] in ['awsuser', 'administrator', 'admin']:
                self.evaluated_keys = ['master_username']
                if 'publicly_accessible' in conf:
                    if str(conf['publicly_accessible'][0]).lower() == 'true':
                        return CheckResult.FAILED
                else:
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = RedshiftClusterWithCommonUsernameAndPublicAccess()
