from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import List


class DataprocPrivateCluster(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Dataproc clusters are not anonymously or publicly accessible"
        id = "CKV_GCP_96"
        supported_resources = ['google_dataproc_cluster_iam_member', 'google_dataproc_cluster_iam_binding']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        members = conf.get('members', [[]])[0]
        members = members if isinstance(members, list) else []
        member_conf = conf.get('member', []) + members
        if not any(member in member_conf for member in ['allUsers', 'allAuthenticatedUsers']):
            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['members', 'member']


check = DataprocPrivateCluster()
