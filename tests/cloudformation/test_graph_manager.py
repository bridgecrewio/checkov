import os
from unittest import TestCase

from checkov.cloudformation.graph_builder.graph_components.block_types import BlockType
from checkov.cloudformation.graph_manager import CloudformationGraphManager
from checkov.cloudformation.parser import parse
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestCloudformationGraphManager(TestCase):
    def test_build_graph_from_source_directory_no_rendering(self):
        root_dir = os.path.realpath(os.path.join(TEST_DIRNAME, "./runner/resources"))
        graph_manager = CloudformationGraphManager(db_connector=NetworkxConnector())
        local_graph, definitions = graph_manager.build_graph_from_source_directory(root_dir, render_variables=False)

        expected_resources_by_file = {
            "/tags.yaml": [
                "AWS::S3::Bucket.DataBucket",
                "AWS::S3::Bucket.NoTags",
                "AWS::EKS::Nodegroup.EKSClusterNodegroup",
                "AWS::AutoScaling::AutoScalingGroup.TerraformServerAutoScalingGroup"],
            "/cfn_newline_at_end.yaml": [
                "AWS::RDS::DBInstance.MyDB",
                "AWS::S3::Bucket.MyBucket"],
            "/success.json": [
                "AWS::S3::Bucket.acmeCWSBucket",
                "AWS::S3::Bucket.acmeCWSBucket2",
                "AWS::S3::BucketPolicy.acmeCWSBucketPolicy",
                "AWS::SNS::Topic.acmeCWSTopic",
                "AWS::SNS::TopicPolicy.acmeCWSTopicPolicy",
                "AWS::CloudTrail::Trail.acmeCWSTrail",
                "AWS::KMS::Key.CloudtrailKMSKey",
                "AWS::KMS::Alias.CloudtrailKMSKeyAlias",
                "AWS::SQS::Queue.acmeCWSQueue",
                "AWS::SQS::QueuePolicy.acmeCWSQueuePolicy",
                "AWS::SNS::Subscription.acmeCWSSubscription",
                "AWS::IAM::Role.acmeCWSSACrossAccountAccessRole",
                "AWS::EKS::Cluster.eksCluster",
                "Custom::acmeSnsCustomResource.acmeSnsCustomResource",
                ],
        }
        self.assertEqual(20, len(local_graph.vertices))
        self.assertEqual(20, len(local_graph.vertices_by_block_type[BlockType.RESOURCE]))

        for v in local_graph.vertices:
            self.assertIn(v.id, expected_resources_by_file[v.path])

        sqs_queue_vertex = local_graph.vertices[local_graph.vertices_block_name_map[BlockType.RESOURCE]["acmeCWSQueue"][0]]
        self.assertDictEqual({'Fn::Join': ['', [{'Ref': 'ResourceNamePrefix', '__startline__': 650, '__endline__': 652}, '-acmecws']], '__startline__': 646, '__endline__': 656}, sqs_queue_vertex.attributes["QueueName"])

    def test_build_graph_from_source_directory_with_rendering(self):
            root_dir = os.path.realpath(os.path.join(TEST_DIRNAME, "./runner/resources"))
            graph_manager = CloudformationGraphManager(db_connector=NetworkxConnector())
            local_graph, definitions = graph_manager.build_graph_from_source_directory(root_dir, render_variables=True)

            sqs_queue_vertex = local_graph.vertices[local_graph.vertices_block_name_map[BlockType.RESOURCE]["acmeCWSQueue"][0]]
            self.assertDictEqual({'Fn::Join': ['', ['acme', '-acmecws']], '__startline__': 646, '__endline__': 656}, sqs_queue_vertex.attributes["QueueName"])

    def test_build_graph_from_definitions(self):
        relative_file_path = "./checks/resource/aws/example_APIGatewayXray/APIGatewayXray-PASSED.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_manager = CloudformationGraphManager(db_connector=NetworkxConnector())
        local_graph = graph_manager.build_graph_from_definitions(definitions)
        self.assertEqual(1, len(local_graph.vertices))
        resource_vertex = local_graph.vertices[0]
        self.assertEqual("MyStage", resource_vertex.name)
        self.assertEqual("AWS::ApiGateway::Stage.MyStage", resource_vertex.id)
        self.assertEqual(BlockType.RESOURCE, resource_vertex.block_type)
        self.assertEqual("CloudFormation", resource_vertex.source)
        self.assertDictEqual(definitions[relative_file_path]["Resources"]["MyStage"]["Properties"], resource_vertex.attributes)
