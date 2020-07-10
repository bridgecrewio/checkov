from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class GKEMonitoringEnabled(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure Stackdriver Monitoring is set to Enabled on Kubernetes Engine Clusters"
        id = "CKV_GCP_8"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'monitoring_service/0'

    def get_forbidden_values(self):
        return ['none']


check = GKEMonitoringEnabled()
