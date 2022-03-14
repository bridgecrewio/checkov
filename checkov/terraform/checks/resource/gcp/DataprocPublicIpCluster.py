from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class DataprocPublicIpCluster(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Dataproc Clusters do not have public IPs"
        id = "CKV_GCP_103"
        supported_resources = ['google_dataproc_cluster']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'cluster_config/[0]/gce_cluster_config/[0]/internal_ip_only'

check = DataprocPublicIpCluster()
