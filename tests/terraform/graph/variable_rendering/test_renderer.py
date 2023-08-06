import os
import time
from pathlib import Path
from unittest import mock
from unittest.case import TestCase

from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_manager import TerraformGraphManager
from checkov.terraform.graph_builder.variable_rendering.renderer import TerraformVariableRenderer
from checkov.terraform.graph_builder.graph_to_tf_definitions import convert_graph_vertices_to_tf_definitions
from tests.terraform.graph.variable_rendering.expected_data import (
    expected_terragoat_local_resource_prefix,
    expected_terragoat_db_instance,
    expected_eks,
    expected_provider,
)

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@mock.patch.dict(os.environ, {"RENDER_ASYNC_MAX_WORKERS": "50", "RENDER_VARIABLES_ASYNC": "False"})
class TestRenderer(TestCase):
    def test_render_local(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/variable_rendering/render_local')
        graph_manager = TerraformGraphManager('acme', ['acme'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        expected_local = {'bucket_name': 'test_bucket_name'}
        expected_resource = {'region': 'us-west-2', 'bucket': expected_local['bucket_name']}

        self.compare_vertex_attributes(local_graph, expected_local, BlockType.LOCALS, 'bucket_name')
        self.compare_vertex_attributes(local_graph, expected_resource, BlockType.RESOURCE, 'aws_s3_bucket.template_bucket')

    def test_render_variable(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/variable_rendering/render_variable')
        graph_manager = TerraformGraphManager('acme', ['acme'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        expected_resource = {'region': "us-west-2", 'bucket': "test_bucket_name", "acl": "acl", "force_destroy": True}

        self.compare_vertex_attributes(local_graph, expected_resource, BlockType.RESOURCE, 'aws_s3_bucket.template_bucket')

    def test_render_variable(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/variable_rendering/render_variable')
        graph_manager = TerraformGraphManager('acme', ['acme'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        expected_resource = {'region': "us-west-2", 'bucket': "Storage bucket", "acl": "acl", "force_destroy": True}

        self.compare_vertex_attributes(local_graph, expected_resource, BlockType.RESOURCE, 'aws_s3_bucket.storage_bucket')

    def test_render_local_from_variable(self):
        resources_dir = os.path.join(TEST_DIRNAME,
                                     '../resources/variable_rendering/render_local_from_variable')
        graph_manager = TerraformGraphManager('acme', ['acme'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        expected_local = {'bucket_name': 'test_bucket_name'}

        self.compare_vertex_attributes(local_graph, expected_local, BlockType.LOCALS, 'bucket_name')

    def test_general_example(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/general_example')
        graph_manager = TerraformGraphManager('acme', ['acme'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        expected_provider = {'profile': 'default', 'region': 'us-east-1', 'alias': 'east1'}
        expected_local = {'bucket_name': {'val': 'MyBucket'}}
        expected_resource = {'region': 'us-west-2', 'bucket': expected_local['bucket_name']}

        self.compare_vertex_attributes(local_graph, expected_provider, BlockType.PROVIDER, 'aws.east1')
        self.compare_vertex_attributes(local_graph, expected_local, BlockType.LOCALS, 'bucket_name')
        self.compare_vertex_attributes(local_graph, expected_resource, BlockType.RESOURCE, 'aws_s3_bucket.template_bucket')

    def test_terragoat_db_app(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/variable_rendering/render_terragoat_db_app')
        graph_manager = TerraformGraphManager('acme', ['acme'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        self.compare_vertex_attributes(local_graph, expected_terragoat_local_resource_prefix, BlockType.LOCALS, 'resource_prefix')
        self.compare_vertex_attributes(local_graph, expected_terragoat_db_instance, BlockType.RESOURCE, "aws_db_instance.default")

    def test_render_nested_modules(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/variable_rendering/render_nested_modules')
        graph_manager = TerraformGraphManager('acme', ['acme'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        expected_aws_instance = {"instance_type": "bar"}
        self.compare_vertex_attributes(local_graph, expected_aws_instance, BlockType.RESOURCE, "aws_instance.example")
        expected_output_bucket_acl = {"value": "z"}
        self.compare_vertex_attributes(local_graph, expected_output_bucket_acl, BlockType.OUTPUT, "bucket_acl")

    def compare_vertex_attributes(self, local_graph, expected_attributes, block_type, block_name):
        vertex = local_graph.vertices[local_graph.vertices_block_name_map[block_type][block_name][0]]
        print(f'breadcrumbs = {vertex.breadcrumbs}')
        vertex_attributes = vertex.get_attribute_dict()
        for attribute_key, expected_value in expected_attributes.items():
            actual_value = vertex_attributes.get(attribute_key)
            self.assertEqual(expected_value, actual_value, f'error during comparing {block_type} in attribute key: {attribute_key}')

    def test_breadcrumbs(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/s3_bucket')
        graph_manager = TerraformGraphManager('acme', ['acme'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)
        vertices = local_graph.vertices
        s3_vertex = list(filter(lambda vertex: vertex.block_type == BlockType.RESOURCE, vertices))[0]
        changed_attributes = list(s3_vertex.changed_attributes.keys())
        self.assertCountEqual(changed_attributes, ['versioning.enabled', 'acl'])

        for breadcrumbs in s3_vertex.changed_attributes.values():
            self.assertEqual(1, len(breadcrumbs))

        acl_origin_vertex = s3_vertex.changed_attributes.get('acl')[0]
        matching_acl_vertex = vertices[acl_origin_vertex.vertex_id]
        self.assertEqual('acl', matching_acl_vertex.name)

        versioning_origin_vertex = s3_vertex.changed_attributes.get('versioning.enabled')[0]
        matching_versioning_vertex = vertices[versioning_origin_vertex.vertex_id]
        self.assertEqual('is_enabled', matching_versioning_vertex.name)

    def test_multiple_breadcrumbs(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/general_example')
        graph_manager = TerraformGraphManager('acme', ['acme'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)
        vertices = local_graph.vertices
        s3_vertex = list(filter(lambda vertex: vertex.block_type == BlockType.RESOURCE, vertices))[0]
        changed_attributes = list(s3_vertex.changed_attributes.keys())
        self.assertListEqual(changed_attributes, ['region', 'bucket'])

        bucket_vertices_ids_list = s3_vertex.changed_attributes.get('bucket')
        self.assertEqual(2, len(bucket_vertices_ids_list))

        first_vertex = vertices[bucket_vertices_ids_list[0].vertex_id]
        self.assertEqual(BlockType.VARIABLE, first_vertex.block_type)
        self.assertEqual('bucket_name', first_vertex.name)
        self.assertEqual(first_vertex.name, s3_vertex.breadcrumbs['bucket'][0]['name'])

        second_vertex = vertices[bucket_vertices_ids_list[1].vertex_id]
        self.assertEqual(BlockType.LOCALS, second_vertex.block_type)
        self.assertEqual('bucket_name', second_vertex.name)
        self.assertEqual(second_vertex.name, s3_vertex.breadcrumbs['bucket'][1]['name'])

    def test_render_lambda(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/variable_rendering/render_lambda')
        graph_manager = TerraformGraphManager('acme', ['acme'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        expected_aws_lambda_permission = {'count': 0, 'statement_id': 'test_statement_id', 'action': 'lambda:InvokeFunction', 'function_name': 'my-func', 'principal': 'dumbeldor', 'resource_type': 'aws_lambda_permission'}

        self.compare_vertex_attributes(local_graph, expected_aws_lambda_permission, BlockType.RESOURCE, "aws_lambda_permission.test_lambda_permissions")

    def test_eks(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/variable_rendering/terraform-aws-eks-master')
        graph_manager = TerraformGraphManager('eks', ['eks'])
        local_graph, tf_def = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        for v in local_graph.vertices:
            expected_v = expected_eks.get(v.block_type, {}).get(v.name)
            if expected_v:
                for attribute_key, expected_value in expected_v.items():
                    actual_value = v.attributes.get(attribute_key)
                    self.assertEqual(expected_value, actual_value,
                                     f'error during comparing {v.block_type} in attribute key: {attribute_key}')


    def test_dict_tfvar(self):
        resources_dir = os.path.join(TEST_DIRNAME, '../resources/variable_rendering/render_dictionary_tfvars')
        graph_manager = TerraformGraphManager('d', ['d'])
        local_graph, tf_def = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=True)

        for v in local_graph.vertices:
            expected_v = expected_provider.get(v.block_type, {}).get(v.name)
            if expected_v:
                for attribute_key, expected_value in expected_v.items():
                    actual_value = v.attributes.get(attribute_key)
                    self.assertEqual(expected_value, actual_value,
                                     f'error during comparing {v.block_type} in attribute key: {attribute_key}')

    @mock.patch.dict(os.environ, {"CHECKOV_NEW_TF_PARSER": "False"})
    def test_graph_rendering_order(self):
        resource_path = os.path.join(TEST_DIRNAME, "..", "resources", "module_rendering", "example")
        graph_manager = TerraformGraphManager('m', ['m'])
        local_graph, tf_def = graph_manager.build_graph_from_source_directory(resource_path, render_variables=True)
        module_vertices = list(filter(lambda v: v.block_type == BlockType.MODULE, local_graph.vertices))
        existing = set()
        self.assertEqual(6, len(local_graph.edges))
        for e in local_graph.edges:
            if e in existing:
                self.fail("No 2 edges should be aimed at the same vertex in this example")
            else:
                existing.add(e)
        count = 0
        found = 0
        for v in module_vertices:
            if v.name == 'second-mock':
                found += 1
                if v.attributes['input'] == ['aws_s3_bucket.some-bucket.arn']:
                    count += 1
        self.assertEqual(found, count, f"Expected all instances to have the same value, found {found} instances but only {count} correct values")

    def test_graph_rendering_order_nested_module_enable(self):
        resource_path = os.path.realpath(os.path.join(TEST_DIRNAME, "..", "resources", "module_rendering", "example"))
        graph_manager = TerraformGraphManager('m', ['m'])
        local_graph, tf_def = graph_manager.build_graph_from_source_directory(resource_path, render_variables=True)
        module_vertices = list(filter(lambda v: v.block_type == BlockType.MODULE, local_graph.vertices))
        existing = set()
        self.assertEqual(6, len(local_graph.edges))
        for e in local_graph.edges:
            if e in existing:
                self.fail("No 2 edges should be aimed at the same vertex in this example")
            else:
                existing.add(e)
        count = 0
        found = 0
        for v in module_vertices:
            if v.name == 'second-mock':
                found += 1
                if v.attributes['input'] == ['aws_s3_bucket.some-bucket.arn']:
                    count += 1
        self.assertEqual(found, count, f"Expected all instances to have the same value, found {found} instances but only {count} correct values")

    def test_type_default_values(self):
        self.assertEqual(TerraformVariableRenderer.get_default_placeholder_value('map'), {})
        self.assertEqual(TerraformVariableRenderer.get_default_placeholder_value('${map}'), {})
        self.assertEqual(TerraformVariableRenderer.get_default_placeholder_value('map(string)'), {})
        self.assertEqual(TerraformVariableRenderer.get_default_placeholder_value('${map(string)}'), {})
        self.assertEqual(TerraformVariableRenderer.get_default_placeholder_value('list'), [])
        self.assertEqual(TerraformVariableRenderer.get_default_placeholder_value('list(string)'), [])
        self.assertEqual(TerraformVariableRenderer.get_default_placeholder_value('${list}'), [])
        self.assertEqual(TerraformVariableRenderer.get_default_placeholder_value('${list(string)}'), [])
        self.assertIsNone(TerraformVariableRenderer.get_default_placeholder_value('number'))
        self.assertIsNone(TerraformVariableRenderer.get_default_placeholder_value('${number}'))
        self.assertIsNone(TerraformVariableRenderer.get_default_placeholder_value(None))
        self.assertIsNone(TerraformVariableRenderer.get_default_placeholder_value(123))

    def test_tfvar_rendering_module_vars(self):
        resource_path = os.path.join(TEST_DIRNAME, "test_resources", "tfvar_module_variables")
        graph_manager = TerraformGraphManager('m', ['m'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(resource_path, render_variables=True)
        resources_vertex = list(filter(lambda v: v.block_type == BlockType.RESOURCE, local_graph.vertices))
        assert resources_vertex[0].attributes.get('name') == ['airpods']

    def test_dynamic_blocks_with_list(self):
        resource_paths = [
            os.path.join(TEST_DIRNAME, "test_resources", "dynamic_blocks_resource"),
            os.path.join(TEST_DIRNAME, "test_resources", "dynamic_blocks_variable_rendering"),
            os.path.join(TEST_DIRNAME, "test_resources", "dynamic_blocks_tfvars"),

        ]
        for path in resource_paths:
            graph_manager = TerraformGraphManager('m', ['m'])
            local_graph, _ = graph_manager.build_graph_from_source_directory(path, render_variables=True)
            resources_vertex = list(filter(lambda v: v.block_type == BlockType.RESOURCE, local_graph.vertices))
            assert len(resources_vertex[0].attributes.get('ingress')) == 2
            assert len(resources_vertex[0].attributes.get('egress')) == 2
            assert resources_vertex[0].attributes.get('ingress') == \
                   [{'cidr_blocks': ['0.0.0.0/0'], 'from_port': 80, 'protocol': 'tcp', 'to_port': 80},
                    {'cidr_blocks': ['0.0.0.0/0'], 'from_port': 443, 'protocol': 'tcp', 'to_port': 443}]
            assert resources_vertex[0].attributes.get('egress') == \
                   [{'cidr_blocks': ['0.0.0.0/0'], 'from_port': 443, 'protocol': 'tcp', 'to_port': 443},
                    {'cidr_blocks': ['0.0.0.0/0'], 'from_port': 1433, 'protocol': 'tcp', 'to_port': 1433}]

    def test_dynamic_blocks_with_map(self):
        resource_paths = [
            os.path.join(TEST_DIRNAME, "test_resources", "dynamic_blocks_map"),
            os.path.join(TEST_DIRNAME, "test_resources", "dynamic_blocks_map_brackets"),
        ]
        for path in resource_paths:
            graph_manager = TerraformGraphManager('m', ['m'])
            local_graph, _ = graph_manager.build_graph_from_source_directory(path, render_variables=True)
            resources_vertex = list(filter(lambda v: v.block_type == BlockType.RESOURCE, local_graph.vertices))
            assert len(resources_vertex[0].attributes.get('ingress')) == 2
            assert resources_vertex[0].attributes.get('ingress') == \
                   [{'action': 'allow', 'cidr_block': '10.0.0.1/32', 'from_port': 22, 'protocol': 'tcp', 'rule_no': 1,
                     'to_port': 22},
                    {'action': 'allow', 'cidr_block': '10.0.0.2/32', 'from_port': 22, 'protocol': 'tcp', 'rule_no': 2,
                     'to_port': 22}]

    def test_dynamic_blocks_with_nesting_attributes(self):
        root_folder = os.path.join(TEST_DIRNAME, "test_resources", "dynamic_block_nesting_attribute")
        graph_manager = TerraformGraphManager('m', ['m'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(root_folder, render_variables=True)

        # Test dynamic blocks with nesting attributes
        resource_vertex = list(filter(lambda v: v.block_type == BlockType.RESOURCE, local_graph.vertices))[0]

        assert resource_vertex.attributes.get('server_side_encryption_configuration') == [{'rule': {
            'apply_server_side_encryption_by_default': {'kms_master_key_id': 'testkey1', 'sse_algorithm': 'aws:kms'}}},
            {'rule': {'apply_server_side_encryption_by_default': {'kms_master_key_id': 'testkey2',
                                                                  'sse_algorithm': 'aws:notkms'}}}]

    def test_extract_dynamic_value_in_map(self):
        self.assertEqual(TerraformVariableRenderer.extract_dynamic_value_in_map('value.value1.value2'), 'value2')
        self.assertEqual(TerraformVariableRenderer.extract_dynamic_value_in_map('value.value1["value2"]'), 'value2')

    def test_dynamic_blocks_breadcrumbs(self):
        root_folder = os.path.join(TEST_DIRNAME, "test_resources", "dynamic_blocks_variable_rendering")
        graph_manager = TerraformGraphManager('m', ['m'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(root_folder, render_variables=True)
        definitions, breadcrumbs = convert_graph_vertices_to_tf_definitions(
            local_graph.vertices,
            root_folder,
        )
        # Test multiple dynamic blocks
        assert 'ingress.from_port' in breadcrumbs['/main.tf']['aws_security_group.list_example']
        assert 'ingress.to_port' in breadcrumbs['/main.tf']['aws_security_group.list_example']
        assert 'egress.to_port' in breadcrumbs['/main.tf']['aws_security_group.list_example']
        assert 'egress.to_port' in breadcrumbs['/main.tf']['aws_security_group.list_example']

        # Test single dynamic block
        assert 'ingress.from_port' in breadcrumbs['/main.tf']['aws_security_group.single_dynamic_example']
        assert 'ingress.to_port' in breadcrumbs['/main.tf']['aws_security_group.single_dynamic_example']

    def test_nested_dynamic_blocks_breadcrumbs(self):
        root_folder = os.path.join(TEST_DIRNAME, "test_resources", "dynamic_blocks_with_nested")
        graph_manager = TerraformGraphManager('m', ['m'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(root_folder, render_variables=True)
        definitions, breadcrumbs = convert_graph_vertices_to_tf_definitions(
            local_graph.vertices,
            root_folder,
        )
        # Test multiple dynamic blocks
        assert 'required_resource_access.resource_app_id' in breadcrumbs['/main.tf']['azuread_application.bootstrap']
        assert 'required_resource_access.resource_access.id' in breadcrumbs['/main.tf']['azuread_application.bootstrap']
        assert 'required_resource_access.resource_access.type' in breadcrumbs['/main.tf']['azuread_application.bootstrap']

    def test_list_entry_rendering_module_vars(self):
        # given
        resource_path = Path(TEST_DIRNAME) / "test_resources/list_entry_module_var"
        graph_manager = TerraformGraphManager(NetworkxConnector())

        # when
        local_graph, _ = graph_manager.build_graph_from_source_directory(str(resource_path), render_variables=True)

        # then
        resource_vertex = next(v for v in local_graph.vertices if v.id == 'aws_security_group.sg')

        self.assertEqual(
            resource_vertex.config["aws_security_group"]["sg"]["ingress"][0]["cidr_blocks"][0],
            ["0.0.0.0/0"],
        )
        self.assertCountEqual(
            resource_vertex.config["aws_security_group"]["sg"]["egress"][0]["cidr_blocks"][0],
            ["10.0.0.0/16", "0.0.0.0/0"],
        )

    @mock.patch.dict(os.environ, {"CHECKOV_RENDER_DYNAMIC_MODULES": "False"})
    def test_dynamic_with_env_var_false(self):
        graph_manager = TerraformGraphManager('m', ['m'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(os.path.join(TEST_DIRNAME, "test_resources", "dynamic_blocks_resource"), render_variables=True)
        resources_vertex = list(filter(lambda v: v.block_type == BlockType.RESOURCE, local_graph.vertices))
        assert not resources_vertex[0].attributes.get('ingress')
        assert not resources_vertex[0].attributes.get('egress')

    def test_dynamic_blocks_with_nested_map(self):
        resource_paths = [
            os.path.join(TEST_DIRNAME, 'test_resources', 'dynamic_blocks_with_nested'),
        ]
        for path in resource_paths:
            graph_manager = TerraformGraphManager('m', ['m'])
            local_graph, _ = graph_manager.build_graph_from_source_directory(path, render_variables=True)
            resources_vertex = list(filter(lambda v: v.block_type == BlockType.RESOURCE, local_graph.vertices))
            assert len(resources_vertex[0].attributes.get('required_resource_access')) == 2
            assert resources_vertex[0].attributes.get('required_resource_access') == \
                   {'resource_app_id': '00000003-0000-0000-c000-000000000000',
                    'resource_access': {'id': '7ab1d382-f21e-4acd-a863-ba3e13f7da61', 'type': 'Role'}}

    def test_dynamic_example_for_security_rule(self):
        graph_manager = TerraformGraphManager('m', ['m'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(os.path.join(TEST_DIRNAME, "test_resources", "dynamic_block_map_example"), render_variables=True)
        resources_vertex = list(filter(lambda v: v.block_type == BlockType.RESOURCE, local_graph.vertices))
        assert resources_vertex[0].attributes.get('security_rule') == [
            {'access': 'Allow', 'destination_address_prefix': '*', 'destination_port_range': 80, 'direction': 'Inbound', 'name': 'AllowHttpIn', 'priority': 100, 'protocol': 'Tcp', 'source_address_prefix': '*', 'source_port_range': '*'},
            {'access': 'Allow', 'destination_address_prefix': '*', 'destination_port_range': 443, 'direction': 'Inbound', 'name': 'AllowHttpsIn', 'priority': 110, 'protocol': 'Tcp', 'source_address_prefix': '*', 'source_port_range': '*'},
            {'access': 'Allow', 'destination_address_prefix': '*', 'destination_port_range': 3389, 'direction': 'Inbound', 'name': 'AllowRdpIn', 'priority': 120, 'protocol': 'Tcp', 'source_address_prefix': '*', 'source_port_range': '*'},
            {'access': 'Allow', 'destination_address_prefix': '*', 'destination_port_range': '*', 'direction': 'Inbound', 'name': 'AllowIcmpIn', 'priority': 130, 'protocol': 'Icmp', 'source_address_prefix': '*', 'source_port_range': '*'}]
        assert resources_vertex[1].attributes.get('security_rule') == [
            {'access': 'Deny', 'destination_address_prefix': '*', 'destination_port_range': 80, 'direction': 'Inbound', 'name': 'DenyHttpIn', 'priority': 100, 'protocol': 'Tcp', 'source_address_prefix': '*', 'source_port_range': '*'},
            {'access': 'Allow', 'destination_address_prefix': '*', 'destination_port_range': 443, 'direction': 'Inbound', 'name': 'AllowHttpsIn', 'priority': 110, 'protocol': 'Tcp', 'source_address_prefix': '35.181.123.80/32', 'source_port_range': '*'},
            {'access': 'Deny', 'destination_address_prefix': '*', 'destination_port_range': 3389, 'direction': 'Inbound', 'name': 'DenyRdpIn', 'priority': 120, 'protocol': 'Tcp', 'source_address_prefix': '*', 'source_port_range': '*'},
            {'access': 'Deny', 'destination_address_prefix': '*', 'destination_port_range': '*', 'direction': 'Inbound', 'name': 'DenyIcmpIn', 'priority': 130, 'protocol': 'Icmp', 'source_address_prefix': '*', 'source_port_range': '*'}]

    def test_dynamic_blocks_with_nested_lookup(self):
        resource_paths = [
            os.path.join(TEST_DIRNAME, 'test_resources', 'dynamic_nested_with_lookup_foreach'),
        ]
        for path in resource_paths:
            start_time = time.time()
            graph_manager = TerraformGraphManager('m', ['m'])
            local_graph, _ = graph_manager.build_graph_from_source_directory(path, render_variables=True)
            end_time = time.time()
            assert end_time - start_time < 1
            resources_vertex = list(filter(lambda v: v.block_type == BlockType.RESOURCE and v.has_dynamic_block, local_graph.vertices))
            assert resources_vertex[0].attributes['stage'] == [
                {'name': 'Source',
                 'action': {'category': 'Source', 'configuration': {'BranchName': 'master', 'PollForSourceChanges': 'false', 'RepositoryName': 'cron-poll'}, 'input_artifacts': [], 'name': 'Source', 'output_artifacts': ['SourceArtifact'], 'owner': 'AWS', 'provider': 'CodeCommit', 'region': '', 'role_arn': 'null', 'run_order': 1, 'version': '1'}},
                {'name': 'Build',
                 'action': {'category': 'Build', 'configuration': {'ProjectName': 'cron-poll'}, 'input_artifacts': ['SourceArtifact'], 'name': 'Build', 'output_artifacts': ['BuildArtifact'], 'owner': 'AWS', 'provider': 'CodeBuild', 'region': '', 'role_arn': 'null', 'run_order': 2, 'version': '1'}},
                {'name': 'Deploy',
                 'action': {'category': 'Deploy', 'configuration': {'ClusterName': 'test', 'ServiceName': 'cron-poll'}, 'input_artifacts': ['BuildArtifact'], 'name': 'Deploy', 'output_artifacts': [], 'owner': 'AWS', 'provider': 'ECS', 'region': '', 'role_arn': 'null', 'run_order': 4, 'version': '1'}}
            ]

    def test_dynamic_blocks_null_lookup(self):
        graph_manager = TerraformGraphManager('m', ['m'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(
            os.path.join(TEST_DIRNAME, "test_resources", "dynamic_blocks_null_lookup"), render_variables=True)
        resources_vertex = list(filter(lambda v: v.block_type == BlockType.RESOURCE, local_graph.vertices))
        assert len(resources_vertex[0].attributes.get('ingress')) == 2
        assert resources_vertex[0].attributes.get('ingress')[0].get('ipv6_cidr_blocks') == 'null'
        assert resources_vertex[0].attributes.get('ingress')[0].get('self') == 'false'
        assert resources_vertex[0].attributes.get('ingress')[0].get('cidr_blocks') == ['10.248.180.0/23', '10.248.186.0/23']

    def test_dynamic_with_conditional_expression(self):
        graph_manager = TerraformGraphManager('m', ['m'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(
            os.path.join(TEST_DIRNAME, "test_resources", "dynamic_with_conditional_expression"), render_variables=True)
        resources_vertex = list(filter(lambda v: v.block_type == BlockType.RESOURCE, local_graph.vertices))
        assert resources_vertex[0].attributes.get('identity').get('identity_ids') == 'null'
        assert resources_vertex[0].attributes.get('identity').get('type') == 'SystemAssigned'

    def test_lookup_from_var(self):
        graph_manager = TerraformGraphManager('m', ['m'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(
            os.path.join(TEST_DIRNAME, "test_resources", "lookup_from_var"), render_variables=True)
        resources_vertex = list(filter(lambda v: v.block_type == BlockType.RESOURCE, local_graph.vertices))
        assert resources_vertex[0].attributes.get('protocol')[0] == 'http'
        assert resources_vertex[0].attributes.get('endpoint')[0] == 'http://www.example.com'

    def test_skip_rendering_unsupported_values(self):
        # given
        resource_path = Path(TEST_DIRNAME) / "test_resources/skip_renderer"

        # when
        graph_manager = TerraformGraphManager('m', ['m'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(str(resource_path), render_variables=True)

        # then
        local_b = next(vertex for vertex in local_graph.vertices if vertex.block_type == BlockType.LOCALS and vertex.name == "b")
        assert local_b.attributes["b"] == ["..."]  # not Ellipsis object

    def test_default_map_value(self):
        # given
        resource_path = Path(TEST_DIRNAME) / "test_resources/default_map_value"

        # when
        graph_manager = TerraformGraphManager('m', ['m'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(str(resource_path), render_variables=True)

        # then
        key_vault = next(vertex for vertex in local_graph.vertices if vertex.block_type == BlockType.RESOURCE and vertex.name == "azurerm_key_vault.this")
        assert key_vault.attributes["network_acls"] == {
            "bypass": "AzureServices",
            "default_action": "Deny",
            "ip_rules": [],
            "virtual_network_subnet_ids": []
        }

    def test_provider_alias(self):
        # given
        resource_path = Path(TEST_DIRNAME) / "test_resources/provider_alias"

        # when
        graph_manager = TerraformGraphManager('m', ['m'])
        local_graph, _ = graph_manager.build_graph_from_source_directory(str(resource_path), render_variables=True)

        # then
        provider = next(vertex for vertex in local_graph.vertices if vertex.block_type == BlockType.PROVIDER and vertex.name == "aws")
        assert provider.config["aws"]["default_tags"] == [{"tags": [{"test": "Test"}]}]

        provider_alias = next(vertex for vertex in local_graph.vertices if vertex.block_type == BlockType.PROVIDER and vertex.name == "aws.test")
        assert provider_alias.config["aws"]["default_tags"] == [{"tags": [{"test": "Test"}]}]
