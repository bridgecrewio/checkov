import os
import shutil
from unittest import TestCase

from checkov.graph.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.graph.terraform.graph_manager import GraphManager
from checkov.graph.parser import external_modules_download_path

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestGraphBuilder(TestCase):

    def test_build_graph(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/general_example')

        graph_manager = GraphManager()
        graph, tf_definitions = graph_manager.build_graph_from_source_directory(resources_dir)

        expected_num_of_var_nodes = 3
        expected_num_of_locals_nodes = 1
        expected_num_of_resources_nodes = 1
        expected_num_of_provider_nodes = 1
        vertices_by_block_type = graph.vertices_by_block_type
        self.assertEqual(expected_num_of_var_nodes, len(vertices_by_block_type[BlockType.VARIABLE]))
        self.assertEqual(expected_num_of_locals_nodes, len(vertices_by_block_type[BlockType.LOCALS]))
        self.assertEqual(expected_num_of_resources_nodes, len(vertices_by_block_type[BlockType.RESOURCE]))
        self.assertEqual(expected_num_of_provider_nodes, len(vertices_by_block_type[BlockType.PROVIDER]))

        provider_node = graph.vertices[vertices_by_block_type[BlockType.PROVIDER][0]]
        resource_node = graph.vertices[vertices_by_block_type[BlockType.RESOURCE][0]]
        local_node = graph.vertices[vertices_by_block_type[BlockType.LOCALS][0]]

        var_bucket_name_node = None
        var_region_node = None
        var_aws_profile_node = None
        for index in vertices_by_block_type[BlockType.VARIABLE]:
            var_node = graph.vertices[index]
            if var_node.name == 'aws_profile':
                var_aws_profile_node = var_node
            if var_node.name == 'bucket_name':
                var_bucket_name_node = var_node
            if var_node.name == 'region':
                var_region_node = var_node

        self.check_edge(graph, resource_node, local_node, 'bucket')
        self.check_edge(graph, resource_node, provider_node, 'provider')
        self.check_edge(graph, resource_node, var_region_node, 'region')
        self.check_edge(graph, provider_node, var_aws_profile_node, 'profile')
        self.check_edge(graph, local_node, var_bucket_name_node, 'bucket_name')

    def check_edge(self, graph, node_from, node_to, expected_label):
        hashed_from = node_from.get_hash()
        hashed_to = node_to.get_hash()
        matching_edges = []
        for edge in graph.edges:
            if graph.vertices[edge.origin].get_hash() == hashed_from and graph.vertices[edge.dest].get_hash() == hashed_to:
                matching_edges.append(edge)
        self.assertGreater(len(matching_edges), 0,
                           f'expected to find edge from [{node_from.block_type.value} {node_from.name}] to [{node_to.block_type.value} {node_to.name}] with label [{expected_label}]')
        if not any(e.label == expected_label for e in matching_edges):
            self.fail(
                f'expected to find edge from [{node_from.block_type.value} {node_from.name}] to [{node_to.block_type.value} {node_to.name}] with label [{expected_label}], found edges: {[str(e) for e in matching_edges]}')

    @staticmethod
    def get_vertex_by_name_and_type(local_graph, block_type, name, multiple=False):
        vertices = [local_graph.vertices[i] for i in local_graph.vertices_block_name_map[block_type][name]]
        if multiple:
            return vertices
        return vertices[0]

    def test_update_vertices_configs_deep_nesting(self):

        resources_dir = os.path.join(TEST_DIRNAME, '../resources/variable_rendering/render_deep_nesting')
        graph_manager = GraphManager()
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)
        expected_config = {'aws_s3_bucket': {'default': {'server_side_encryption_configuration': [
            {'rule': [{'apply_server_side_encryption_by_default': [
                {'sse_algorithm': ['AES256'], 'kms_master_key_id': ['']}]}]}]}}}
        actual_config = local_graph.vertices[local_graph.vertices_by_block_type.get(BlockType.RESOURCE)[0]].config
        self.assertDictEqual(expected_config, actual_config)
        print('')

    def test_build_graph_with_linked_modules(self):
        # see the image to view the expected graph in tests/resources/modules/linked_modules/expected_graph.png
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/modules/linked_modules'))

        graph_manager = GraphManager()
        local_graph, tf_definitions = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=False)

        vertices_by_block_type = local_graph.vertices_by_block_type

        expected_vertices_num_by_type = {
            BlockType.VARIABLE: 5,
            BlockType.RESOURCE: 5,
            BlockType.OUTPUT: 3,
            BlockType.MODULE: 3,
            BlockType.DATA: 1,
        }

        for block_type, count in expected_vertices_num_by_type.items():
            self.assertEqual(count, len(vertices_by_block_type[block_type]))

        module_all_notifications = self.get_vertex_by_name_and_type(local_graph, BlockType.MODULE, 'all_notifications')
        output_this_lambda_func_arn = self.get_vertex_by_name_and_type(local_graph, BlockType.OUTPUT,
                                                                       'this_lambda_function_arn')
        output_this_lambda_func_name = self.get_vertex_by_name_and_type(local_graph, BlockType.OUTPUT,
                                                                        'this_lambda_function_name')
        output_this_s3_bucket_id = self.get_vertex_by_name_and_type(local_graph, BlockType.OUTPUT, 'this_s3_bucket_id')
        resource_aws_lambda_function = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE,
                                                                        'aws_lambda_function.this')
        resource_aws_s3_bucket_policy = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE,
                                                                         'aws_s3_bucket_policy.this')
        resource_aws_s3_bucket = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE, 'aws_s3_bucket.this')

        self.check_edge(local_graph, node_from=output_this_lambda_func_arn, node_to=resource_aws_lambda_function,
                        expected_label='value')
        self.check_edge(local_graph, node_from=output_this_lambda_func_name, node_to=resource_aws_lambda_function,
                        expected_label='value')
        self.check_edge(local_graph, node_from=module_all_notifications, node_to=output_this_lambda_func_name,
                        expected_label='lambda_notifications.lambda1.function_name')
        self.check_edge(local_graph, node_from=module_all_notifications, node_to=output_this_lambda_func_arn,
                        expected_label='lambda_notifications.lambda1.function_arn')
        self.check_edge(local_graph, node_from=module_all_notifications, node_to=output_this_s3_bucket_id,
                        expected_label='bucket')
        self.check_edge(local_graph, node_from=output_this_s3_bucket_id, node_to=resource_aws_s3_bucket_policy,
                        expected_label='value')
        self.check_edge(local_graph, node_from=output_this_s3_bucket_id, node_to=resource_aws_s3_bucket,
                        expected_label='value')

    def test_build_graph_with_linked_registry_modules(self):
        os.environ['DOWNLOAD_EXTERNAL_MODULES'] = 'true'
        resources_dir = os.path.realpath(
            os.path.join(TEST_DIRNAME, '../resources/modules/registry_security_group_inner_module'))

        graph_manager = GraphManager()
        local_graph, tf_definitions = graph_manager.build_graph_from_source_directory(resources_dir,
                                                                                      render_variables=True)

        outputs_vpcs = self.get_vertex_by_name_and_type(local_graph, BlockType.OUTPUT, 'this_security_group_vpc_id',
                                                        multiple=True)
        resource_flow_log = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE,
                                                             'aws_flow_log.related_flow_log')
        resource_security_group_this = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE,
                                                                        'aws_security_group.this')
        resource_security_group_this_name_prefix = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE,
                                                                                    'aws_security_group.this_name_prefix')

        output_this_security_group_vpc_id_inner = [o for o in outputs_vpcs if 'http-80' in o.path][0]
        output_this_security_group_vpc_id_outer = [o for o in outputs_vpcs if 'http-80' not in o.path][0]

        self.check_edge(local_graph, node_from=resource_flow_log, node_to=output_this_security_group_vpc_id_inner,
                        expected_label='vpc_id')
        self.check_edge(local_graph, node_from=output_this_security_group_vpc_id_inner,
                        node_to=output_this_security_group_vpc_id_outer, expected_label='value')
        self.check_edge(local_graph, node_from=output_this_security_group_vpc_id_outer,
                        node_to=resource_security_group_this, expected_label='value')
        self.check_edge(local_graph, node_from=output_this_security_group_vpc_id_outer,
                        node_to=resource_security_group_this_name_prefix, expected_label='value')

        # cleanup
        if os.path.exists(os.path.join(resources_dir, external_modules_download_path)):
            shutil.rmtree(os.path.join(resources_dir, external_modules_download_path))

    def test_build_graph_with_deep_nested_edges(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/k8_service'))

        graph_manager = GraphManager()
        local_graph, tf = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        resource_kubernetes_deployment = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE,
                                                                          'kubernetes_deployment.bazel_remote_cache')
        locals_name = self.get_vertex_by_name_and_type(local_graph, BlockType.LOCALS, 'name')
        locals_labels = self.get_vertex_by_name_and_type(local_graph, BlockType.LOCALS, 'labels')

        self.check_edge(local_graph, node_from=locals_labels, node_to=locals_name,
                        expected_label="labels.app.kubernetes.io/name")
        self.check_edge(local_graph, node_from=resource_kubernetes_deployment, node_to=locals_name,
                        expected_label="metadata.name")
        self.check_edge(local_graph, node_from=resource_kubernetes_deployment, node_to=locals_name,
                        expected_label="spec.template.metadata.name")
        self.check_edge(local_graph, node_from=resource_kubernetes_deployment, node_to=locals_name,
                        expected_label="spec.template.spec.container.name")
        self.check_edge(local_graph, node_from=resource_kubernetes_deployment, node_to=locals_name,
                        expected_label="spec.template.spec.volume.1.config_map.name")
