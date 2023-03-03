import os

from parameterized import parameterized_class

from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class([
   {"graph_framework": "NETWORKX"},
   {"graph_framework": "IGRAPH"}
])
class TestRangeIncludesSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestRangeIncludesSolver, self).setUp()

    def test_range_includes_int_solver(self):
        root_folder = 'resources'
        check_id = "RangeIncludesInt"
        should_pass = ['test.pass1', 'test.pass2', 'test.pass3', 'test.pass4', 'test.pass5', 'test.pass6']
        should_fail = ['test.fail1', 'test.fail2', 'test.fail3', 'test.fail4', 'test.fail5', 'test.fail6', 'test.fail7', 'test.fail8']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_range_includes_string_solver(self):
        root_folder = 'resources'
        check_id = "RangeIncludesString"
        should_pass = ['test.pass1', 'test.pass2', 'test.pass3', 'test.pass4', 'test.pass5', 'test.pass6']
        should_fail = ['test.fail1', 'test.fail2', 'test.fail3', 'test.fail4', 'test.fail5', 'test.fail6', 'test.fail7',
                       'test.fail8']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_range_includes_int_jsonpath_solver(self):
        root_folder = 'resources'
        check_id = "JsonPathRangeIncludesInt"
        should_pass = ['test.pass1', 'test.pass2', 'test.pass3', 'test.pass4', 'test.pass5', 'test.pass6']
        should_fail = ['test.fail1', 'test.fail2', 'test.fail3', 'test.fail4', 'test.fail5', 'test.fail6', 'test.fail7', 'test.fail8']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_range_includes_string_jsonpath_solver(self):
        root_folder = 'resources'
        check_id = "JsonPathRangeIncludesString"
        should_pass = ['test.pass1', 'test.pass2', 'test.pass3', 'test.pass4', 'test.pass5', 'test.pass6']
        should_fail = ['test.fail1', 'test.fail2', 'test.fail3', 'test.fail4', 'test.fail5', 'test.fail6', 'test.fail7',
                       'test.fail8']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)
