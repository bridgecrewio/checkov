from parameterized import parameterized_class

from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver
import os
TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestNotQuery(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestNotQuery, self).setUp()

    def test_buckets_with_option_env_tag(self):
        root_folder = '../../../resources/s3_bucket_2'
        check_id = "NotTest"
        should_fail = ['aws_s3_bucket.private']
        should_pass = ['aws_s3_bucket.public', 'aws_s3_bucket.non_tag']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_simple_not_with_list(self):
        root_folder = '../../../resources/s3_bucket_2'
        check_id = "NotWithNestedList"
        should_fail = ['aws_s3_bucket.private']
        should_pass = ['aws_s3_bucket.public', 'aws_s3_bucket.non_tag']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_simple_not_with_dict(self):
        root_folder = '../../../resources/s3_bucket_2'
        check_id = "NotWithNestedDict"
        should_fail = ['aws_s3_bucket.private']
        should_pass = ['aws_s3_bucket.public', 'aws_s3_bucket.non_tag']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)
