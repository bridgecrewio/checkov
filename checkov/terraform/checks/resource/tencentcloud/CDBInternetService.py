from typing import Any, List

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import \
    BaseResourceNegativeValueCheck


class CDBInternetService(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure Tencent Cloud mysql instances do not enable access from public networks"
        id = "CKV_TC_9"
        supported_resources = ['tencentcloud_mysql_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'internet_service/[0]'

    def get_forbidden_values(self) -> List[Any]:
        return [1]


check = CDBInternetService()
