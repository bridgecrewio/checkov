import os
from parameterized import parameterized_class

from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))

@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestEqualsIgnoreCaseSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestEqualsIgnoreCaseSolver, self).setUp()

    def test_equals_ignore_case_solver_wildcard(self):
        root_folder = '../../../resources/encryption_test'
        check_id = "EncryptedResources"
        should_pass = ['aws_rds_cluster.rds_cluster_encrypted', 'aws_s3_bucket.encrypted_bucket',
                       'aws_neptune_cluster.encrypted_neptune']
        should_fail = ['aws_rds_cluster.rds_cluster_unencrypted', 'aws_s3_bucket.unencrypted_bucket',
                       'aws_neptune_cluster.unencrypted_neptune']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        super(TestEqualsIgnoreCaseSolver, self).run_test(root_folder=root_folder, expected_results=expected_results,
                                                         check_id=check_id)

    def test_equals_ignore_case_solver_boolean(self):
        root_folder = '../../../resources/boolean_test'
        check_id = "BooleanString"
        should_pass = ['azurerm_storage_account.fail1', 'azurerm_storage_account.fail2',
                       'azurerm_storage_account.fail3']
        should_fail = ['azurerm_storage_account.pass1', 'azurerm_storage_account.pass2']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        super(TestEqualsIgnoreCaseSolver, self).run_test(root_folder=root_folder, expected_results=expected_results,
                                                         check_id=check_id)
