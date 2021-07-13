import os
from unittest import TestCase

from checkov.cloudformation.graph_manager import CloudformationGraphManager
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestCloudformationGraphManager(TestCase):
    def test_build_graph_from_source_directory(self):
        root_dir = os.path.realpath(os.path.join(TEST_DIRNAME, "./runner/resources"))
        graph_manager = CloudformationGraphManager(db_connector=NetworkxConnector())
        local_graph, definitions = graph_manager.build_graph_from_source_directory(root_dir)

        expected_resources_by_file = {
            "./tags.yaml": [
                "AWS::S3::Bucket.DataBucket",
                "AWS::S3::Bucket.NoTags",
                "AWS::EKS::Nodegroup.EKSClusterNodegroup",
                "AWS::AutoScaling::AutoScalingGroup.TerraformServerAutoScalingGroup"],
            "./cfn_newline_at_end.yaml": [
                "AWS::RDS::DBInstance.MyDB",
                "AWS::S3::Bucket.MyBucket"],
            "./success.json": [
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
        self.assertEqual(6, len(local_graph.vertices_by_block_type["AWS::S3::Bucket"]))
        self.assertEqual(1, len(local_graph.vertices_by_block_type["AWS::EKS::Nodegroup"]))
        self.assertEqual(1, len(local_graph.vertices_by_block_type["AWS::AutoScaling::AutoScalingGroup"]))
        self.assertEqual(1, len(local_graph.vertices_by_block_type["AWS::RDS::DBInstance"]))

        for v in local_graph.vertices:
            self.assertIn(v.name, expected_resources_by_file[v.path])

    def test_build_graph_from_definitions(self):
        self.fail()
