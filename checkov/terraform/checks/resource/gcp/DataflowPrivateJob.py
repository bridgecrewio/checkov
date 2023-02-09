from typing import Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class DataflowPrivateJob(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Dataflow jobs are private"
        id = "CKV_GCP_94"
        supported_resources = ("google_dataflow_job",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "ip_configuration"

    # Possible values are "WORKER_IP_PUBLIC" or "WORKER_IP_PRIVATE"
    def get_expected_value(self) -> Any:
        return "WORKER_IP_PRIVATE"


check = DataflowPrivateJob()
