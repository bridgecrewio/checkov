"""
Module to resolve connections in terraform plan when values are unresolved.
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple

from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.plan_parser import TF_PLAN_RESOURCE_ADDRESS


class PlanConnectionResolver:
    """Resolves connections in terraform plan based on module structure and resource types."""
    
    def __init__(self, plan_file_path: str):
        """Initialize with the plan file path to access raw plan data."""
        self.plan_file_path = plan_file_path
        self.raw_plan = self._load_raw_plan()
        self.resource_changes = self._index_resource_changes()
        
    def _load_raw_plan(self) -> Dict[str, Any]:
        """Load the raw terraform plan JSON."""
        try:
            with open(self.plan_file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load plan file {self.plan_file_path}: {e}")
            return {}
    
    def _index_resource_changes(self) -> Dict[str, Dict[str, Any]]:
        """Index resource changes by address for quick lookup."""
        index = {}
        for resource in self.raw_plan.get('resource_changes', []):
            address = resource.get('address')
            if address:
                index[address] = resource
        return index
    
    def resolve_unresolved_connections(self, plan_graph: TerraformLocalGraph, 
                                      plan_vertex_map: Dict[str, Tuple[int, TerraformBlock]]) -> int:
        """
        Resolve connections for resources with unresolved references.
        Returns the number of connections created.
        """
        connections_created = 0
        
        # Check each resource for unresolved references
        for address, (vertex_idx, vertex) in plan_vertex_map.items():
            resource_data = self.resource_changes.get(address)
            if not resource_data:
                continue
            
            # Check if this resource has unresolved connection attributes
            change = resource_data.get('change', {})
            after_unknown = change.get('after_unknown', {})
            
            # Common connection attributes
            connection_attrs = [
                'target_resource_id',
                'source_resource_id', 
                'destination_resource_id',
                'resource_id',
                'subnet_id',
                'network_security_group_id',
            ]
            
            for attr in connection_attrs:
                if after_unknown.get(attr) == True:
                    # This attribute is unresolved, try to infer the connection
                    logging.info(f"Found unresolved {attr} in {address}")
                    
                    # Infer based on resource type and module structure
                    target_address = self._infer_target_address(address, resource_data, attr)
                    if target_address:
                        # Find the target vertex
                        target_data = plan_vertex_map.get(target_address)
                        if target_data:
                            target_idx = target_data[0]
                            # Create edge
                            if not self._edge_exists(plan_graph, vertex_idx, target_idx):
                                logging.info(f"Creating inferred edge: {address} -> {target_address} (via {attr})")
                                plan_graph.create_edge(vertex_idx, target_idx, attr)
                                connections_created += 1
        
        return connections_created
    
    def _infer_target_address(self, source_address: str, source_data: Dict[str, Any], 
                              attr_name: str) -> Optional[str]:
        """
        Infer the target resource address based on module structure and resource type.
        """
        source_type = source_data.get('type', '')
        
        # Special handling for Azure Monitor Diagnostic Settings
        if source_type == 'azurerm_monitor_diagnostic_setting' and attr_name == 'target_resource_id':
            # The target is usually a resource in the same or parent module
            # Extract module path from source address
            module_parts = self._extract_module_path(source_address)
            
            # Look for potential target resources
            for address, resource in self.resource_changes.items():
                if address == source_address:
                    continue
                
                resource_type = resource.get('type', '')
                # Check if this is a monitorable resource type
                if self._is_monitorable_resource(resource_type):
                    # Check if they're in related modules
                    target_module_parts = self._extract_module_path(address)
                    if self._are_modules_related(module_parts, target_module_parts):
                        logging.debug(f"Found potential target: {address} for {source_address}")
                        return address
        
        return None
    
    def _extract_module_path(self, address: str) -> List[str]:
        """Extract module path components from a resource address."""
        parts = []
        for part in address.split('.'):
            if part == 'module':
                continue
            if not part.startswith('azurerm_') and not part.startswith('aws_'):
                # This is likely a module name or resource name
                parts.append(re.sub(r'\[.*?\]', '', part))  # Remove array indices
        return parts
    
    def _are_modules_related(self, module1: List[str], module2: List[str]) -> bool:
        """Check if two module paths are related (same module or parent/child)."""
        # Check if they share common module components
        if not module1 or not module2:
            return True  # Root level resources
        
        # Check for common prefix (same parent module)
        common_prefix_len = 0
        for i in range(min(len(module1), len(module2))):
            if module1[i] == module2[i]:
                common_prefix_len += 1
            else:
                break
        
        # They're related if they share at least the first module component
        return common_prefix_len > 0
    
    def _is_monitorable_resource(self, resource_type: str) -> bool:
        """Check if a resource type can be monitored by diagnostic settings."""
        monitorable_types = [
            'azurerm_redis_cache',
            'azurerm_redis_enterprise_cluster',
            'azurerm_sql_server',
            'azurerm_sql_database',
            'azurerm_postgresql_server',
            'azurerm_mysql_server',
            'azurerm_storage_account',
            'azurerm_app_service',
            'azurerm_function_app',
            'azurerm_key_vault',
            'azurerm_eventhub_namespace',
            'azurerm_service_bus_namespace',
        ]
        return resource_type in monitorable_types
    
    def _edge_exists(self, graph: TerraformLocalGraph, source_idx: int, dest_idx: int) -> bool:
        """Check if an edge already exists between two vertices."""
        for edge in graph.out_edges.get(source_idx, []):
            if edge.dest == dest_idx:
                return True
        return False