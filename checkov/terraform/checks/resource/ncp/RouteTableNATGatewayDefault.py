from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class RouteTableNATGatewayDefault(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Routing Table associated with Web tier subnet have the default route (0.0.0.0/0) defined to " \
               "allow connectivity "
        id = "CKV_NCP_20"
        supported_resources = ('ncloud_route',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "destination_cidr_block" in conf.keys() and "target_type" in conf.keys():
            if conf.get("target_type") == ["NATGW"]:
                if conf.get("destination_cidr_block") == ["0.0.0.0/0"]:
                    return CheckResult.PASSED
                else:
                    return CheckResult.FAILED
        return CheckResult.UNKNOWN


check = RouteTableNATGatewayDefault()
