import os

from tests.graph.terraform.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestNotEqualsSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestNotEqualsSolver, self).setUp()

    def test_not_equals_solver_simple(self):
        root_folder = '../../../resources/public_security_groups'
        check_id = "PublicDBSG"
        should_fail = ['aws_db_security_group.aws_db_security_group_private']
        should_pass = ['aws_db_security_group.aws_db_security_group_public']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_not_equals_solver_wildcard(self):
        root_folder = '../../../resources/security_group_multiple_rules'
        check_id = "SGPorts"
        should_pass = ['aws_security_group.sg1', 'aws_security_group.sg2']
        should_fail = []
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)
