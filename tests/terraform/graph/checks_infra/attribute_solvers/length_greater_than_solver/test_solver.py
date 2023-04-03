import os

from parameterized import parameterized_class

from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class([
   {"graph_framework": "NETWORKX"},
   {"graph_framework": "IGRAPH"}
])
class TestLengthGreaterThan(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestLengthGreaterThan, self).setUp()

    def test_array_length_greater_than(self):
        # this is just a basic check to make sure the operator works
        # we'll check all the other combinations more directly (because coming up with all the policy combos is painful)
        root_folder = '../../../resources/lengths'
        check_id = "ArrayLengthGreaterThan"
        should_pass = ['aws_security_group.sg1']
        should_fail = ['aws_security_group.sg2']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_string_length_greater_than(self):
        # this is just a basic check to make sure the operator works
        # we'll check all the other combinations more directly (because coming up with all the policy combos is painful)
        root_folder = '../../../resources/lengths'
        check_id = "StringLengthGreaterThan"
        should_pass = ['aws_security_group.sg2']
        should_fail = ['aws_security_group.sg1']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_dict_length_greater_than(self):
        # this is just a basic check to make sure the operator works
        # we'll check all the other combinations more directly (because coming up with all the policy combos is painful)
        root_folder = '../../../resources/lengths'
        check_id = "DictLengthGreaterThan"
        should_pass = ['aws_security_group.sg4']
        should_fail = ['aws_security_group.sg3']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)