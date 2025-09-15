import logging
import re

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.common.output.report import Report
from checkov.terraform.plan_parser import TF_PLAN_RESOURCE_ADDRESS
from typing import Dict, Tuple, Optional, Any, List
from checkov.terraform.plan_connection_resolver import PlanConnectionResolver


class DeepAnalysisGraphManager:
    def __init__(self, tf_graph: TerraformLocalGraph, tf_plan_graph: TerraformLocalGraph, plan_file_path: Optional[str] = None) -> None:
        self.tf_graph: TerraformLocalGraph = tf_graph
        self.tf_plan_graph: TerraformLocalGraph = tf_plan_graph
        self.plan_file_path = plan_file_path
        self._address_to_tf_idx_and_vertex_map: Dict[str, Tuple[int, TerraformBlock]] = {}
        self._address_to_tf_plan_idx_and_vertex_map: Dict[str, Tuple[int, TerraformBlock]] = {}
        self._apply_address_mapping()
        
        # Log detailed information about the graphs
        tf_edge_count = sum(len(edges) for edges in self.tf_graph.out_edges.values())
        plan_edge_count = sum(len(edges) for edges in self.tf_plan_graph.out_edges.values())
        
        logging.info(f"DeepAnalysisGraphManager initialized:")
        logging.info(f"  TF graph: {len(self.tf_graph.vertices)} vertices, {tf_edge_count} edges")
        logging.info(f"  Plan graph: {len(self.tf_plan_graph.vertices)} vertices, {plan_edge_count} edges")
        logging.info(f"  Mapped TF resources: {len(self._address_to_tf_idx_and_vertex_map)}")
        logging.info(f"  Mapped Plan resources: {len(self._address_to_tf_plan_idx_and_vertex_map)}")
        
        # Try to resolve unresolved connections if we have the plan file path
        if self.plan_file_path:
            try:
                resolver = PlanConnectionResolver(self.plan_file_path)
                connections_created = resolver.resolve_unresolved_connections(
                    self.tf_plan_graph,
                    self._address_to_tf_plan_idx_and_vertex_map
                )
                if connections_created > 0:
                    logging.info(f"Resolved {connections_created} unresolved connections from plan file")
            except Exception as e:
                logging.debug(f"Failed to resolve connections from plan file: {e}")
        
        self._infer_unresolved_connections()

    def _apply_address_mapping(self) -> None:
        # Map TF graph vertices - they might not have TF_PLAN_RESOURCE_ADDRESS
        for i, vertex in enumerate(self.tf_graph.vertices):
            if vertex.block_type == BlockType.RESOURCE:
                # Try multiple ways to get the address
                address = vertex.attributes.get(TF_PLAN_RESOURCE_ADDRESS)
                if not address:
                    # Try to construct address from name and path
                    address = vertex.name
                if address:
                    self._address_to_tf_idx_and_vertex_map[address] = (i, vertex)
                    # Also store with simplified address for better matching
                    simplified = self._simplify_address(address)
                    if simplified != address:
                        self._address_to_tf_idx_and_vertex_map[simplified] = (i, vertex)
        
        # Map plan graph vertices
        for i, vertex in enumerate(self.tf_plan_graph.vertices):
            if vertex.block_type == BlockType.RESOURCE:
                address = vertex.attributes.get(TF_PLAN_RESOURCE_ADDRESS)
                if address:
                    self._address_to_tf_plan_idx_and_vertex_map[address] = (i, vertex)
    
    def _simplify_address(self, address: str) -> str:
        """
        Simplify an address by removing array indices for better matching.
        E.g., module.foo.resource.bar["key"] -> module.foo.resource.bar
        """
        import re
        return re.sub(r'\[.*?\]', '', address)

    def _get_tf_vertex_idx_from_tf_plan_vertex(self, v: TerraformBlock) -> Optional[int]:
        vertex = self._address_to_tf_idx_and_vertex_map.get(v.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS, ''))
        if vertex is None:
            return None
        return vertex[0]

    def append_vertex_to_terraform_graph(self, tf_plan_vertex: TerraformBlock, tf_plan_vertex_index: int, address: str) -> None:
        new_vertex_idx = len(self.tf_graph.vertices)
        self.tf_graph.vertices.append(tf_plan_vertex)
        self._address_to_tf_idx_and_vertex_map[address] = (new_vertex_idx, tf_plan_vertex)

        for edge in self.tf_plan_graph.out_edges[tf_plan_vertex_index]:
            dest = self.tf_plan_graph.vertices[edge.dest]
            dest_index = self._get_tf_vertex_idx_from_tf_plan_vertex(dest)
            if dest_index:
                self.tf_graph.create_edge(new_vertex_idx, dest_index, edge.label)
        for edge in self.tf_plan_graph.in_edges[tf_plan_vertex_index]:
            origin = self.tf_plan_graph.vertices[edge.origin]
            origin_index = self._get_tf_vertex_idx_from_tf_plan_vertex(origin)
            if origin_index:
                self.tf_graph.create_edge(origin_index, new_vertex_idx, edge.label)

    def enrich_tf_graph_attributes(self) -> None:
        for address, tf_plan_idx_and_vertex in self._address_to_tf_plan_idx_and_vertex_map.items():
            tf_plan_vertex_index, tf_plan_vertex = tf_plan_idx_and_vertex
            tf_idx_and_vertex = self._address_to_tf_idx_and_vertex_map.get(address)
            if not tf_idx_and_vertex:
                logging.info(f'Cant find this address: {address} in tf graph, adding it')
                self.append_vertex_to_terraform_graph(tf_plan_vertex, tf_plan_vertex_index, address)
                continue
            _, tf_vertex = tf_idx_and_vertex
            tf_vertex.attributes = {**tf_vertex.attributes, **tf_plan_vertex.attributes}
            tf_vertex.path = tf_plan_vertex.path
    
    def _infer_unresolved_connections(self) -> None:
        """
        Infer connections from Terraform source graph when plan values are unresolved.
        This scans all resource attributes for references to other resources and creates edges.
        """
        logging.info("Starting inference of unresolved connections from TF source")
        total_refs_found = 0
        
        # First try to infer from TF graph if available
        for address, (source_idx, source_vertex) in self._address_to_tf_idx_and_vertex_map.items():
            if source_vertex.block_type != BlockType.RESOURCE:
                continue
            
            # Find all resource references in this vertex's attributes
            references = self._find_resource_references_in_attributes(source_vertex.attributes)
            
            if references:
                logging.info(f"Found {len(references)} references in TF vertex {source_vertex.name}")
                total_refs_found += len(references)
            
            for ref in references:
                # Try to find the target resource and create an edge
                self._create_edge_for_reference(source_idx, source_vertex, ref)
        
        # Also check plan vertices for unresolved references
        # This handles cases where resources are in modules not loaded in TF graph
        logging.info("Checking plan vertices for unresolved connections...")
        for address, (plan_idx, plan_vertex) in self._address_to_tf_plan_idx_and_vertex_map.items():
            if plan_vertex.block_type != BlockType.RESOURCE:
                continue
            
            # Check for unresolved references in plan attributes
            self._infer_plan_connections(plan_idx, plan_vertex)
        
        # After inference, log the final edge counts
        tf_edge_count_after = sum(len(edges) for edges in self.tf_graph.out_edges.values())
        plan_edge_count_after = sum(len(edges) for edges in self.tf_plan_graph.out_edges.values())
        
        logging.info(f"Inference complete:")
        logging.info(f"  Found {total_refs_found} references in TF graph")
        logging.info(f"  TF graph edges: {tf_edge_count_after} (was {sum(len(edges) for edges in self.tf_graph.out_edges.values())})")
        logging.info(f"  Plan graph edges: {plan_edge_count_after} (was {sum(len(edges) for edges in self.tf_plan_graph.out_edges.values())})")
    
    def _infer_plan_connections(self, plan_idx: int, plan_vertex: TerraformBlock) -> None:
        """
        Infer connections for plan vertices when their attributes have unresolved references.
        Since the plan vertices don't have after_unknown in their attributes, we need to
        check if there's a corresponding TF vertex with the reference information.
        """
        resource_type = plan_vertex.attributes.get('resource_type', '')
        plan_address = plan_vertex.attributes.get(TF_PLAN_RESOURCE_ADDRESS, '')
        
        # Try to find corresponding TF vertex
        tf_vertex_data = self._address_to_tf_idx_and_vertex_map.get(plan_address)
        if not tf_vertex_data:
            # Try simplified address
            simplified = self._simplify_address(plan_address)
            tf_vertex_data = self._address_to_tf_idx_and_vertex_map.get(simplified)
        
        if tf_vertex_data:
            tf_idx, tf_vertex = tf_vertex_data
            # Check TF vertex for references
            references = self._find_resource_references_in_attributes(tf_vertex.attributes)
            
            for ref in references:
                # Create edges in the plan graph based on TF references
                self._create_plan_edge_for_reference(plan_idx, plan_vertex, ref)
        else:
            # No TF vertex found, try context-based inference
            # Check for common connection attributes
            connection_attributes = [
                'target_resource_id',  # Azure Monitor Diagnostic Settings
                'source_resource_id',  # Various Azure resources
                'destination_resource_id',  # Various Azure resources
                'resource_id',  # Generic reference
                'subnet_id',  # Network resources
                'network_security_group_id',  # Network resources
            ]
            
            for attr_name in connection_attributes:
                # If the attribute is not set in the plan, try to infer it
                attr_value = plan_vertex.attributes.get(attr_name)
                if attr_value is None:
                    logging.debug(f"Checking if {attr_name} needs inference for {plan_vertex.name}")
                    self._infer_connection_by_context(plan_idx, plan_vertex, attr_name)
    
    def _create_plan_edge_for_reference(self, source_idx: int, source_vertex: TerraformBlock, reference: Dict[str, Any]) -> None:
        """
        Create an edge in the plan graph based on a reference found in the TF graph.
        """
        target_resource_type = reference['resource_type']
        target_resource_name = reference['resource_name']
        attribute_path = reference.get('attribute_path', 'reference')
        
        # Find matching target in plan graph
        for target_address, (target_idx, target_vertex) in self._address_to_tf_plan_idx_and_vertex_map.items():
            if target_vertex.block_type != BlockType.RESOURCE:
                continue
            
            target_type = target_vertex.attributes.get('resource_type', '')
            
            if target_type == target_resource_type:
                # Check if the address matches the reference
                if self._plan_vertex_matches_reference(target_vertex, target_address, target_resource_type, target_resource_name):
                    # Create edge in plan graph
                    edge_exists = any(
                        edge.dest == target_idx
                        for edge in self.tf_plan_graph.out_edges.get(source_idx, [])
                    )
                    
                    if not edge_exists:
                        logging.info(f"Creating plan edge based on TF reference: {source_vertex.name} -> {target_vertex.name} (via {attribute_path})")
                        self.tf_plan_graph.create_edge(source_idx, target_idx, attribute_path)
    
    def _plan_vertex_matches_reference(self, vertex: TerraformBlock, address: str, resource_type: str, resource_name: str) -> bool:
        """
        Check if a plan vertex matches the given resource reference.
        """
        # Check if the address contains the expected pattern
        pattern = f"{resource_type}.{resource_name}"
        
        # For plan vertices, we need to be more flexible with matching
        # because of module prefixes and array indices
        simplified_address = self._simplify_address(address)
        
        return pattern in address or pattern in simplified_address
    
    def _infer_connection_by_context(self, source_idx: int, source_vertex: TerraformBlock, attr_name: str) -> None:
        """
        Infer connections based on resource type context and naming patterns.
        """
        source_address = source_vertex.attributes.get(TF_PLAN_RESOURCE_ADDRESS, '')
        source_type = source_vertex.attributes.get('resource_type', '')
        
        # Special handling for Azure Monitor Diagnostic Settings
        if source_type == 'azurerm_monitor_diagnostic_setting' and attr_name == 'target_resource_id':
            # Look for resources that could be monitored (Redis, SQL, etc.)
            # The diagnostic setting is usually in the same module or parent module
            module_prefix = source_address.rsplit('.azurerm_monitor_diagnostic_setting', 1)[0]
            
            for target_address, (target_idx, target_vertex) in self._address_to_tf_plan_idx_and_vertex_map.items():
                if target_vertex.block_type != BlockType.RESOURCE:
                    continue
                
                target_type = target_vertex.attributes.get('resource_type', '')
                
                # Check if this could be a monitored resource
                monitored_types = [
                    'azurerm_redis_cache',
                    'azurerm_sql_server',
                    'azurerm_sql_database',
                    'azurerm_postgresql_server',
                    'azurerm_mysql_server',
                    'azurerm_storage_account',
                    'azurerm_app_service',
                    'azurerm_function_app',
                ]
                
                if target_type in monitored_types:
                    # Check if they're in related modules (same parent or sibling)
                    if self._are_resources_related(source_address, target_address, module_prefix):
                        # Create edge
                        edge_exists = any(
                            edge.dest == target_idx
                            for edge in self.tf_plan_graph.out_edges.get(source_idx, [])
                        )
                        
                        if not edge_exists:
                            logging.info(f"Creating context-inferred edge: {source_vertex.name} -> {target_vertex.name} (via {attr_name})")
                            self.tf_plan_graph.create_edge(source_idx, target_idx, attr_name)
    
    def _are_resources_related(self, source_address: str, target_address: str, module_prefix: str) -> bool:
        """
        Check if two resources are related based on their addresses.
        Resources are considered related if they're in the same module hierarchy.
        """
        # Extract module paths
        source_parts = source_address.split('.')
        target_parts = target_address.split('.')
        
        # Check if they share a common module prefix
        # For example:
        # module.cache_redis.azurerm_redis_cache.redis_cache["key"]
        # module.cache_redis.module.monitor_diagnostic["key"].azurerm_monitor_diagnostic_setting.name["key"]
        
        # Get the base module for each
        source_module = '.'.join(p for p in source_parts if p.startswith('module'))
        target_module = '.'.join(p for p in target_parts if p.startswith('module'))
        
        # They're related if:
        # 1. They're in the exact same module
        # 2. One is in a submodule of the other
        # 3. They share a common parent module
        if source_module == target_module:
            return True
        
        if source_module.startswith(target_module) or target_module.startswith(source_module):
            return True
        
        # Check for common parent
        if source_module and target_module:
            source_parent = source_module.rsplit('.module.', 1)[0] if '.module.' in source_module else source_module
            target_parent = target_module.rsplit('.module.', 1)[0] if '.module.' in target_module else target_module
            if source_parent == target_parent:
                return True
        
        return False
    
    def _find_resource_references_in_attributes(self, attributes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Recursively scan attributes to find references to other resources.
        Returns a list of found references with their attribute paths.
        """
        references = []
        
        def scan_value(value: Any, path: str = "") -> None:
            if isinstance(value, str):
                # Check if this string contains a resource reference
                ref_info = self._parse_resource_reference(value)
                if ref_info:
                    ref_info['attribute_path'] = path
                    ref_info['original_value'] = value
                    references.append(ref_info)
            elif isinstance(value, dict):
                for key, val in value.items():
                    new_path = f"{path}.{key}" if path else key
                    scan_value(val, new_path)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    scan_value(item, f"{path}[{i}]")
        
        scan_value(attributes)
        return references
    
    def _parse_resource_reference(self, value: Any) -> Optional[Dict[str, str]]:
        """
        Parse a potential Terraform resource reference.
        Handles various formats including:
        - resource_type.resource_name.attribute
        - resource_type.resource_name[index].attribute
        - resource_type.resource_name["key"].attribute
        - resource_type.resource_name[each.key].attribute
        - module.module_name.resource_type.resource_name.attribute
        """
        if not value or not isinstance(value, str):
            return None
        
        # Pattern to match resource references
        # This pattern captures resource_type.resource_name with optional module prefix and indexing
        patterns = [
            # Direct resource reference
            r'^([a-z][a-z0-9_]*_[a-z][a-z0-9_]*)\.([a-zA-Z0-9_-]+)(?:\[.*?\])?(?:\..*)?$',
            # Module resource reference
            r'^module\.[a-zA-Z0-9_-]+\.([a-z][a-z0-9_]*_[a-z][a-z0-9_]*)\.([a-zA-Z0-9_-]+)(?:\[.*?\])?(?:\..*)?$',
            # Data source reference
            r'^data\.([a-z][a-z0-9_]*_[a-z][a-z0-9_]*)\.([a-zA-Z0-9_-]+)(?:\[.*?\])?(?:\..*)?$'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, value)
            if match:
                return {
                    'resource_type': match.group(1),
                    'resource_name': match.group(2),
                    'is_data': 'data.' in value
                }
        
        return None
    
    def _create_edge_for_reference(self, source_idx: int, source_vertex: TerraformBlock, reference: Dict[str, Any]) -> None:
        """
        Create an edge from source vertex to the referenced resource.
        """
        target_resource_type = reference['resource_type']
        target_resource_name = reference['resource_name']
        attribute_path = reference.get('attribute_path', 'reference')
        
        # Find matching target resources in the graph
        for address, (target_idx, target_vertex) in self._address_to_tf_idx_and_vertex_map.items():
            if target_vertex.block_type != BlockType.RESOURCE:
                continue
            
            # Check if this vertex matches the reference
            if self._vertex_matches_reference(target_vertex, address, target_resource_type, target_resource_name):
                # Create edge in TF graph
                edge_label = f"{attribute_path}"
                
                # Check if edge already exists
                edge_exists = any(
                    edge.dest == target_idx and edge.label == edge_label
                    for edge in self.tf_graph.out_edges.get(source_idx, [])
                )
                
                if not edge_exists:
                    logging.info(f"Creating inferred edge: {source_vertex.name} -> {target_vertex.name} (via {attribute_path})")
                    self.tf_graph.create_edge(source_idx, target_idx, edge_label)
                    
                    # Also try to create edge in plan graph if vertices exist there
                    self._create_plan_graph_edge(source_vertex, target_vertex, edge_label)
    
    def _vertex_matches_reference(self, vertex: TerraformBlock, address: str, resource_type: str, resource_name: str) -> bool:
        """
        Check if a vertex matches the given resource reference.
        Handles various address formats including those with for_each/count.
        """
        vertex_resource_type = vertex.attributes.get('resource_type', '')
        
        # First check if resource types match
        if vertex_resource_type != resource_type:
            return False
        
        # Check if the address contains the expected resource pattern
        # This handles cases like:
        # - resource_type.resource_name
        # - module.module_name.resource_type.resource_name["key"]
        # - resource_type.resource_name[0]
        pattern = f"{resource_type}.{resource_name}"
        
        # For exact matching, also check the vertex name
        if pattern in address or pattern in vertex.name:
            return True
        
        # Additional check for resources with different naming in plan vs source
        if hasattr(vertex, 'config') and isinstance(vertex.config, dict):
            # Check if the resource block name matches
            for key in vertex.config.keys():
                if key == resource_name:
                    return True
        
        return False
    
    def _create_plan_graph_edge(self, source_vertex: TerraformBlock, target_vertex: TerraformBlock, edge_label: str) -> None:
        """
        Create an edge in the plan graph if both vertices exist there.
        """
        source_address = source_vertex.attributes.get(TF_PLAN_RESOURCE_ADDRESS)
        target_address = target_vertex.attributes.get(TF_PLAN_RESOURCE_ADDRESS)
        
        if not source_address or not target_address:
            return
        
        source_plan_data = self._address_to_tf_plan_idx_and_vertex_map.get(source_address)
        target_plan_data = self._address_to_tf_plan_idx_and_vertex_map.get(target_address)
        
        if source_plan_data and target_plan_data:
            source_plan_idx = source_plan_data[0]
            target_plan_idx = target_plan_data[0]
            
            # Check if edge already exists
            edge_exists = any(
                edge.dest == target_plan_idx
                for edge in self.tf_plan_graph.out_edges.get(source_plan_idx, [])
            )
            
            if not edge_exists:
                logging.info(f"Creating inferred edge in plan graph: {source_address} -> {target_address}")
                self.tf_plan_graph.create_edge(source_plan_idx, target_plan_idx, edge_label)

    def filter_report(self, report: Report) -> None:
        report.failed_checks = [check for check in report.failed_checks if
                                check.resource_address in self._address_to_tf_plan_idx_and_vertex_map]
        report.passed_checks = [check for check in report.passed_checks if
                                check.resource_address in self._address_to_tf_plan_idx_and_vertex_map]
        report.skipped_checks = [check for check in report.skipped_checks if
                                 check.resource_address in self._address_to_tf_plan_idx_and_vertex_map]
        # No need to filter other fields for now
        report.resources = set()
        report.extra_resources = set()
        report.parsing_errors = []
