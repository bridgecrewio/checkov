import os
import unittest
import warnings

from checkov.terraform import checks
from .test_yaml_policies import load_yaml_data, get_policy_results


class TestYamlConnectedNodes(unittest.TestCase):
    def setUp(self) -> None:
        os.environ['UNIQUE_TAG'] = ''
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    def test_S3BucketEncryption_connected_node(self):
        report = self.get_report("S3BucketEncryption")
        assert report.failed_checks[0].connected_node is None
        assert report.failed_checks[1].connected_node is None
        assert report.failed_checks[2].connected_node['file_path'] == '/main.tf'
        assert report.failed_checks[2].connected_node['resource'] == 'aws_s3_bucket_server_side_encryption_configuration.bad_sse_1'
        assert report.failed_checks[2].connected_node['file_line_range'] == [135, 144]
        assert report.failed_checks[3].connected_node['file_path'] == '/main.tf'
        assert report.failed_checks[3].connected_node['resource'] == 'aws_s3_bucket_server_side_encryption_configuration.bad_sse_2'
        assert report.failed_checks[3].connected_node['file_line_range'] == [146, 154]
        assert report.failed_checks[4].connected_node is None
        assert report.failed_checks[5].connected_node['file_path'] == '/main.tf'
        assert report.failed_checks[5].connected_node['resource'] == 'aws_s3_bucket_server_side_encryption_configuration.bad_sse_3'
        assert report.failed_checks[5].connected_node['file_line_range'] == [156, 167]

        assert report.passed_checks[0].connected_node is None
        assert report.passed_checks[1].connected_node is None
        assert report.passed_checks[2].connected_node is None
        assert report.passed_checks[3].connected_node['file_path'] == '/main.tf'
        assert report.passed_checks[3].connected_node['resource'] == 'aws_s3_bucket_server_side_encryption_configuration.good_sse_1'
        assert report.passed_checks[3].connected_node['file_line_range'] == [100, 109]
        assert report.passed_checks[4].connected_node['file_path'] == '/main.tf'
        assert report.passed_checks[4].connected_node['resource'] == 'aws_s3_bucket_server_side_encryption_configuration.good_sse_2'
        assert report.passed_checks[4].connected_node['file_line_range'] == [111, 120]
        assert report.passed_checks[5].connected_node['file_path'] == '/main.tf'
        assert report.passed_checks[5].connected_node['resource'] == 'aws_s3_bucket_server_side_encryption_configuration.good_sse_3'
        assert report.passed_checks[5].connected_node['file_line_range'] == [122, 133]


    def test_S3BucketLogging_connected_node(self):
        report = self.get_report("S3BucketLogging")
        assert report.failed_checks[0].connected_node is None

        assert report.passed_checks[0].connected_node is None
        assert report.passed_checks[1].connected_node['file_path'] == '/main.tf'
        assert report.passed_checks[1].connected_node['resource'] == 'aws_s3_bucket_logging.example'
        assert report.passed_checks[1].connected_node['file_line_range'] == [14, 19]

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
                return get_policy_results(dir_path, policy)
