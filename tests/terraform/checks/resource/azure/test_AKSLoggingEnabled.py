import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.AKSLoggingEnabled import check


class TestAKSLoggingEnabled(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['example-aks1'], 'location': ['${azurerm_resource_group.example.location}'],
                         'resource_group_name': ['${azurerm_resource_group.example.name}'], 'dns_prefix': ['exampleaks1'],
                         'default_node_pool': [{'name': ['default'], 'node_count': [1], 'vm_size': ['Standard_D2_v2']}],
                         'identity': [{'type': ['SystemAssigned']}], 'agent_pool_profile': [{}], 'service_principal': [{}],
                         'tags': [{'Environment': 'Production'}]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['example-aks1'], 'location': ['${azurerm_resource_group.example.location}'],
                         'resource_group_name': ['${azurerm_resource_group.example.name}'], 'dns_prefix': ['exampleaks1'],
                         'default_node_pool': [{'name': ['default'], 'node_count': [1], 'vm_size': ['Standard_D2_v2']}],
                         'identity': [{'type': ['SystemAssigned']}], 'agent_pool_profile': [{}], 'service_principal': [{}],
                         'tags': [{'Environment': 'Production'}],
                         'addon_profile': [{'oms_agent': [{'enabled': [True], 'log_analytics_workspace_id': ['']}]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['example-aks1'], 'location': ['${azurerm_resource_group.example.location}'],
                         'resource_group_name': ['${azurerm_resource_group.example.name}'], 'dns_prefix': ['exampleaks1'],
                         'default_node_pool': [{'name': ['default'], 'node_count': [1], 'vm_size': ['Standard_D2_v2']}],
                         'identity': [{'type': ['SystemAssigned']}], 'agent_pool_profile': [{}], 'service_principal': [{}],
                         'tags': [{'Environment': 'Production'}],
                         'addon_profile': [{'oms_agent': [{'enabled': [True], 'log_analytics_workspace_id': ['']}]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_new_syntax(self):
        resource_conf = {'name': ['example-aks1'], 'location': ['${azurerm_resource_group.example.location}'],
                         'resource_group_name': ['${azurerm_resource_group.example.name}'], 'dns_prefix': ['exampleaks1'],
                         'default_node_pool': [{'name': ['default'], 'node_count': [1], 'vm_size': ['Standard_D2_v2']}],
                         'identity': [{'type': ['SystemAssigned']}], 'agent_pool_profile': [{}], 'service_principal': [{}],
                         'tags': [{'Environment': 'Production'}],
                         'oms_agent': [{'log_analytics_workspace_id': 'mock_workspace_id'}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
