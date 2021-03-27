import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.LaunchConfigurationEBSEncryption import check


class TestLaunchConfigurationEBSEncryption(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "image_id": ["ami-123"],
            "instance_type": ["t2.micro"],
            "root_block_device": [{"encrypted": [False]}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_missing_element(self):
        resource_conf = {
            "image_id": ["ami-123"],
            "instance_type": ["t2.micro"],
            "root_block_device": [{}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_multiple_blocks(self):
        hcl_res = hcl2.loads(
            """
                            resource "aws_instance" "test" {
                              ami                  = var.ami_id
                              instance_type        = var.instance_type
                              key_name             = var.key_name

                              root_block_device {
                                volume_type = "gp2"
                                volume_size = var.root_volume_size
                                encrypted = true
                              }


                              ebs_block_device {
                                volume_type = "gp2"
                                volume_size = var.ebs_volume_size
                                device_name = "/dev/xvdb"
                                encrypted = false
                              }
                            }
                                """
        )
        resource_conf = hcl_res["resource"][0]["aws_instance"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_omission_root_block_device_1(self):
        # Test to ensure no false negative as raised in issue 496
        hcl_res = hcl2.loads(
            """
                            resource "aws_instance" "test" {
                              ami                  = var.ami_id
                              instance_type        = var.instance_type
                              key_name             = var.key_name

                              ebs_block_device {
                                volume_type = "gp2"
                                volume_size = var.ebs_volume_size
                                device_name = "/dev/xvdb"
                                encrypted = false
                              }
                            }
                                """
        )
        resource_conf = hcl_res["resource"][0]["aws_instance"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_omission_root_block_device_2(self):
        # Test to ensure no false negative as raised in issue 496
        hcl_res = hcl2.loads(
            """
                            resource "aws_instance" "test" {
                              ami                  = var.ami_id
                              instance_type        = var.instance_type
                              key_name             = var.key_name
                            }
                                """
        )
        resource_conf = hcl_res["resource"][0]["aws_instance"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_with_snapshot_id(self):
        hcl_res = hcl2.loads(
            """
                        resource "aws_instance" "test" {
                              ami                  = var.ami_id
                              instance_type        = var.instance_type
                              key_name             = var.key_name

                              root_block_device {
                                volume_type = "gp2"
                                volume_size = var.root_volume_size
                                snapshot_id = "snap-1234"
                              }
                            }
                        """
        )
        resource_conf = hcl_res["resource"][0]["aws_instance"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
                        resource "aws_instance" "test" {
                              ami                  = var.ami_id
                              instance_type        = var.instance_type
                              key_name             = var.key_name

                              root_block_device {
                                volume_type = "gp2"
                                volume_size = var.root_volume_size
                                encrypted = true
                              }
                            }
                        """
        )
        resource_conf = hcl_res["resource"][0]["aws_instance"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_multiple_ordering(self):
        hcl_res = hcl2.loads(
            """
                            resource "aws_instance" "test" {
                              ami                  = var.ami_id
                              instance_type        = var.instance_type
                              key_name             = var.key_name

                              ebs_block_device {
                                volume_type = "gp2"
                                volume_size = var.ebs_volume_size
                                device_name = "/dev/xvdb"
                                encrypted = true
                              }

                              root_block_device {
                                volume_type = "gp2"
                                volume_size = var.root_volume_size
                                encrypted = true
                              }

                            }
                                """
        )
        resource_conf = hcl_res["resource"][0]["aws_instance"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
