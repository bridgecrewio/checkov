from typing import Any, List

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import \
    BaseResourceNegativeValueCheck


class CDBIntranetPort(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure Tencent Cloud MySQL instances intranet ports are not set to the default 3306"
        id = "CKV_TC_10"
        supported_resources = ['tencentcloud_mysql_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'intranet_port/[0]'

    def get_forbidden_values(self) -> List[Any]:
        return [3306]


check = CDBIntranetPort()
