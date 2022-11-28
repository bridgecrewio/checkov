from __future__ import annotations

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class LBListenerUsingHTTPS(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure Load Balancer Listener Using HTTPS"
        id = "CKV_NCP_24"
        supported_resources = ("ncloud_lb_listener",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'protocol'

    def get_expected_value(self):
        return 'HTTPS'


check = LBListenerUsingHTTPS()
