from typing import List, Any
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck

class ComputeVMSerialConsole(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure compute instance does not have serial console enabled."
        id = "CKV_YC_4"
        categories = [CheckCategories.GENERAL_SECURITY]
        supported_resources = ["yandex_compute_instance"]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return "metadata/[0]/serial-port-enable"

    def get_forbidden_values(self) -> List[Any]:
        return [True]

check = ComputeVMSerialConsole()