import os
from unittest import TestCase

from checkov.cloudformation.cfn_utils import create_definitions
from checkov.cloudformation.graph_builder.graph_components.block_types import BlockType
from checkov.cloudformation.graph_builder.graph_components.block_types import CloudformationTemplateSections
from checkov.cloudformation.graph_builder.graph_to_definitions import convert_graph_vertices_to_definitions
from checkov.cloudformation.graph_builder.local_graph import CloudformationLocalGraph
from checkov.cloudformation.parser import parse
from checkov.runner_filter import RunnerFilter

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestLocalGraph(TestCase):
    def test_build_graph_with_single_resource(self):
        relative_file_path = "../../checks/resource/aws/example_APIGatewayXray/APIGatewayXray-PASSED.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        local_graph = CloudformationLocalGraph(definitions)
        local_graph.build_graph(render_variables=False)
        self.assertEqual(1, len(local_graph.vertices))
        resource_vertex = local_graph.vertices[0]
        self.assertEqual("AWS::ApiGateway::Stage.MyStage", resource_vertex.name)
        self.assertEqual("AWS::ApiGateway::Stage.MyStage", resource_vertex.id)
        self.assertEqual(BlockType.RESOURCE, resource_vertex.block_type)
        self.assertEqual("CloudFormation", resource_vertex.source)
        self.assertDictEqual(definitions[relative_file_path]["Resources"]["MyStage"]["Properties"],
                             resource_vertex.attributes)

    def test_build_graph_with_params_outputs(self):
        relative_file_path = "../../checks/resource/aws/example_IAMRoleAllowAssumeFromAccount/example_IAMRoleAllowAssumeFromAccount-PASSED-2.yml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        local_graph = CloudformationLocalGraph(definitions)
        local_graph.build_graph(render_variables=False)
        self.assertEqual(len(local_graph.vertices), 56)
        self.assertEqual(len([v for v in local_graph.vertices if v.block_type == BlockType.CONDITION]), 2)
        self.assertEqual(len([v for v in local_graph.vertices if v.block_type == BlockType.RESOURCE]), 16)
        self.assertEqual(len([v for v in local_graph.vertices if v.block_type == BlockType.PARAMETER]), 30)
        self.assertEqual(len([v for v in local_graph.vertices if v.block_type == BlockType.OUTPUT]), 8)

    def test_vertices_from_local_graph(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, './resources'))
        definitions, _ = create_definitions(root_folder=resources_dir, files=None, runner_filter=RunnerFilter())
        local_graph = CloudformationLocalGraph(definitions)
        local_graph.build_graph(render_variables=False)
        tf_definitions, breadcrumbs = convert_graph_vertices_to_definitions(local_graph.vertices, resources_dir)

        self.assertIsNotNone(tf_definitions)
        self.assertEqual(len(tf_definitions.items()), 2)

        test_yaml_definitions = tf_definitions['/test.yaml'][CloudformationTemplateSections.RESOURCES]
        self.assertEqual(len(test_yaml_definitions.keys()), 2)
        self.assertIn('MyDB', test_yaml_definitions.keys())
        self.assertIn('MySourceQueue', test_yaml_definitions.keys())

        test_json_definitions = tf_definitions['/test.json'][CloudformationTemplateSections.RESOURCES]
        self.assertEqual(len(test_json_definitions.keys()), 2)
        self.assertIn('MyDB', test_json_definitions.keys())
        self.assertIn('MySourceQueue', test_json_definitions.keys())

        self.assertIsNotNone(breadcrumbs)
        self.assertDictEqual(breadcrumbs, {})  # Will be changed when we add breadcrumbs to cfn vertices
