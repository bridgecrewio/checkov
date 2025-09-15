"""
Tests for the PlanConnectionResolver that resolves unresolved connections in terraform plans.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from checkov.terraform.plan_connection_resolver import PlanConnectionResolver
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_builder.graph_components.block_types import BlockType


class TestPlanConnectionResolver(unittest.TestCase):
    """Test cases for PlanConnectionResolver."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_plan = {
            "terraform_version": "1.5.0",
            "resource_changes": [
                {
                    "address": "module.cache_redis.azurerm_redis_cache.redis_cache[\"southeastasia\"]",
                    "type": "azurerm_redis_cache",
                    "change": {
                        "after": {
                            "name": "redis-cache-sea",
                            "location": "southeastasia"
                        },
                        "after_unknown": {}
                    }
                },
                {
                    "address": "module.cache_redis.module.monitor_diagnostic[\"redis01\"].azurerm_monitor_diagnostic_setting.monitor_diagnostic_settings[\"default|southeastasia\"]",
                    "type": "azurerm_monitor_diagnostic_setting",
                    "change": {
                        "after": {
                            "name": "diagnostic-setting",
                            "target_resource_id": None
                        },
                        "after_unknown": {
                            "target_resource_id": True,
                            "id": True
                        }
                    }
                }
            ]
        }
    
    def test_load_raw_plan(self):
        """Test loading raw plan from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_plan, f)
            temp_file = f.name
        
        try:
            resolver = PlanConnectionResolver(temp_file)
            self.assertIsNotNone(resolver.raw_plan)
            self.assertEqual(resolver.raw_plan['terraform_version'], '1.5.0')
            self.assertEqual(len(resolver.resource_changes), 2)
        finally:
            os.unlink(temp_file)
    
    def test_resolve_unresolved_connections(self):
        """Test resolving unresolved connections between resources."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_plan, f)
            temp_file = f.name
        
        try:
            resolver = PlanConnectionResolver(temp_file)
            
            # Create a mock plan graph
            from checkov.terraform.modules.module_objects import TFModule
            module = TFModule(path="", name="test")
            plan_graph = TerraformLocalGraph(module)
            
            # Create vertices for the resources
            redis_vertex = TerraformBlock(
                name="azurerm_redis_cache.redis_cache",
                config={},
                path="",
                block_type=BlockType.RESOURCE,
                attributes={
                    "resource_type": "azurerm_redis_cache",
                    "__address__": "module.cache_redis.azurerm_redis_cache.redis_cache[\"southeastasia\"]"
                }
            )
            
            diag_vertex = TerraformBlock(
                name="azurerm_monitor_diagnostic_setting.monitor_diagnostic_settings",
                config={},
                path="",
                block_type=BlockType.RESOURCE,
                attributes={
                    "resource_type": "azurerm_monitor_diagnostic_setting",
                    "__address__": "module.cache_redis.module.monitor_diagnostic[\"redis01\"].azurerm_monitor_diagnostic_setting.monitor_diagnostic_settings[\"default|southeastasia\"]"
                }
            )
            
            plan_graph.vertices = [redis_vertex, diag_vertex]
            plan_graph.out_edges = {0: [], 1: []}
            plan_graph.in_edges = {0: [], 1: []}
            
            # Create vertex map
            vertex_map = {
                "module.cache_redis.azurerm_redis_cache.redis_cache[\"southeastasia\"]": (0, redis_vertex),
                "module.cache_redis.module.monitor_diagnostic[\"redis01\"].azurerm_monitor_diagnostic_setting.monitor_diagnostic_settings[\"default|southeastasia\"]": (1, diag_vertex)
            }
            
            # Resolve connections
            connections_created = resolver.resolve_unresolved_connections(plan_graph, vertex_map)
            
            # Verify that a connection was created
            self.assertEqual(connections_created, 1)
            
            # Check that an edge was created from diagnostic setting to redis cache
            self.assertEqual(len(plan_graph.out_edges[1]), 1)
            self.assertEqual(plan_graph.out_edges[1][0].dest, 0)
            self.assertEqual(plan_graph.out_edges[1][0].label, 'target_resource_id')
            
        finally:
            os.unlink(temp_file)
    
    def test_is_monitorable_resource(self):
        """Test checking if a resource type is monitorable."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_plan, f)
            temp_file = f.name
        
        try:
            resolver = PlanConnectionResolver(temp_file)
            
            # Test monitorable resources
            self.assertTrue(resolver._is_monitorable_resource('azurerm_redis_cache'))
            self.assertTrue(resolver._is_monitorable_resource('azurerm_sql_server'))
            self.assertTrue(resolver._is_monitorable_resource('azurerm_storage_account'))
            
            # Test non-monitorable resources
            self.assertFalse(resolver._is_monitorable_resource('azurerm_resource_group'))
            self.assertFalse(resolver._is_monitorable_resource('azurerm_virtual_network'))
            
        finally:
            os.unlink(temp_file)
    
    def test_extract_module_path(self):
        """Test extracting module path from resource address."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_plan, f)
            temp_file = f.name
        
        try:
            resolver = PlanConnectionResolver(temp_file)
            
            # Test various address formats
            path1 = resolver._extract_module_path("module.cache_redis.azurerm_redis_cache.redis_cache[\"key\"]")
            self.assertEqual(path1, ['cache_redis', 'redis_cache'])
            
            path2 = resolver._extract_module_path("module.parent.module.child.azurerm_resource.name")
            self.assertEqual(path2, ['parent', 'child', 'name'])
            
            path3 = resolver._extract_module_path("azurerm_resource.name")
            self.assertEqual(path3, ['name'])
            
        finally:
            os.unlink(temp_file)
    
    def test_are_modules_related(self):
        """Test checking if two module paths are related."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_plan, f)
            temp_file = f.name
        
        try:
            resolver = PlanConnectionResolver(temp_file)
            
            # Same module
            self.assertTrue(resolver._are_modules_related(['cache_redis'], ['cache_redis']))
            
            # Parent and child
            self.assertTrue(resolver._are_modules_related(['cache_redis'], ['cache_redis', 'monitor']))
            
            # Siblings with same parent
            self.assertTrue(resolver._are_modules_related(['cache_redis', 'resource1'], ['cache_redis', 'resource2']))
            
            # Unrelated modules
            self.assertFalse(resolver._are_modules_related(['module1'], ['module2']))
            
            # Root level resources
            self.assertTrue(resolver._are_modules_related([], []))
            
        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()