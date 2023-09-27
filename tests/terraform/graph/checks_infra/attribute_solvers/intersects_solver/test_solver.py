import os
from parameterized import parameterized_class

from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class([
   {"graph_framework": "NETWORKX"},
   {"graph_framework": "IGRAPH"}
])
class TestIntersectsSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestIntersectsSolver, self).setUp()

    def test_simple_array_intersection1(self):
        root_folder = '../../../resources/public_virtual_machines'
        check_id = "PublicVMs"
        should_pass = ['aws_default_security_group.default_security_group_open']
        should_fail = ['aws_default_security_group.default_security_group_closed']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_simple_array_intersection2(self):
        root_folder = '../../../resources/array_test'
        check_id = "ArrayIntersect"
        should_pass = ['aws_xyz.pass1', 'aws_xyz.pass2']
        should_fail = ['aws_xyz.fail2', 'aws_xyz.fail3', 'aws_xyz.pass3']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_none_attribute(self):
        root_folder = '../../../resources/public_virtual_machines'
        check_id = "NoneAttribute"
        should_pass = []
        should_fail = ['aws_subnet.subnet_public_ip', 'aws_subnet.subnet_not_public_ip']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_string_attribute(self):
        root_folder = '../../../resources/public_virtual_machines'
        check_id = "StringAttribute"
        should_pass = ['aws_subnet.subnet_public_ip']
        should_fail = ['aws_subnet.subnet_not_public_ip']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_mixed_value(self):
        root_folder = '../../../resources/public_virtual_machines'
        check_id = "MixedValue"
        should_pass = ['aws_default_security_group.default_security_group_open']
        should_fail = ['aws_default_security_group.default_security_group_closed']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_tags_intersection(self):
        root_folder = '../../../resources/tag_includes'
        check_id = "TagsIntersect"
        should_pass = ['aws_subnet.acme_subnet']
        should_fail = ['aws_instance.some_instance', 'aws_s3_bucket.acme_s3_bucket']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)
