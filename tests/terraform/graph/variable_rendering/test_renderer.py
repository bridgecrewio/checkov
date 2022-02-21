import os
from unittest.case import TestCase

from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_manager import TerraformGraphManager
from checkov.terraform.graph_builder.variable_rendering.renderer import TerraformVariableRenderer
from tests.terraform.graph.variable_rendering.expected_data import (
    expected_terragoat_local_resource_prefix,
    expected_terragoat_db_instance,
    expected_eks,
    expected_provider,
)

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestRenderer(TestCase):
    def setUp(self) -> None:
        os.environ['UNIQUE_TAG'] = ''
        os.environ['RENDER_ASYNC_MAX_WORKERS'] = '50'
        os.environ['RENDER_VARIABLES_ASYNC'] = 'False'

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
