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
        local_graph, definitions = graph_manager.build_graph_from_source_directory(root_dir, render_variables=False,
                                                                                   excluded_paths=["skip.*", "double_state.*"])

        expected_resources_by_file = {
            os.path.join(root_dir, "no_properties.yaml"): [
                "AWS::Serverless::Function.NoPropertiesYaml"
            ],
            os.path.join(root_dir, "no_properties.json"): [
                "AWS::Serverless::Function.NoPropertiesJson"
            ],
            os.path.join(root_dir, "tags.yaml"): [
                "AWS::S3::Bucket.DataBucket",
                "AWS::S3::Bucket.NoTags",
                "AWS::EKS::Nodegroup.EKSClusterNodegroup",
                "AWS::AutoScaling::AutoScalingGroup.TerraformServerAutoScalingGroup",
            ],
            os.path.join(root_dir, "cfn_newline_at_end.yaml"): [
                "AWS::RDS::DBInstance.MyDB",
                "AWS::S3::Bucket.MyBucket",
            ],
            os.path.join(root_dir, "success.json"): [
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
            os.path.join(root_dir, "fail.yaml"): [
                "AWS::SQS::Queue.UnencryptedQueue",
            ],
            os.path.join(root_dir, "graph.yaml"): [
                "AWS::AppSync::GraphQLApi.GoodAppSyncGraphQLApi",
                "AWS::WAFv2::WebACL.GoodWAFv2WebACL",
                "AWS::WAFv2::WebACLAssociation.WebACLAssociation",
                "AWS::AppSync::GraphQLApi.NoWAFAppSyncGraphQLApi"
            ],
            os.path.join(root_dir, "suppress_graph_check.yaml"): [
                "AWS::AppSync::GraphQLApi.CommentSuppress",
                "AWS::AppSync::GraphQLApi.MetadataSuppress"
            ]
        }
        self.assertEqual(49, len(local_graph.vertices))
        self.assertEqual(29, len(local_graph.vertices_by_block_type[BlockType.RESOURCE]))
        self.assertEqual(9, len(local_graph.vertices_by_block_type[BlockType.PARAMETERS]))
        self.assertEqual(6, len(local_graph.vertices_by_block_type[BlockType.OUTPUTS]))
        self.assertEqual(4, len(local_graph.vertices_by_block_type[BlockType.CONDITIONS]))
        self.assertEqual(1, len(local_graph.vertices_by_block_type[BlockType.MAPPINGS]))

        for v in local_graph.vertices:
            if v.block_type == BlockType.RESOURCE:
                self.assertIn(v.name, expected_resources_by_file[v.path])

        sqs_queue_vertex = local_graph.vertices[local_graph.vertices_block_name_map[BlockType.RESOURCE]["AWS::SQS::Queue.acmeCWSQueue"][0]]
        self.assertDictEqual({'Fn::Join': ['', [{'Ref': 'ResourceNamePrefix', '__startline__': 650, '__endline__': 652}, '-acmecws']], '__startline__': 646, '__endline__': 656}, sqs_queue_vertex.attributes["QueueName"])

    def test_build_graph_from_source_directory_with_rendering(self):
        root_dir = os.path.realpath(os.path.join(TEST_DIRNAME, "./runner/resources"))
        graph_manager = CloudformationGraphManager(db_connector=NetworkxConnector())
        local_graph, definitions = graph_manager.build_graph_from_source_directory(root_dir, render_variables=True)

        sqs_queue_vertex = local_graph.vertices[local_graph.vertices_block_name_map[BlockType.RESOURCE]["AWS::SQS::Queue.acmeCWSQueue"][0]]
        expected_node = {'Fn::Join': ['', ['acme', '-acmecws']], '__startline__': 646, '__endline__': 656}
        self.assertDictEqual(expected_node, sqs_queue_vertex.config["QueueName"])
        found = False
        for d in definitions:
            if 'resources/success.json' in d:
                found = True
                node = definitions[d]['Resources']['acmeCWSQueue']['Properties']['QueueName']
                self.assertDictEqual(expected_node, node)
        self.assertTrue(found, 'Did not find the wanted node, for acmeCWSQueue')

    def test_build_graph_from_definitions(self):
        relative_file_path = "./checks/resource/aws/example_APIGatewayXray/APIGatewayXray-PASSED.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_manager = CloudformationGraphManager(db_connector=NetworkxConnector())
        local_graph = graph_manager.build_graph_from_definitions(definitions)
        self.assertEqual(1, len(local_graph.vertices))
        resource_vertex = local_graph.vertices[0]
        self.assertEqual("AWS::ApiGateway::Stage.Enabled", resource_vertex.name)
        self.assertEqual("AWS::ApiGateway::Stage.Enabled", resource_vertex.id)
        self.assertEqual(BlockType.RESOURCE, resource_vertex.block_type)
        self.assertEqual("CloudFormation", resource_vertex.source)
        self.assertDictEqual(definitions[relative_file_path]["Resources"]["Enabled"]["Properties"], resource_vertex.attributes)
