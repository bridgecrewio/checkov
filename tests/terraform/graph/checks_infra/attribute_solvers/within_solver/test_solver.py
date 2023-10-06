import os

from parameterized import parameterized_class

from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestWithinSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestWithinSolver, self).setUp()

    def test_name_starting_with(self):
        root_folder = '../../../resources/public_virtual_machines'
        check_id = "NameWithin"
        should_pass = ['aws_subnet.subnet_public_ip']
        should_fail = ['aws_subnet.subnet_not_public_ip']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_wildcard(self):
        root_folder = '../../../resources/array_test'
        check_id = 'WildcardWithin'
        should_pass = ['aws_xyz.pass1', 'aws_xyz.pass2', 'aws_xyz.pass3']
        # TODO fail1 needs to fail here, but for now we are just skipping the resource, because it's a larger discussion on how to handle wildcard matches.
        should_fail = ['aws_xyz.fail2', 'aws_xyz.fail3']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}
        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_within_unrendered(self):
        root_folder = '../../../resources/variable_rendering/unrendered'
        check_id = "UnrenderedVar"
        should_pass = []
        should_fail = []
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)