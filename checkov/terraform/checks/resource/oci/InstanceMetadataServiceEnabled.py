from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class InstanceMetadataServiceEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure OCI Compute Instance has Legacy MetaData service endpoint disabled"
        id = "CKV_OCI_5"
        supported_resources = ("oci_core_instance",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "instance_options/[0]/are_legacy_imds_endpoints_disabled"

    def get_expected_value(self) -> Any:
        return True


check = InstanceMetadataServiceEnabled()
