import os

from parameterized import parameterized_class

from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestCIDRRangeNotSubsetSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestCIDRRangeNotSubsetSolver, self).setUp()

    def test_cidr_range_not_subset_string_solver(self):
        root_folder = 'resources'
        check_id = "CIDRRangeNotSubsetString"
        should_fail = ['test.pass1', 'test.pass2', 'test.pass3', 'test.pass4']
        should_pass = ['test.fail1', 'test.fail2', 'test.fail3']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_cidr_range_not_subset_string_jsonpath_solver(self):
        root_folder = 'resources'
        check_id = "JsonPathCIDRRangeNotSubsetString"
        should_fail = ['test.pass1', 'test.pass2', 'test.pass3', 'test.pass4']
        should_pass = ['test.fail1', 'test.fail2', 'test.fail3']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_cidr_range_not_subset_list_solver(self):
        root_folder = 'resources'
        check_id = "CIDRRangeNotSubsetList"
        should_fail = ['test.pass1', 'test.pass2', 'test.pass3', 'test.pass4']
        should_pass = ['test.fail1', 'test.fail2', 'test.fail3']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_cidr_range_not_subset_list_jsonpath_solver(self):
        root_folder = 'resources'
        check_id = "JsonPathCIDRRangeNotSubsetList"
        should_fail = ['test.pass1', 'test.pass2', 'test.pass3', 'test.pass4']
        should_pass = ['test.fail1', 'test.fail2', 'test.fail3']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_ipv6_cidr_range_not_subset_list_solver(self):
        root_folder = 'resources'
        check_id = "IPV6CIDRRangeNotSubsetList"
        should_fail = ['test.ipv6_pass1', 'test.ipv6_pass2']
        should_pass = ['test.ipv6_fail1', 'test.ipv6_fail2', 'test.pass1', 'test.pass2', 'test.pass3', 'test.pass4',
                       'test.fail1', 'test.fail2', 'test.fail3']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_ipv6_cidr_range_not_subset_list_jsonpath_solver(self):
        root_folder = 'resources'
        check_id = "JsonPathIPV6CIDRRangeNotSubsetList"
        should_fail = ['test.ipv6_pass1', 'test.ipv6_pass2']
        should_pass = ['test.ipv6_fail1', 'test.ipv6_fail2', 'test.pass1', 'test.pass2', 'test.pass3', 'test.pass4',
                       'test.fail1', 'test.fail2', 'test.fail3']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)
