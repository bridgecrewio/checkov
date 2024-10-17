import os
import shutil
from unittest import TestCase, mock

from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_to_tf_definitions import convert_graph_vertices_to_tf_definitions
from checkov.terraform.graph_manager import TerraformGraphManager
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.terraform.modules.module_utils import external_modules_download_path
from checkov.terraform.plan_utils import create_definitions

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestGraphBuilder(TestCase):
    def test_build_graph(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/general_example')

        graph_manager = TerraformGraphManager(db_connector=NetworkxConnector())
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
        local_node = graph.vertices[graph.vertices_block_name_map[BlockType.LOCALS]["bucket_name"][0]]

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
                           f'expected to find edge from [{node_from.block_type} {node_from.name}] to [{node_to.block_type} {node_to.name}] with label [{expected_label}]')
        if not any(e.label == expected_label for e in matching_edges):
            self.fail(
                f'expected to find edge from [{node_from.block_type} {node_from.name}] to [{node_to.block_type} {node_to.name}] with label [{expected_label}], found edges: {[str(e) for e in matching_edges]}')

    @staticmethod
    def get_vertex_by_name_and_type(local_graph, block_type, name, multiple=False):
        vertices = [local_graph.vertices[i] for i in local_graph.vertices_block_name_map[block_type][name]]
        if multiple:
            return vertices
        return vertices[0]

    def test_update_vertices_configs_deep_nesting(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/variable_rendering/render_deep_nesting')
        graph_manager = TerraformGraphManager(NetworkxConnector())
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)
        expected_config = {
            "aws_s3_bucket": {
                "default": {
                    "server_side_encryption_configuration": [
                        {
                            "rule": [
                                {
                                    "apply_server_side_encryption_by_default": [
                                        {"kms_master_key_id": [""], "sse_algorithm": ["AES256"]}
                                    ]
                                }
                            ]
                        }
                    ],
                    "__start_line__": 1,
                    "__end_line__": 10,
                    "__address__": "aws_s3_bucket.default"
                }
            }
        }
        actual_config = local_graph.vertices[local_graph.vertices_by_block_type.get(BlockType.RESOURCE)[0]].config
        self.assertDictEqual(expected_config, actual_config)

    @mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
    def test_build_graph_with_linked_modules(self):
        # see the image to view the expected graph in tests/resources/modules/linked_modules/expected_graph.png
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/modules/linked_modules'))

        graph_manager = TerraformGraphManager(NetworkxConnector())
        local_graph, tf_definitions = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=False)

        vertices_by_block_type = local_graph.vertices_by_block_type

        expected_vertices_num_by_type = {
            BlockType.VARIABLE: 5,
            BlockType.RESOURCE: 5,
            BlockType.OUTPUT: 3,
            BlockType.MODULE: 2,
            BlockType.DATA: 1,
        }

        for block_type, count in expected_vertices_num_by_type.items():
            self.assertEqual(count, len(vertices_by_block_type[block_type]))

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
        self.check_edge(local_graph, node_from=output_this_s3_bucket_id, node_to=resource_aws_s3_bucket_policy,
                        expected_label='value')
        self.check_edge(local_graph, node_from=output_this_s3_bucket_id, node_to=resource_aws_s3_bucket,
                        expected_label='value')

    @mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
    def test_build_graph_with_linked_registry_modules(self):
        resources_dir = os.path.realpath(
            os.path.join(TEST_DIRNAME, '../resources/modules/registry_security_group_inner_module'))

        graph_manager = TerraformGraphManager(NetworkxConnector())
        local_graph, tf_definitions = graph_manager.build_graph_from_source_directory(resources_dir,
                                                                                      render_variables=True,
                                                                                      download_external_modules=True)

        outputs_vpcs = self.get_vertex_by_name_and_type(local_graph, BlockType.OUTPUT, 'security_group_vpc_id',
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
        self.check_edge(local_graph, node_from=output_this_security_group_vpc_id_outer,
                        node_to=resource_security_group_this, expected_label='value')
        self.check_edge(local_graph, node_from=output_this_security_group_vpc_id_outer,
                        node_to=resource_security_group_this_name_prefix, expected_label='value')

        # cleanup
        if os.path.exists(os.path.join(resources_dir, external_modules_download_path)):
            shutil.rmtree(os.path.join(resources_dir, external_modules_download_path))

    def test_build_graph_with_deep_nested_edges(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/k8_service'))

        graph_manager = TerraformGraphManager(NetworkxConnector())
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

    def test_blocks_from_local_graph_module(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/modules/stacks'))
        graph_manager = TerraformGraphManager(NetworkxConnector())
        local_graph, tf = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)
        tf, _ = convert_graph_vertices_to_tf_definitions(local_graph.vertices, resources_dir)
        found_results = 0
        for key, value in tf.items():
            if key.file_path.startswith(os.path.join(os.path.dirname(resources_dir), 's3_inner_modules', 'inner', 'main.tf')):
                conf = value['resource'][0]['aws_s3_bucket']['inner_s3']
                new_key = build_new_key_for_tf_definition(key)
                if 'stage/main' in new_key or 'prod/main' in new_key:
                    self.assertTrue(conf['versioning'][0]['enabled'][0])
                    found_results += 1
                elif 'test/main' in new_key:
                    self.assertFalse(conf['versioning'][0]['enabled'][0])
                    found_results += 1
        self.assertEqual(found_results, 3)

    def test_build_graph_with_dynamic_blocks(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/dynamic_lambda_function'))

        graph_manager = TerraformGraphManager(NetworkxConnector())
        local_graph, tf = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)
        lambda_attributes = local_graph.vertices[0].attributes
        self.assertIn("dead_letter_config", lambda_attributes.keys())

    def test_get_attribute_dict_with_list_value(self):
        # given
        resources_dir = os.path.join(TEST_DIRNAME, "../resources/s3_bucket_grant")
        graph_manager = TerraformGraphManager(NetworkxConnector())
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        # when
        attributes = local_graph.vertices[
            local_graph.vertices_by_block_type.get(BlockType.RESOURCE)[0]
        ].get_attribute_dict()

        # then
        expected_grant_attribute = [
            {"permissions": ["READ_ACP"], "type": "Group", "uri": "http://acs.amazonaws.com/groups/global/AllUsers"},
            {"id": "1234567890", "permissions": ["FULL_CONTROL"], "type": "CanonicalUser"},
        ]

        self.assertCountEqual(expected_grant_attribute, attributes["grant"])

    def test_build_graph_terraform_block(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/terraform_block')

        graph_manager = TerraformGraphManager(db_connector=NetworkxConnector())
        graph, tf_definitions = graph_manager.build_graph_from_source_directory(resources_dir)

        terraform_blocks = graph.vertices_by_block_type[BlockType.TERRAFORM]
        self.assertEqual(1, len(terraform_blocks))

        terraform_block = graph.vertices[terraform_blocks[0]]
        expected_attributes = ["backend", "required_version", "required_providers"]
        for attr in expected_attributes:
            self.assertIn(attr, list(terraform_block.attributes.keys()))

    @mock.patch.dict(os.environ, {"CHECKOV_EXPERIMENTAL_CROSS_VARIABLE_EDGES": "True"})
    def test_build_graph_with_cross_variables_connections(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/cross_variables')

        graph_manager = TerraformGraphManager(NetworkxConnector())
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        var_bucket_resource = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE, 'aws_s3_bucket_public_access_block.var_bucket')
        bucket_resource = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE, 'aws_s3_bucket.example')

        self.assertEqual(len(local_graph.edges), 4)
        self.check_edge(local_graph, node_from=var_bucket_resource, node_to=bucket_resource,
                        expected_label="[cross-variable] bucket")

    @mock.patch.dict(os.environ, {"CHECKOV_EXPERIMENTAL_CROSS_VARIABLE_EDGES": "True"})
    def test_build_graph_with_cross_variables_connections_from_module(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/cross_variables2/main'))

        graph_manager = TerraformGraphManager(NetworkxConnector())
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        var_bucket_resource = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE, 'aws_s3_bucket_public_access_block.var_bucket')
        bucket_resource = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE, 'aws_s3_bucket.example')

        self.assertEqual(len(local_graph.edges), 6)
        self.check_edge(local_graph, node_from=var_bucket_resource, node_to=bucket_resource,
                        expected_label="[cross-variable] bucket")

    @mock.patch.dict(os.environ, {"CHECKOV_EXPERIMENTAL_CROSS_VARIABLE_EDGES": "True"})
    def test_build_graph_with_cross_modules_connections(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/cross_modules'))

        graph_manager = TerraformGraphManager(NetworkxConnector())
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        var_bucket_resource = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE,
                                                               'aws_s3_bucket_public_access_block.var_bucket')
        bucket_resource = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE, 'aws_s3_bucket.example')

        self.assertEqual(len(local_graph.edges), 5)
        self.check_edge(local_graph, node_from=var_bucket_resource, node_to=bucket_resource,
                        expected_label="[cross-variable] bucket")

    @mock.patch.dict(os.environ, {"CHECKOV_EXPERIMENTAL_CROSS_VARIABLE_EDGES": "True"})
    def test_build_graph_with_cross_nested_modules_connections(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/cross_modules2'))

        graph_manager = TerraformGraphManager(NetworkxConnector())
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        var_bucket_resource = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE,
                                                               'aws_s3_bucket_public_access_block.var_bucket')
        bucket_resource = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE, 'aws_s3_bucket.example')

        self.assertEqual(len(local_graph.edges), 8)
        self.check_edge(local_graph, node_from=var_bucket_resource, node_to=bucket_resource,
                        expected_label="[cross-variable] bucket")

    def test_nested_modules_address_attribute(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/nested_modules_address'))
        graph_manager = TerraformGraphManager(NetworkxConnector())
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)
        module_1 = self.get_vertex_by_name_and_type(local_graph, BlockType.MODULE, 'inner_s3_module')
        assert module_1.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS) == 'module.s3_module.inner_s3_module'
        module_2 = self.get_vertex_by_name_and_type(local_graph, BlockType.MODULE, 's3_module')
        assert module_2.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS) == 's3_module'
        resource_1 = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE, 'aws_s3_bucket_public_access_block.var_bucket')
        assert resource_1.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS) == 'module.s3_module.module.inner_s3_module.aws_s3_bucket_public_access_block.var_bucket'
        resource_2 = self.get_vertex_by_name_and_type(local_graph, BlockType.RESOURCE, 'aws_s3_bucket.example')
        assert resource_2.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS) == 'aws_s3_bucket.example'
        provider = self.get_vertex_by_name_and_type(local_graph, BlockType.PROVIDER, 'aws.test_provider')
        assert provider.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS) == 'aws.test_provider'

    # Related to https://github.com/bridgecrewio/checkov/issues/4324
    def test_build_graph_for_each_with_variables_and_dynamic_not_crash(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/for_each')

        graph_manager = TerraformGraphManager(db_connector=NetworkxConnector())
        # Shouldn't throw exception
        graph_manager.build_graph_from_source_directory(resources_dir)

    def test_build_rustworkx_graph(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/general_example')

        graph_manager = TerraformGraphManager(db_connector=RustworkxConnector())
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
        local_node = graph.vertices[graph.vertices_block_name_map[BlockType.LOCALS]["bucket_name"][0]]

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

    def test_multiple_modules_with_connected_resources(self):
        valid_plan_path = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/modules_edges_tfplan/tfplan.json'))
        definitions, definitions_raw = create_definitions(root_folder=None, files=[valid_plan_path])
        graph_manager = TerraformGraphManager(db_connector=RustworkxConnector())
        tf_plan_local_graph = graph_manager.build_graph_from_definitions(definitions, render_variables=False)
        self.assertTrue(tf_plan_local_graph.in_edges[3])


def build_new_key_for_tf_definition(key):
    key = key.tf_source_modules
    new_key = ''
    while key.nested_tf_module:
        new_key += f'{key.nested_tf_module.path}'
        key = key.nested_tf_module
    return new_key
