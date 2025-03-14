import os
import unittest
import warnings
from unittest import mock

import pytest

from checkov.terraform import checks
from tests.graph_utils.utils import GRAPH_FRAMEWORKS
from .test_yaml_policies import load_yaml_data, get_policy_results


class TestYamlConnectedNodes(unittest.TestCase):
    def setUp(self) -> None:
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    def test_S3BucketEncryption_connected_node(self):
        report = get_report("S3BucketEncryption")
        assert report.failed_checks[0].connected_node is None
        assert report.failed_checks[1].connected_node['file_path'] == '/main.tf'
        assert report.failed_checks[1].connected_node['resource'] == 'aws_s3_bucket_server_side_encryption_configuration.bad_sse_1'
        assert report.failed_checks[1].connected_node['file_line_range'] == [163, 172]
        assert report.failed_checks[2].connected_node['file_path'] == '/main.tf'
        assert report.failed_checks[2].connected_node['resource'] == 'aws_s3_bucket_server_side_encryption_configuration.bad_sse_2'
        assert report.failed_checks[2].connected_node['file_line_range'] == [174, 182]
        assert report.failed_checks[3].connected_node is None
        assert report.failed_checks[4].connected_node['file_path'] == '/main.tf'
        assert report.failed_checks[4].connected_node['resource'] == 'aws_s3_bucket_server_side_encryption_configuration.bad_sse_3'
        assert report.failed_checks[4].connected_node['file_line_range'] == [184, 195]

        assert report.passed_checks[0].connected_node is None
        assert report.passed_checks[1].connected_node is None
        assert report.passed_checks[2].connected_node is None
        assert report.passed_checks[3].connected_node['file_path'] == '/main.tf'
        assert report.passed_checks[3].connected_node['resource'] == 'aws_s3_bucket_server_side_encryption_configuration.good_sse_1'
        assert report.passed_checks[3].connected_node['file_line_range'] == [117, 126]
        assert report.passed_checks[4].connected_node['file_path'] == '/main.tf'
        assert report.passed_checks[4].connected_node['resource'] == 'aws_s3_bucket_server_side_encryption_configuration.good_sse_2'
        assert report.passed_checks[4].connected_node['file_line_range'] == [128, 137]
        assert report.passed_checks[5].connected_node['file_path'] == '/main.tf'
        assert report.passed_checks[5].connected_node['resource'] == 'aws_s3_bucket_server_side_encryption_configuration.good_sse_3'
        assert report.passed_checks[5].connected_node['file_line_range'] == [139, 150]

    def test_S3BucketLogging_connected_node(self):
        report = get_report("S3BucketLogging")
        assert report.failed_checks[0].connected_node is None

        assert report.passed_checks[0].connected_node is None
        assert report.passed_checks[1].connected_node['file_path'] == '/main.tf'
        assert report.passed_checks[1].connected_node['resource'] == 'aws_s3_bucket_logging.example'
        assert report.passed_checks[1].connected_node['file_line_range'] == [14, 19]


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_correct_connected_node_per_check(graph_framework):
    failed_check_id_with_connected_node = 'CKV_AWS_144'
    pass_check_id_with_connected_node = 'CKV_AWS_145'
    pass_check_id_without_connected_node = 'CKV_AWS_20'
    check_ids = [failed_check_id_with_connected_node, pass_check_id_with_connected_node, pass_check_id_without_connected_node]

    report = get_report("connected_nodes", checks_ids=check_ids, graph_framework=graph_framework)
    assert len(report.passed_checks) == 2
    assert len(report.failed_checks) == 1

    assert report.failed_checks[0].connected_node['resource'] == 'aws_s3_bucket_replication_configuration.replication'
    assert report.failed_checks[0].connected_node['file_path'] == '/main.tf'
    assert report.failed_checks[0].connected_node['file_line_range'] == [6, 18]

    passed_with_connection = next((c for c in report.passed_checks if c.check_id == pass_check_id_with_connected_node), None)
    passed_without_connection = next((c for c in report.passed_checks if c.check_id == pass_check_id_without_connected_node), None)

    assert passed_with_connection.connected_node is not None
    assert passed_without_connection.connected_node is None

    assert passed_with_connection.connected_node['resource'] == 'aws_s3_bucket_server_side_encryption_configuration.bad_sse'
    assert passed_with_connection.connected_node['file_path'] == '/main.tf'
    assert passed_with_connection.connected_node['file_line_range'] == [20, 29]


def get_report(dir_name, graph_framework='NETWORKX', checks_ids=None):
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            f"resources/{dir_name}")
    assert os.path.exists(dir_path)
    policy_dir_path = os.path.dirname(checks.__file__)
    assert os.path.exists(policy_dir_path)
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        if checks_ids:
                return get_policy_results(dir_path, check_ids=checks_ids)
        for root, _, f_names in os.walk(policy_dir_path):
            for f_name in f_names:
                if f_name != f"{dir_name}.yaml":
                    continue
                policy = load_yaml_data(f_name, root)
                assert policy is not None
                return get_policy_results(dir_path, check_ids=[policy['metadata']['id']])
