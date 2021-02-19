import os
import unittest

import dpath

from checkov.terraform.checks.definition_access import TerraformDefinitionAccess
from checkov.terraform.parser import Parser


class TestDefinitionAccess(unittest.TestCase):
    def setUp(self) -> None:
        self.data = {}
        dir = f"{os.path.dirname(os.path.realpath(__file__))}/resources/definition_access"
        self.file_name = f"{dir}/example.tf"
        Parser().parse_directory(dir, self.data)
        self.access = TerraformDefinitionAccess(self.data)

    def test_full(self):
        assert self.access.full_definition() == self.data           # equivalent
        assert self.access.full_definition() is not self.data       # not the same (defensive copy or proxy)

    def test_file_not_set(self):
        # Hasn't called _set_file_being_checked
        with self.assertRaises(AssertionError):
            self.access.find_resource_by_name("aws_s3_bucket", "foo")

    def test_find_by_name(self):
        self.access._set_file_being_checked(self.file_name)    # needed to function, normally called in runner

        foo_conf_expected = dpath.get(self.data[self.file_name], f"resource/*/aws_s3_bucket/foo")
        foo_conf = self.access.find_resource_by_name("aws_s3_bucket", "foo")
        assert foo_conf == foo_conf_expected

        bar_conf_expected = dpath.get(self.data[self.file_name], "resource/*/aws_s3_bucket/bar")
        bar_conf = self.access.find_resource_by_name("aws_s3_bucket", "bar")
        assert bar_conf == bar_conf_expected

        assert self.access.find_resource_by_name("aws_s3_bucket", "DOES_NOT_EXIST") == {}
        assert self.access.find_resource_by_name("DOES_NOT_EXIST", "foo") == {}
