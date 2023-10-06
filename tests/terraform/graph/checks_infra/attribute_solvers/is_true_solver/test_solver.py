import os

from parameterized import parameterized_class

from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestIsTrue(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestIsTrue, self).setUp()

    def test_is_true(self):
        root_folder = '../../../resources/boolean_test'
        check_id = "TrueValue"
        should_pass = ['azurerm_storage_account.fail1', 'azurerm_storage_account.fail2', 'azurerm_storage_account.fail3']
        should_fail = ['azurerm_storage_account.pass1', 'azurerm_storage_account.pass2']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        super(TestIsTrue, self).run_test(root_folder=root_folder, expected_results=expected_results,
                                               check_id=check_id)

    def test_is_false(self):
        root_folder = '../../../resources/lb'
        check_id = "FalseValue"
        should_pass = []
        should_fail = ['aws_lb.lb_bad_1']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        super(TestIsTrue, self).run_test(root_folder=root_folder, expected_results=expected_results,
                                         check_id=check_id)