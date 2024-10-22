import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.AKSRbacEnabled import check


class TestAKSRbacEnabled(unittest.TestCase):
    # azurerm < 2.99.0
    def test_failure_false(self):
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

    # azurerm >= 2.99.0
    def test_failure_false_new_syntax(self):
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
            "role_based_access_control_enabled": [False],
            "tags": [{"Environment": "Production"}],
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_default(self):
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
            "tags": [{"Environment": "Production"}],
            "addon_profile": [
                {"oms_agent": [{"enabled": [True], "log_analytics_workspace_id": [""]}]}
            ],
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    # azurerm < 2.99.0
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
            "role_based_access_control": [{"enabled": [True]}],
            "tags": [{"Environment": "Production"}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    # azurerm >= 2.99.0
    def test_success_new_syntax(self):
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
            "role_based_access_control_enabled": [True],
            "tags": [{"Environment": "Production"}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
