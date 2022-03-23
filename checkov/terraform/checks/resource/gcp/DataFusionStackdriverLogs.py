from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class DataFusionStackdriverLogs(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Datafusion has stack driver logging enabled"
        id = "CKV_GCP_104"
        supported_resources = ['google_data_fusion_instance']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "enable_stackdriver_logging"


check = DataFusionStackdriverLogs()
