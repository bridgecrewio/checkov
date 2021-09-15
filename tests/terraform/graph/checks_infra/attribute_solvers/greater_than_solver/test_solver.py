import os

from checkov.common.checks_infra.solvers.attribute_solvers.greater_than_attribute_solver import \
    GreaterThanAttributeSolver
from checkov.common.checks_infra.solvers.attribute_solvers.greater_than_or_equal_attribute_solver import \
    GreaterThanOrEqualAttributeSolver
from checkov.common.checks_infra.solvers.attribute_solvers.less_than_attribute_solver import LessThanAttributeSolver
from checkov.common.checks_infra.solvers.attribute_solvers.less_than_or_equal_attribute_solver import \
    LessThanOrEqualAttributeSolver
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestGreaterThanLessThanSolvers(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestGreaterThanLessThanSolvers, self).setUp()

    def test_greater_than_solver_simple(self):
        # this is just a basic check to make sure the operator works
        # we'll check all the other combinations more directly (because coming up with all the policy combos is painful)
        root_folder = 'resources'
        check_id = "GT"
        should_pass = ['aws_s3_bucket.b2']
        should_fail = ['aws_s3_bucket.b1', 'aws_s3_bucket.b3']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_less_than_solver_simple(self):
        root_folder = 'resources'
        check_id = "LT"
        should_pass = ['aws_s3_bucket.b1']
        should_fail = ['aws_s3_bucket.b2', 'aws_s3_bucket.b3']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_greater_than_or_equal_solver_simple(self):
        # this is just a basic check to make sure the operator works
        # we'll check all the other combinations more directly (because coming up with all the policy combos is painful)
        root_folder = 'resources'
        check_id = "GTE"
        should_pass = ['aws_s3_bucket.b2', 'aws_s3_bucket.b3']
        should_fail = ['aws_s3_bucket.b1']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_less_than_or_equal_solver_simple(self):
        root_folder = 'resources'
        check_id = "LTE"
        should_pass = ['aws_s3_bucket.b1', 'aws_s3_bucket.b3']
        should_fail = ['aws_s3_bucket.b2']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_gt_combinations(self):
        self.assertTrue(GreaterThanAttributeSolver([], None, 1)._get_operation({'a': 2}, 'a'))
        self.assertTrue(GreaterThanAttributeSolver([], None, 1)._get_operation({'a': '2'}, 'a'))
        self.assertTrue(GreaterThanAttributeSolver([], None, '1')._get_operation({'a': 2}, 'a'))
        self.assertTrue(GreaterThanAttributeSolver([], None, '1')._get_operation({'a': '2'}, 'a'))
        self.assertTrue(GreaterThanAttributeSolver([], None, 1)._get_operation({'a': 'aaa'}, 'a'))
        self.assertTrue(GreaterThanAttributeSolver([], None, '1')._get_operation({'a': 'aaa'}, 'a'))
        self.assertTrue(GreaterThanAttributeSolver([], None, '1')._get_operation({'a': '1.5'}, 'a'))

        self.assertFalse(GreaterThanAttributeSolver([], None, 1)._get_operation({'a': 1}, 'a'))
        self.assertFalse(GreaterThanAttributeSolver([], None, 1)._get_operation({'a': '1'}, 'a'))
        self.assertFalse(GreaterThanAttributeSolver([], None, '1')._get_operation({'a': 1}, 'a'))
        self.assertFalse(GreaterThanAttributeSolver([], None, '1')._get_operation({'a': '1'}, 'a'))
        self.assertFalse(GreaterThanAttributeSolver([], None, '1.0')._get_operation({'a': '1.0'}, 'a'))

        self.assertFalse(GreaterThanAttributeSolver([], None, 2)._get_operation({'a': 1}, 'a'))
        self.assertFalse(GreaterThanAttributeSolver([], None, 2)._get_operation({'a': '1'}, 'a'))
        self.assertFalse(GreaterThanAttributeSolver([], None, '2')._get_operation({'a': 1}, 'a'))
        self.assertFalse(GreaterThanAttributeSolver([], None, '2')._get_operation({'a': '1'}, 'a'))
        self.assertFalse(GreaterThanAttributeSolver([], None, 'xxxx')._get_operation({'a': 'aaa'}, 'a'))
        self.assertFalse(GreaterThanAttributeSolver([], None, 'xxxx')._get_operation({'a': '1'}, 'a'))
        self.assertFalse(GreaterThanAttributeSolver([], None, 'xxxx')._get_operation({'a': 1}, 'a'))

    def test_gte_combinations(self):
        self.assertTrue(GreaterThanOrEqualAttributeSolver([], None, 1)._get_operation({'a': 2}, 'a'))
        self.assertTrue(GreaterThanOrEqualAttributeSolver([], None, 1)._get_operation({'a': '2'}, 'a'))
        self.assertTrue(GreaterThanOrEqualAttributeSolver([], None, '1')._get_operation({'a': 2}, 'a'))
        self.assertTrue(GreaterThanOrEqualAttributeSolver([], None, '1')._get_operation({'a': '2'}, 'a'))
        self.assertTrue(GreaterThanOrEqualAttributeSolver([], None, 1)._get_operation({'a': 'aaa'}, 'a'))
        self.assertTrue(GreaterThanOrEqualAttributeSolver([], None, '1')._get_operation({'a': 'aaa'}, 'a'))
        self.assertTrue(GreaterThanOrEqualAttributeSolver([], None, '1')._get_operation({'a': '1.5'}, 'a'))

        self.assertTrue(GreaterThanOrEqualAttributeSolver([], None, 1)._get_operation({'a': 1}, 'a'))
        self.assertTrue(GreaterThanOrEqualAttributeSolver([], None, 1)._get_operation({'a': '1'}, 'a'))
        self.assertTrue(GreaterThanOrEqualAttributeSolver([], None, '1')._get_operation({'a': 1}, 'a'))
        self.assertTrue(GreaterThanOrEqualAttributeSolver([], None, '1')._get_operation({'a': '1'}, 'a'))
        self.assertTrue(GreaterThanOrEqualAttributeSolver([], None, '1')._get_operation({'a': '1.0'}, 'a'))
        self.assertTrue(GreaterThanOrEqualAttributeSolver([], None, '1.0')._get_operation({'a': '1.0'}, 'a'))

        self.assertFalse(GreaterThanOrEqualAttributeSolver([], None, 2)._get_operation({'a': 1}, 'a'))
        self.assertFalse(GreaterThanOrEqualAttributeSolver([], None, 2)._get_operation({'a': '1'}, 'a'))
        self.assertFalse(GreaterThanOrEqualAttributeSolver([], None, '2')._get_operation({'a': 1}, 'a'))
        self.assertFalse(GreaterThanOrEqualAttributeSolver([], None, '2')._get_operation({'a': '1'}, 'a'))
        self.assertFalse(GreaterThanOrEqualAttributeSolver([], None, 'xxxx')._get_operation({'a': 'aaa'}, 'a'))
        self.assertFalse(GreaterThanOrEqualAttributeSolver([], None, 'xxxx')._get_operation({'a': '1'}, 'a'))
        self.assertFalse(GreaterThanOrEqualAttributeSolver([], None, 'xxxx')._get_operation({'a': 1}, 'a'))

    def test_lt_combinations(self):
        self.assertFalse(LessThanAttributeSolver([], None, 1)._get_operation({'a': 2}, 'a'))
        self.assertFalse(LessThanAttributeSolver([], None, 1)._get_operation({'a': '2'}, 'a'))
        self.assertFalse(LessThanAttributeSolver([], None, '1')._get_operation({'a': 2}, 'a'))
        self.assertFalse(LessThanAttributeSolver([], None, '1')._get_operation({'a': '2'}, 'a'))
        self.assertFalse(LessThanAttributeSolver([], None, 1)._get_operation({'a': 'aaa'}, 'a'))
        self.assertFalse(LessThanAttributeSolver([], None, '1')._get_operation({'a': 'aaa'}, 'a'))
        self.assertFalse(LessThanAttributeSolver([], None, '1')._get_operation({'a': '1.5'}, 'a'))

        self.assertFalse(LessThanAttributeSolver([], None, 1)._get_operation({'a': 1}, 'a'))
        self.assertFalse(LessThanAttributeSolver([], None, 1)._get_operation({'a': '1'}, 'a'))
        self.assertFalse(LessThanAttributeSolver([], None, '1')._get_operation({'a': 1}, 'a'))
        self.assertFalse(LessThanAttributeSolver([], None, '1')._get_operation({'a': '1'}, 'a'))
        self.assertFalse(LessThanAttributeSolver([], None, '1.0')._get_operation({'a': '1.0'}, 'a'))

        self.assertTrue(LessThanAttributeSolver([], None, 2)._get_operation({'a': 1}, 'a'))
        self.assertTrue(LessThanAttributeSolver([], None, 2)._get_operation({'a': '1'}, 'a'))
        self.assertTrue(LessThanAttributeSolver([], None, '2')._get_operation({'a': 1}, 'a'))
        self.assertTrue(LessThanAttributeSolver([], None, '2')._get_operation({'a': '1'}, 'a'))
        self.assertTrue(LessThanAttributeSolver([], None, 'xxxx')._get_operation({'a': 'aaa'}, 'a'))
        self.assertTrue(LessThanAttributeSolver([], None, 'xxxx')._get_operation({'a': '1'}, 'a'))
        self.assertTrue(LessThanAttributeSolver([], None, 'xxxx')._get_operation({'a': 1}, 'a'))

    def test_lte_combinations(self):
        self.assertFalse(LessThanOrEqualAttributeSolver([], None, 1)._get_operation({'a': 2}, 'a'))
        self.assertFalse(LessThanOrEqualAttributeSolver([], None, 1)._get_operation({'a': '2'}, 'a'))
        self.assertFalse(LessThanOrEqualAttributeSolver([], None, '1')._get_operation({'a': 2}, 'a'))
        self.assertFalse(LessThanOrEqualAttributeSolver([], None, '1')._get_operation({'a': '2'}, 'a'))
        self.assertFalse(LessThanOrEqualAttributeSolver([], None, 1)._get_operation({'a': 'aaa'}, 'a'))
        self.assertFalse(LessThanOrEqualAttributeSolver([], None, '1')._get_operation({'a': 'aaa'}, 'a'))
        self.assertFalse(LessThanOrEqualAttributeSolver([], None, '1')._get_operation({'a': '1.5'}, 'a'))

        self.assertTrue(LessThanOrEqualAttributeSolver([], None, 1)._get_operation({'a': 1}, 'a'))
        self.assertTrue(LessThanOrEqualAttributeSolver([], None, 1)._get_operation({'a': '1'}, 'a'))
        self.assertTrue(LessThanOrEqualAttributeSolver([], None, '1')._get_operation({'a': 1}, 'a'))
        self.assertTrue(LessThanOrEqualAttributeSolver([], None, '1')._get_operation({'a': '1'}, 'a'))
        self.assertTrue(LessThanOrEqualAttributeSolver([], None, '1.0')._get_operation({'a': '1.0'}, 'a'))

        self.assertTrue(LessThanOrEqualAttributeSolver([], None, 2)._get_operation({'a': 1}, 'a'))
        self.assertTrue(LessThanOrEqualAttributeSolver([], None, 2)._get_operation({'a': '1'}, 'a'))
        self.assertTrue(LessThanOrEqualAttributeSolver([], None, '2')._get_operation({'a': 1}, 'a'))
        self.assertTrue(LessThanOrEqualAttributeSolver([], None, '2')._get_operation({'a': '1'}, 'a'))
        self.assertTrue(LessThanOrEqualAttributeSolver([], None, 'xxxx')._get_operation({'a': 'aaa'}, 'a'))
        self.assertTrue(LessThanOrEqualAttributeSolver([], None, 'xxxx')._get_operation({'a': '1'}, 'a'))
        self.assertTrue(LessThanOrEqualAttributeSolver([], None, 'xxxx')._get_operation({'a': 1}, 'a'))
