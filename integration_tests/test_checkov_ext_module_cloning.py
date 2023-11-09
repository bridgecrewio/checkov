import os
import unittest
import sys
import platform

current_dir = os.path.dirname(os.path.realpath(__file__))
ext_modules_path = os.path.join(current_dir, "example_ext_private_modules", ".external_modules")


class TestCheckovExtModuleCloning(unittest.TestCase):

    def test_private_github_modules_api_key(self):
        if sys.version_info[1] == 8 and platform.system() == 'Linux' and False:
            expected_private_github_path = os.path.join(ext_modules_path, "github.com", "ckv-tests")
            expected_private_github_modules = [os.path.join(expected_private_github_path, "terraform-aws-iam-s3-user-private"),
                                               os.path.join(expected_private_github_path, "terraform-aws-s3-bucket-private")]
            for m in expected_private_github_modules:
                assert os.path.exists(m)

    def test_private_tfc_modules_api_key(self):
        if sys.version_info[1] == 8 and platform.system() == 'Linux' and False:
            expected_private_tfc_path = os.path.join(ext_modules_path, "app.terraform.io", "panw-bridgecrew")
            expected_private_tfc_modules = [
                os.path.join(expected_private_tfc_path, "iam-s3-user", "aws", "0.15.7"),
                os.path.join(expected_private_tfc_path, "s3-bucket1", "aws", "0.0.2")]
            for m in expected_private_tfc_modules:
                assert os.path.exists(m)
