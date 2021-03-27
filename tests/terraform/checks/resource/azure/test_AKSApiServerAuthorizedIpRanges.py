import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.AKSApiServerAuthorizedIpRanges import check


class TestAKSApiServerAuthorizedIpRanges(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "name": ["example-aks1"],
            "location": ["${azurerm_resource_group.example.location}"],
            "resource_group_name": ["${azurerm_resource_group.example.name}"],
            "dns_prefix": ["exampleaks1"],
            "default_node_pool": [
                {"name": ["default"], "node_count": [1], "vm_size": ["Standard_D2_v2"]}
            ],
            "identity": [{"type": ["SystemAssigned"]}],
            "agent_pool_profile": [{}],
            "service_principal": [{}],
            "role_based_access_control": [{"enabled": [False]}],
            "tags": [{"Environment": "Production"}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": ["example-aks1"],
            "location": ["${azurerm_resource_group.example.location}"],
            "resource_group_name": ["${azurerm_resource_group.example.name}"],
            "dns_prefix": ["exampleaks1"],
            "default_node_pool": [
                {"name": ["default"], "node_count": [1], "vm_size": ["Standard_D2_v2"]}
            ],
            "identity": [{"type": ["SystemAssigned"]}],
            "agent_pool_profile": [{}],
            "service_principal": [{}],
            "api_server_authorized_ip_ranges": [["192.168.0.0/16"]],
            "tags": [{"Environment": "Production"}],
            "addon_profile": [
                {"oms_agent": [{"enabled": [True], "log_analytics_workspace_id": [""]}]}
            ],
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success2(self):
        resource_conf = {
            "name": ["example-aks1"],
            "location": ["${azurerm_resource_group.example.location}"],
            "resource_group_name": ["${azurerm_resource_group.example.name}"],
            "dns_prefix": ["exampleaks1"],
            "default_node_pool": [
                {"name": ["default"], "node_count": [1], "vm_size": ["Standard_D2_v2"]}
            ],
            "identity": [{"type": ["SystemAssigned"]}],
            "agent_pool_profile": [{}],
            "service_principal": [{}],
            "api_server_authorized_ip_ranges": [[]],
            "role_based_access_control": [{"enabled": [True]}],
            "tags": [{"Environment": "Production"}],
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
