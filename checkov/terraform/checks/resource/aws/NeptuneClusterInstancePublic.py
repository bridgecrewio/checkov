from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class NeptuneClusterInstancePublic(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Neptune Cluster instance is not publicly available"
        id = "CKV_AWS_102"
        supported_resources = ['aws_neptune_cluster_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'publicly_accessible' in conf.keys():
            if conf['publicly_accessible'] == [True]:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = NeptuneClusterInstancePublic()
