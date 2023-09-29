import os

from parameterized import parameterized_class

from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestNotExistsSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestNotExistsSolver, self).setUp()

    def test_nested_attribute_doesnt_exists_versioning(self):
        root_folder = '../../../resources/s3_bucket'
        check_id = "VersioningEnabledExists"
        should_pass = []
        should_fail = ['aws_s3_bucket.destination']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_nested_attribute_doesnt_exists_tag(self):
        root_folder = '../../../resources/s3_bucket'
        check_id = "TagEnvironmentExists"
        should_pass = ['aws_s3_bucket.destination']
        should_fail = []
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_nested_attribute_doesnt_exists_policy(self):
        root_folder = 'resources'
        check_id = "SecureTransport"
        should_pass = []
        should_fail = ['aws_s3_bucket_policy.allow_access']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)
