import os
import unittest

from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.banner import banner
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner as tf_runner
from checkov.terraform.plan_runner import Runner as tf_plan_runner


class TestRunnerRegistry(unittest.TestCase):

    def test_multi_iac(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/example_multi_iac"
        runner_filter = RunnerFilter(framework=None, checks=None, skip_checks=None)
        runner_registry = RunnerRegistry(banner, runner_filter, tf_runner(), cfn_runner(), k8_runner())
        reports = runner_registry.run(root_folder=test_files_dir)
        for report in reports:
            self.assertGreater(len(report.passed_checks), 1)

    def test_empty_tf(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/example_empty_tf"
        self.verify_empty_report(test_files_dir=test_files_dir)
        test_files = [test_files_dir + '/example_empty_file.tf']
        self.verify_empty_report(test_files_dir=None, files=test_files)

    def test_empty_non_existing(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/foo"
        self.verify_empty_report(test_files_dir=test_files_dir)
        test_files = [test_files_dir + '/goo.yaml']
        self.verify_empty_report(test_files_dir=None, files=test_files)

    def test_empty_yaml(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/example_empty_yaml"
        self.verify_empty_report(test_files_dir=test_files_dir)
        test_files = [test_files_dir + '/example_empty_file.yaml']
        self.verify_empty_report(test_files_dir=None, files=test_files)

    def verify_empty_report(self, test_files_dir, files=None):
        runner_filter = RunnerFilter(framework=None, checks=None, skip_checks=None)
        runner_registry = RunnerRegistry(banner, runner_filter, tf_runner(), cfn_runner(), k8_runner())
        reports = runner_registry.run(root_folder=test_files_dir, files=files)
        for report in reports:
            self.assertEqual(report.failed_checks, [])
            self.assertEqual(report.skipped_checks, [])
            self.assertEqual(report.passed_checks, [])
        return runner_registry

    def test_enrichment_of_plan_report(self):
        allowed_checks = ["CKV_AWS_19", "CKV_AWS_20", "CKV_AWS_28", "CKV_AWS_63", "CKV_AWS_119"]
        runner_registry = RunnerRegistry(banner, RunnerFilter(checks=allowed_checks), tf_plan_runner())
        
        current_dir = os.path.dirname(os.path.realpath(__file__))
        repo_root = current_dir + "/plan_with_hcl_for_enrichment/"
        valid_plan_path = repo_root + "tfplan.json"

        reports = runner_registry.run(
            repo_root_for_plan_enrichment=repo_root,
            files=[valid_plan_path]
        )

        for report in reports:
            failed_check_ids = set([c.check_id for c in report.failed_checks])
            skipped_check_ids = set([c.check_id for c in report.skipped_checks]) 
            expected_failed_check_ids = {
                "CKV_AWS_19",
                "CKV_AWS_63",
                "CKV_AWS_119"
            }
            expected_skipped_check_ids = {
                "CKV_AWS_20",
                "CKV_AWS_28"
            }
            enriched_data = set([(c.file_path, tuple(c.file_line_range), tuple(c.code_block)) for c in report.failed_checks])
            expected_enriched_paths = {
                (
                    "iam.tf",  
                    (1, 19), 
                    (
                        (1, 'resource "aws_iam_policy" "policy" {\n'),
                        (2, '  name        = "my_policy-123456789101"\n'),
                        (3, '  path        = "/"\n'),
                        (4, '  description = "My test policy"\n'),
                        (5, '  policy = <<EOF\n'),
                        (6, '{\n'),
                        (7, '  "Version": "2012-10-17",\n'),
                        (8, '  "Statement": [\n'),
                        (9, '    {\n'),
                        (10, '      "Action": [\n'),
                        (11, '        "*"\n'),
                        (12, '      ],\n'),
                        (13, '      "Effect": "Allow",\n'),
                        (14, '      "Resource": "arn:aws:iam::${var.aws_account_id}:role/admin"\n'),
                        (15, '    }\n'),
                        (16, '  ]\n'),
                        (17, '}\n'),
                        (18, 'EOF\n'),
                        (19, '}')
                    )
                ),
                (
                    "s3.tf",
                    (1, 17),
                    (
                        (1, 'resource "aws_s3_bucket" "test-bucket1" {\n'),
                        (2, '  bucket = "test-bucket1"\n'),
                        (3,
                         '  # checkov:skip=CKV_AWS_20: The bucket is a public static content '
                         'host\n'),
                        (4, '  acl    = "public-read"\n'),
                        (5, '  lifecycle_rule {\n'),
                        (6, '    id      = "90 Day Lifecycle"\n'),
                        (7, '    enabled = true\n'),
                        (8, '    expiration {\n'),
                        (9, '      days = 90\n'),
                        (10, '    }\n'),
                        (11, '    noncurrent_version_expiration {\n'),
                        (12, '      days = 90\n'),
                        (13, '    }\n'),
                        (14, '    abort_incomplete_multipart_upload_days = 90\n'),
                        (15, '  }\n'),
                        (16, '  provider = aws.current_region\n'),
                        (17, '}')
                    )
                ),
                (
                    "dynamodb.tf",
                    (1, 12),
                    (
                        (1, 'resource "aws_dynamodb_table" "cross-environment-violations" {\n'),
                        (2, '  # checkov:skip=CKV_AWS_28: ignoring backups for now\n'),
                        (3, '  name           = "CrossEnvironmentViolations"\n'),
                        (4, '  read_capacity  = 20\n'),
                        (5, '  write_capacity = 20\n'),   
                        (6, '  hash_key       = "id"\n'),   
                        (7, '  attribute {\n'),
                        (8, '    name = "id"\n'),   
                        (9, '    type = "S"\n'),   
                        (10, '  }\n'),   
                        (11, '  provider = aws.current_region\n'),   
                        (12, '}')
                    )
                )
            }       

        assert len(report.passed_checks) == 0
        assert len(failed_check_ids) == 3
        assert failed_check_ids == expected_failed_check_ids
        assert len(skipped_check_ids) == 2
        assert skipped_check_ids == expected_skipped_check_ids
        assert enriched_data == expected_enriched_paths




if __name__ == '__main__':
    unittest.main()
