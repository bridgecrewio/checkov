import os
from unittest import TestCase

from checkov.cloudformation.graph_builder.graph_components.block_types import BlockType
from checkov.cloudformation.graph_builder.local_graph import CloudformationLocalGraph
from checkov.cloudformation.parser import parse

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestLocalGraph(TestCase):
    def test_build_graph_with_single_resource(self):
        relative_file_path = "../checks/resource/aws/example_APIGatewayXray/APIGatewayXray-PASSED.yaml"
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
        self.assertEqual("TestDeployment", resource_vertex.attributes.get("DeploymentId"))


