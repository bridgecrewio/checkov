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
        cls = GreaterThanAttributeSolver

        self.assertTrue(cls([], None, 1)._get_operation({'a': 2}, 'a'))
        self.assertTrue(cls([], None, 1)._get_operation({'a': '2'}, 'a'))
        self.assertTrue(cls([], None, '1')._get_operation({'a': 2}, 'a'))
        self.assertTrue(cls([], None, '1')._get_operation({'a': '2'}, 'a'))
        self.assertTrue(cls([], None, 1)._get_operation({'a': 'aaa'}, 'a'))
        self.assertTrue(cls([], None, '1')._get_operation({'a': 'aaa'}, 'a'))
        self.assertTrue(cls([], None, '1')._get_operation({'a': '1.5'}, 'a'))

        self.assertFalse(cls([], None, 1)._get_operation({'a': 1}, 'a'))
        self.assertFalse(cls([], None, 1)._get_operation({'a': '1'}, 'a'))
        self.assertFalse(cls([], None, '1')._get_operation({'a': 1}, 'a'))
        self.assertFalse(cls([], None, '1')._get_operation({'a': '1'}, 'a'))
        self.assertFalse(cls([], None, '1.0')._get_operation({'a': '1.0'}, 'a'))

        self.assertFalse(cls([], None, 2)._get_operation({'a': 1}, 'a'))
        self.assertFalse(cls([], None, 2)._get_operation({'a': '1'}, 'a'))
        self.assertFalse(cls([], None, '2')._get_operation({'a': 1}, 'a'))
        self.assertFalse(cls([], None, '2')._get_operation({'a': '1'}, 'a'))
        self.assertFalse(cls([], None, 'xxxx')._get_operation({'a': 'aaa'}, 'a'))
        self.assertFalse(cls([], None, 'xxxx')._get_operation({'a': '1'}, 'a'))
        self.assertFalse(cls([], None, 'xxxx')._get_operation({'a': 1}, 'a'))

        # undefined types
        self.assertTrue(cls([], None, '1')._get_operation({'a': {'abc': 'xyz'}}, 'a'))
        self.assertFalse(cls([], None, {'a': {'abc': 'xyz'}})._get_operation({'a': '1'}, 'a'))
        self.assertTrue(cls([], None, '1')._get_operation({'a': ['xyz']}, 'a'))
        self.assertFalse(cls([], None, ['xyz'])._get_operation({'a': '1'}, 'a'))

    def test_gte_combinations(self):
        cls = GreaterThanOrEqualAttributeSolver

        self.assertTrue(cls([], None, 1)._get_operation({'a': 2}, 'a'))
        self.assertTrue(cls([], None, 1)._get_operation({'a': '2'}, 'a'))
        self.assertTrue(cls([], None, '1')._get_operation({'a': 2}, 'a'))
        self.assertTrue(cls([], None, '1')._get_operation({'a': '2'}, 'a'))
        self.assertTrue(cls([], None, 1)._get_operation({'a': 'aaa'}, 'a'))
        self.assertTrue(cls([], None, '1')._get_operation({'a': 'aaa'}, 'a'))
        self.assertTrue(cls([], None, '1')._get_operation({'a': '1.5'}, 'a'))

        self.assertTrue(cls([], None, 1)._get_operation({'a': 1}, 'a'))
        self.assertTrue(cls([], None, 1)._get_operation({'a': '1'}, 'a'))
        self.assertTrue(cls([], None, '1')._get_operation({'a': 1}, 'a'))
        self.assertTrue(cls([], None, '1')._get_operation({'a': '1'}, 'a'))
        self.assertTrue(cls([], None, '1')._get_operation({'a': '1.0'}, 'a'))
        self.assertTrue(cls([], None, '1.0')._get_operation({'a': '1.0'}, 'a'))

        self.assertFalse(cls([], None, 2)._get_operation({'a': 1}, 'a'))
        self.assertFalse(cls([], None, 2)._get_operation({'a': '1'}, 'a'))
        self.assertFalse(cls([], None, '2')._get_operation({'a': 1}, 'a'))
        self.assertFalse(cls([], None, '2')._get_operation({'a': '1'}, 'a'))
        self.assertFalse(cls([], None, 'xxxx')._get_operation({'a': 'aaa'}, 'a'))
        self.assertFalse(cls([], None, 'xxxx')._get_operation({'a': '1'}, 'a'))
        self.assertFalse(cls([], None, 'xxxx')._get_operation({'a': 1}, 'a'))

        # undefined types
        self.assertTrue(cls([], None, '1')._get_operation({'a': {'abc': 'xyz'}}, 'a'))
        self.assertFalse(cls([], None, {'a': {'abc': 'xyz'}})._get_operation({'a': '1'}, 'a'))
        self.assertTrue(cls([], None, '1')._get_operation({'a': ['xyz']}, 'a'))
        self.assertFalse(cls([], None, ['xyz'])._get_operation({'a': '1'}, 'a'))

    def test_lt_combinations(self):
        cls = LessThanAttributeSolver

        self.assertFalse(cls([], None, 1)._get_operation({'a': 2}, 'a'))
        self.assertFalse(cls([], None, 1)._get_operation({'a': '2'}, 'a'))
        self.assertFalse(cls([], None, '1')._get_operation({'a': 2}, 'a'))
        self.assertFalse(cls([], None, '1')._get_operation({'a': '2'}, 'a'))
        self.assertFalse(cls([], None, 1)._get_operation({'a': 'aaa'}, 'a'))
        self.assertFalse(cls([], None, '1')._get_operation({'a': 'aaa'}, 'a'))
        self.assertFalse(cls([], None, '1')._get_operation({'a': '1.5'}, 'a'))

        self.assertFalse(cls([], None, 1)._get_operation({'a': 1}, 'a'))
        self.assertFalse(cls([], None, 1)._get_operation({'a': '1'}, 'a'))
        self.assertFalse(cls([], None, '1')._get_operation({'a': 1}, 'a'))
        self.assertFalse(cls([], None, '1')._get_operation({'a': '1'}, 'a'))
        self.assertFalse(cls([], None, '1.0')._get_operation({'a': '1.0'}, 'a'))

        self.assertTrue(cls([], None, 2)._get_operation({'a': 1}, 'a'))
        self.assertTrue(cls([], None, 2)._get_operation({'a': '1'}, 'a'))
        self.assertTrue(cls([], None, '2')._get_operation({'a': 1}, 'a'))
        self.assertTrue(cls([], None, '2')._get_operation({'a': '1'}, 'a'))
        self.assertTrue(cls([], None, 'xxxx')._get_operation({'a': 'aaa'}, 'a'))
        self.assertTrue(cls([], None, 'xxxx')._get_operation({'a': '1'}, 'a'))
        self.assertTrue(cls([], None, 'xxxx')._get_operation({'a': 1}, 'a'))

        # undefined types
        self.assertFalse(cls([], None, '1')._get_operation({'a': {'abc': 'xyz'}}, 'a'))
        self.assertTrue(cls([], None, {'a': {'abc': 'xyz'}})._get_operation({'a': '1'}, 'a'))
        self.assertFalse(cls([], None, '1')._get_operation({'a': ['xyz']}, 'a'))
        self.assertTrue(cls([], None, ['xyz'])._get_operation({'a': '1'}, 'a'))

    def test_lte_combinations(self):
        cls = LessThanOrEqualAttributeSolver

        self.assertFalse(cls([], None, 1)._get_operation({'a': 2}, 'a'))
        self.assertFalse(cls([], None, 1)._get_operation({'a': '2'}, 'a'))
        self.assertFalse(cls([], None, '1')._get_operation({'a': 2}, 'a'))
        self.assertFalse(cls([], None, '1')._get_operation({'a': '2'}, 'a'))
        self.assertFalse(cls([], None, 1)._get_operation({'a': 'aaa'}, 'a'))
        self.assertFalse(cls([], None, '1')._get_operation({'a': 'aaa'}, 'a'))
        self.assertFalse(cls([], None, '1')._get_operation({'a': '1.5'}, 'a'))

        self.assertTrue(cls([], None, 1)._get_operation({'a': 1}, 'a'))
        self.assertTrue(cls([], None, 1)._get_operation({'a': '1'}, 'a'))
        self.assertTrue(cls([], None, '1')._get_operation({'a': 1}, 'a'))
        self.assertTrue(cls([], None, '1')._get_operation({'a': '1'}, 'a'))
        self.assertTrue(cls([], None, '1.0')._get_operation({'a': '1.0'}, 'a'))

        self.assertTrue(cls([], None, 2)._get_operation({'a': 1}, 'a'))
        self.assertTrue(cls([], None, 2)._get_operation({'a': '1'}, 'a'))
        self.assertTrue(cls([], None, '2')._get_operation({'a': 1}, 'a'))
        self.assertTrue(cls([], None, '2')._get_operation({'a': '1'}, 'a'))
        self.assertTrue(cls([], None, 'xxxx')._get_operation({'a': 'aaa'}, 'a'))
        self.assertTrue(cls([], None, 'xxxx')._get_operation({'a': '1'}, 'a'))
        self.assertTrue(cls([], None, 'xxxx')._get_operation({'a': 1}, 'a'))

        self.assertFalse(cls([], None, '1')._get_operation({'a': {'abc': 'xyz'}}, 'a'))
        self.assertTrue(cls([], None, {'a': {'abc': 'xyz'}})._get_operation({'a': '1'}, 'a'))
        self.assertFalse(cls([], None, '1')._get_operation({'a': ['xyz']}, 'a'))
        self.assertTrue(cls([], None, ['xyz'])._get_operation({'a': '1'}, 'a'))
