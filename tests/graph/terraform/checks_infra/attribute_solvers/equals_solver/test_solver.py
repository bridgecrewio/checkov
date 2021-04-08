import os

from tests.graph.terraform.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestEqualsSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestEqualsSolver, self).setUp()

    def test_equals_solver_simple(self):
        root_folder = '../../../resources/public_security_groups'
        check_id = "PublicDBSG"
        should_pass = ['aws_db_security_group.aws_db_security_group_private']
        should_fail = ['aws_db_security_group.aws_db_security_group_public']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_equals_solver_wildcard(self):
        root_folder = '../../../resources/encryption_test'
        check_id = "EncryptedResources"
        should_pass = ['aws_rds_cluster.rds_cluster_encrypted', 'aws_s3_bucket.encrypted_bucket', 'aws_neptune_cluster.encrypted_neptune']
        should_fail = ['aws_rds_cluster.rds_cluster_unencrypted', 'aws_s3_bucket.unencrypted_bucket', 'aws_neptune_cluster.unencrypted_neptune']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        super(TestEqualsSolver, self).run_test(root_folder=root_folder, expected_results=expected_results,
                                               check_id=check_id)