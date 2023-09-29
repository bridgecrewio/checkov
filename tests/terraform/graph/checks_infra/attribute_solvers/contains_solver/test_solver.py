import os
from parameterized import parameterized_class

from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestContainsSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestContainsSolver, self).setUp()

    def test_public_virtual_machines(self):
        root_folder = '../../../resources/public_virtual_machines'
        check_id = "PublicVMs"
        should_pass = ['aws_default_security_group.default_security_group_open']
        should_fail = ['aws_default_security_group.default_security_group_closed']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_public_virtual_machines_with_jsonpath(self):
        root_folder = '../../../resources/public_virtual_machines'
        check_id = "PublicVMsWithJsonpath"
        should_pass = ['aws_default_security_group.default_security_group_open']
        should_fail = ['aws_default_security_group.default_security_group_closed']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_list_cidr_blocks(self):
        root_folder = '../../../resources/security_group_list_cidr_blocks'
        check_id = "PublicSG"
        should_pass = []
        should_fail = ['aws_security_group.passed_cidr_block', 'aws_security_group.failed_cidr_blocks']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_list_cidr_blocks_specific(self):
        root_folder = '../../../resources/security_group_list_cidr_blocks'
        check_id = "SpecificBlockSG"
        should_pass = ['aws_security_group.passed_cidr_block']
        should_fail = ['aws_security_group.failed_cidr_blocks']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_contains_dict(self):
        root_folder = '../../../resources/tag_includes'
        check_id = "TagIncludes"
        should_pass = ['aws_instance.some_instance', 'aws_subnet.acme_subnet']
        should_fail = ['aws_s3_bucket.acme_s3_bucket']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_contains_string_list(self):
        root_folder = '../../../resources/security_group_list_cidr_blocks'
        # this tests a specific condition related to wildcard expression evaluation and is not necessarily a full
        # solver test
        check_id = "PublicSGMultipleIngress"
        should_pass = []
        should_fail = ['aws_security_group.passed_multiple_ingress']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_none_network_acl_ips(self):
        root_folder = '../../../resources/none_contains'
        check_id = "NetworkACL"
        should_pass = []
        should_fail = ['azurerm_key_vault.kv']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_variable_dependent_policy(self):
        root_folder = '../../../resources/variable_dependent_policy'
        check_id = "VariableDependentPolicy"
        should_pass = ['aws_s3_bucket_acl.example5']
        should_fail = []
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)