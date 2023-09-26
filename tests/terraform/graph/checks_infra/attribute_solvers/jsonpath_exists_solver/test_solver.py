import os

from parameterized import parameterized_class

from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class([
    {"graph_framework": "NETWORKX"},
    {"graph_framework": "IGRAPH"}
])
class TestJsonpathExistsSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super().setUp()

    def test_jsonpath_exists_solver_simple(self):
        root_folder = '../../../resources/public_security_groups'
        check_id = "PublicDBSG"
        should_pass = ['aws_security_group.aws_security_group_private']
        should_fail = ['aws_db_security_group.aws_db_security_group_public']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_jsonpath_exists_solver_wildcard(self):
        root_folder = '../../../resources/security_group_multiple_rules3'
        check_id = "CkSshPortOpenForAll"
        should_pass = ['aws_security_group.sg1']
        should_fail = ['aws_security_group.sg2', 'aws_security_group.sg3']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_jsonpath_exists_azure_rule(self):
        root_folder = '../../../resources/azure_secure_rule'
        check_id = "AzureSecureRule"
        should_pass = ['azurerm_network_security_group.sg_fail']
        should_fail = ['azurerm_network_security_group.sg_fail2']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_jsonpath_exists_example(self):
        root_folder = './'
        check_id = "example"
        should_pass = ['xyz.pass']
        should_fail = ['xyz.fail']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)
