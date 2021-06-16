import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.BackupVaultEncrypted import check
import hcl2


class TestBackupVaultEncrypted(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_backup_vault" "example" {
                    name        = "example_backup_vault"
                }
            """)
        resource_conf = hcl_res['resource'][0]['aws_backup_vault']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "aws_backup_vault" "example" {
                    name        = "example_backup_vault"
                    kms_key_arn = aws_kms_key.example.arn
                }
            """)
        resource_conf = hcl_res['resource'][0]['aws_backup_vault']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()