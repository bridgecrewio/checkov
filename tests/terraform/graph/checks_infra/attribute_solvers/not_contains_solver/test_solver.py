import os

from parameterized import parameterized_class

from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestNotContainsSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestNotContainsSolver, self).setUp()

    def test_public_virtual_machines(self):
        root_folder = '../../../resources/public_virtual_machines'
        check_id = "PublicVMs"
        should_pass = ['aws_default_security_group.default_security_group_closed']
        should_fail = ['aws_default_security_group.default_security_group_open']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_list_cidr_blocks(self):
        root_folder = '../../../resources/security_group_list_cidr_blocks'
        check_id = "PublicSG"
        should_pass = ['aws_security_group.passed_cidr_block', 'aws_security_group.failed_cidr_blocks']
        should_fail = []
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_list_cidr_blocks_specific(self):
        root_folder = '../../../resources/security_group_list_cidr_blocks'
        check_id = "SpecificBlockSG"
        should_pass = ['aws_security_group.failed_cidr_blocks']
        should_fail = ['aws_security_group.passed_cidr_block']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)
