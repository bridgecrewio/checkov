import unittest

from pathlib import Path

from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.banner import banner
from checkov.runner_filter import RunnerFilter
from checkov.terraform.plan_runner import Runner as tf_plan_runner


class TestRunnerRegistryEnrichment(unittest.TestCase):

    def test_enrichment_of_plan_report(self):
        allowed_checks = ["CKV_AWS_19", "CKV_AWS_20", "CKV_AWS_28", "CKV_AWS_63", "CKV_AWS_119"]
        runner_registry = RunnerRegistry(
            banner, RunnerFilter(checks=allowed_checks, framework=["terraform_plan"]), tf_plan_runner()
        )

        repo_root = Path(__file__).parent / "plan_with_hcl_for_enrichment"
        valid_plan_path = repo_root / "tfplan.json"

        report = runner_registry.run(repo_root_for_plan_enrichment=[repo_root], files=[str(valid_plan_path)])[0]

        failed_check_ids = {c.check_id for c in report.failed_checks}
        skipped_check_ids = {c.check_id for c in report.skipped_checks}
        expected_failed_check_ids = {"CKV_AWS_19", "CKV_AWS_63", "CKV_AWS_119"}
        expected_skipped_check_ids = {"CKV_AWS_20", "CKV_AWS_28"}

        enriched_data = {(c.file_path, tuple(c.file_line_range), tuple(c.code_block)) for c in report.failed_checks}
        expected_enriched_data = {
            (
                "iam.tf",
                (1, 19),
                (
                    (1, 'resource "aws_iam_policy" "policy" {\n'),
                    (2, '  name        = "my_policy-123456789101"\n'),
                    (3, '  path        = "/"\n'),
                    (4, '  description = "My test policy"\n'),
                    (5, "  policy = <<EOF\n"),
                    (6, "{\n"),
                    (7, '  "Version": "2012-10-17",\n'),
                    (8, '  "Statement": [\n'),
                    (9, "    {\n"),
                    (10, '      "Action": [\n'),
                    (11, '        "*"\n'),
                    (12, "      ],\n"),
                    (13, '      "Effect": "Allow",\n'),
                    (14, '      "Resource": "arn:aws:iam::${var.aws_account_id}:role/admin"\n'),
                    (15, "    }\n"),
                    (16, "  ]\n"),
                    (17, "}\n"),
                    (18, "EOF\n"),
                    (19, "}"),
                ),
            ),
            (
                "s3.tf",
                (1, 17),
                (
                    (1, 'resource "aws_s3_bucket" "test-bucket1" {\n'),
                    (2, '  bucket = "test-bucket1"\n'),
                    (3, "  # checkov:skip=CKV_AWS_20: The bucket is a public static content " "host\n"),
                    (4, '  acl    = "public-read"\n'),
                    (5, "  lifecycle_rule {\n"),
                    (6, '    id      = "90 Day Lifecycle"\n'),
                    (7, "    enabled = true\n"),
                    (8, "    expiration {\n"),
                    (9, "      days = 90\n"),
                    (10, "    }\n"),
                    (11, "    noncurrent_version_expiration {\n"),
                    (12, "      days = 90\n"),
                    (13, "    }\n"),
                    (14, "    abort_incomplete_multipart_upload_days = 90\n"),
                    (15, "  }\n"),
                    (16, "  provider = aws.current_region\n"),
                    (17, "}"),
                ),
            ),
            (
                "dynamodb.tf",
                (1, 12),
                (
                    (1, 'resource "aws_dynamodb_table" "cross-environment-violations" {\n'),
                    (2, "  # checkov:skip=CKV_AWS_28: ignoring backups for now\n"),
                    (3, '  name           = "CrossEnvironmentViolations"\n'),
                    (4, "  read_capacity  = 20\n"),
                    (5, "  write_capacity = 20\n"),
                    (6, '  hash_key       = "id"\n'),
                    (7, "  attribute {\n"),
                    (8, '    name = "id"\n'),
                    (9, '    type = "S"\n'),
                    (10, "  }\n"),
                    (11, "  provider = aws.current_region\n"),
                    (12, "}"),
                ),
            ),
        }

        self.assertEqual(len(failed_check_ids), 3)
        self.assertEqual(failed_check_ids, expected_failed_check_ids)
        self.assertEqual(len(skipped_check_ids), 2)
        self.assertEqual(skipped_check_ids, expected_skipped_check_ids)
        self.assertEqual(enriched_data, expected_enriched_data)

    def test_enrichment_of_plan_report_with_modules(self):
        allowed_checks = ["CKV_AWS_66", "CKV_AWS_158"]
        runner_registry = RunnerRegistry(
            banner, RunnerFilter(checks=allowed_checks, framework="terraform_plan"), tf_plan_runner()
        )

        repo_root = Path(__file__).parent / "plan_with_tf_modules_for_enrichment"
        valid_plan_path = repo_root / "tfplan.json"

        report = runner_registry.run(repo_root_for_plan_enrichment=[repo_root], files=[valid_plan_path])[0]

        failed_check_ids = [c.check_id for c in report.failed_checks]
        passed_check_ids = [c.check_id for c in report.passed_checks]
        skipped_check_ids = [c.check_id for c in report.skipped_checks]
        expected_failed_check_ids = ["CKV_AWS_158", "CKV_AWS_158"]
        expected_passed_check_ids = ["CKV_AWS_66", "CKV_AWS_66"]
        expected_skipped_check_ids = []

        enriched_data = set(
            [(c.file_path, tuple(c.file_line_range), tuple(c.code_block)) for c in report.failed_checks]
        )
        expected_enriched_data = {
            (f"/{Path.relative_to(valid_plan_path, Path.cwd())}", (16, 16), (),),
            (
                "log_group/main.tf",
                (1, 2),
                ((1, 'resource "aws_cloudwatch_log_group" "not_encrypted" {\n'), (2, "}\n"),),
            ),
        }

        self.assertEqual(len(failed_check_ids), 2)
        self.assertEqual(failed_check_ids, expected_failed_check_ids)
        self.assertEqual(len(passed_check_ids), 2)
        self.assertEqual(passed_check_ids, expected_passed_check_ids)
        self.assertEqual(len(skipped_check_ids), 0)
        self.assertEqual(skipped_check_ids, expected_skipped_check_ids)
        self.assertEqual(enriched_data, expected_enriched_data)

    def test_skip_check(self):
        allowed_checks = ["CKV_AWS_20", "CKV_AWS_28"]
        runner_registry = RunnerRegistry(
            banner, RunnerFilter(checks=allowed_checks, framework="terraform_plan"), tf_plan_runner()
        )

        repo_root = Path(__file__).parent / "plan_with_hcl_for_enrichment"
        valid_plan_path = repo_root / "tfplan.json"

        report = runner_registry.run(repo_root_for_plan_enrichment=[repo_root], files=[valid_plan_path])[0]

        failed_check_ids = {c.check_id for c in report.failed_checks}
        skipped_check_ids = {c.check_id for c in report.skipped_checks}
        expected_skipped_check_ids = {"CKV_AWS_20", "CKV_AWS_28"}

        self.assertEqual(len(failed_check_ids), 0)
        self.assertEqual(len(skipped_check_ids), 2)
        self.assertEqual(skipped_check_ids, expected_skipped_check_ids)

    def test_skip_check_in_module(self):
        allowed_checks = ["CKV_AWS_19", "CKV2_AWS_6"]
        runner_registry = RunnerRegistry(
            banner, RunnerFilter(checks=allowed_checks, framework=["terraform_plan"]), tf_plan_runner()
        )

        repo_root = Path(__file__).parent / "plan_module_skip_for_enrichment" / "tf"
        valid_plan_path = repo_root / "tfplan.json"

        report = runner_registry.run(repo_root_for_plan_enrichment=[repo_root], files=[valid_plan_path])[0]

        failed_check_ids = {c.check_id for c in report.failed_checks}
        skipped_check_ids = {c.check_id for c in report.skipped_checks}
        expected_skipped_check_ids = set(allowed_checks)

        self.assertEqual(len(failed_check_ids), 0)
        self.assertEqual(len(skipped_check_ids), 2)
        self.assertEqual(skipped_check_ids, expected_skipped_check_ids)


if __name__ == "__main__":
    unittest.main()
