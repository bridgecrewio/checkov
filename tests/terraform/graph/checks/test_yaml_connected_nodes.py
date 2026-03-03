import os
import unittest
import warnings
from unittest import mock

from checkov.terraform import checks
from .test_yaml_policies import load_yaml_data, get_policy_results


class TestYamlConnectedNodes(unittest.TestCase):
    def setUp(self) -> None:
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    def test_S3BucketEncryption_connected_node(self):
        report = self.get_report("S3BucketEncryption")
        assert report is not None
        failed_connected = self._get_connected_nodes(report.failed_checks)
        passed_connected = self._get_connected_nodes(report.passed_checks)

        assert sorted(failed_connected) == sorted([
            ("/main.tf", "aws_s3_bucket_server_side_encryption_configuration.bad_sse_1", [163, 172]),
            ("/main.tf", "aws_s3_bucket_server_side_encryption_configuration.bad_sse_2", [174, 182]),
            ("/main.tf", "aws_s3_bucket_server_side_encryption_configuration.bad_sse_3", [184, 195]),
        ])

        assert sorted(passed_connected) == sorted([
            ("/main.tf", "aws_s3_bucket_server_side_encryption_configuration.good_sse_1", [117, 126]),
            ("/main.tf", "aws_s3_bucket_server_side_encryption_configuration.good_sse_2", [128, 137]),
            ("/main.tf", "aws_s3_bucket_server_side_encryption_configuration.good_sse_3", [139, 150]),
        ])

    def _get_connected_nodes(self, records):
        return [
            (
                record.connected_node["file_path"],
                record.connected_node["resource"],
                record.connected_node["file_line_range"],
            )
            for record in records
            if record.connected_node is not None
        ]

    def test_S3BucketLogging_connected_node(self):
        report = self.get_report("S3BucketLogging")
        assert report is not None
        failed_connected = self._get_connected_nodes(report.failed_checks)
        passed_connected = self._get_connected_nodes(report.passed_checks)

        assert failed_connected == []
        assert passed_connected == [
            ("/main.tf", "aws_s3_bucket_logging.example", [14, 19]),
        ]

    def get_report(self, dir_name):
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                f"resources/{dir_name}")
        assert os.path.exists(dir_path)
        policy_dir_path = os.path.dirname(checks.__file__)
        assert os.path.exists(policy_dir_path)
        for root, _, f_names in os.walk(policy_dir_path):
            for f_name in f_names:
                if f_name != f"{dir_name}.yaml":
                    continue
                policy = load_yaml_data(f_name, root)
                assert policy is not None
                with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': 'NETWORKX'}):
                    # connected nodes don't exist in igraph, because they are not needed
                    return get_policy_results(dir_path, policy)
