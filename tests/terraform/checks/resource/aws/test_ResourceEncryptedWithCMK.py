import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.ResourceEncyyptedWithCMK import check
from checkov.terraform.runner import Runner

class TestResourceEncryptedWithCMK(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_ResourceEncryptedWithCMK"
        report = runner.run(
            root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id])
        )
        summary = report.get_summary()

        passing_resources = {
            "aws_cloudtrail.pass",
            "aws_docdb_cluster.pass",
            "aws_ebs_snapshot_copy.pass",
            "aws_ebs_volume.pass",
            "aws_efs_file_system.pass",
            "aws_elasticache_replication_group.pass",
            "aws_fsx_lustre_file_system.pass",
            "aws_fsx_ontap_file_system.pass",
            "aws_fsx_windows_file_system.pass",
            "aws_imagebuilder_component.pass",
            "aws_s3_object_copy.pass",
            "aws_kinesis_stream.pass",
            "aws_kinesis_video_stream.pass",
            "aws_redshift_cluster.pass",
            "aws_s3_bucket_object.pass",
            "aws_sagemaker_domain.pass",
        }
        failing_resources = {
            "aws_cloudtrail.fail",
            "aws_docdb_cluster.fail",
            "aws_ebs_snapshot_copy.fail",
            "aws_ebs_volume.fail",
            "aws_efs_file_system.fail",
            "aws_elasticache_replication_group.fail",
            "aws_fsx_lustre_file_system.fail",
            "aws_fsx_ontap_file_system.fail",
            "aws_fsx_windows_file_system.fail",
            "aws_imagebuilder_component.fail",
            "aws_s3_object_copy.fail",
            "aws_kinesis_stream.fail",
            "aws_kinesis_video_stream.fail",
            "aws_redshift_cluster.fail",
            "aws_s3_bucket_object.fail",
            "aws_sagemaker_domain.fail",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 16)
        self.assertEqual(summary["failed"], 16)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
