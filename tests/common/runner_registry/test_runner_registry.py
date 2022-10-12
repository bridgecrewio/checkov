import argparse
import json
import unittest

import os
import io
from unittest.mock import patch
from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.code_categories import CodeCategoryMapping
from checkov.common.output.report import Report
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.banner import banner
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.main import DEFAULT_RUNNERS
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner as tf_runner
import re


class TestRunnerRegistry(unittest.TestCase):
    def test_multi_iac(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/example_multi_iac"
        runner_filter = RunnerFilter(framework=None, checks=None, skip_checks=None)
        runner_registry = RunnerRegistry(
            banner, runner_filter, tf_runner(), cfn_runner(), k8_runner()
        )
        reports = runner_registry.run(root_folder=test_files_dir)
        for report in reports:
            self.assertGreater(len(report.passed_checks), 1)

    def test_resource_counts(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/example_multi_iac"
        runner_filter = RunnerFilter(framework=None, checks=None, skip_checks=None)
        runner_registry = RunnerRegistry(
            banner, runner_filter, tf_runner(), cfn_runner(), k8_runner()
        )
        reports = runner_registry.run(root_folder=test_files_dir)

        # The number of resources that will get scan results. Note that this may change if we add policies covering new resource types.
        counts_by_type = {"kubernetes": 10, "terraform": 3, "cloudformation": 4}

        for report in reports:
            self.assertEqual(
                counts_by_type[report.check_type],
                report.get_summary()["resource_count"],
            )

    def test_empty_tf(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/example_empty_tf"
        self.verify_empty_report(test_files_dir=test_files_dir)
        test_files = [test_files_dir + "/example_empty_file.tf"]
        self.verify_empty_report(test_files_dir=None, files=test_files)

    def test_empty_non_existing(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/foo"
        self.verify_empty_report(test_files_dir=test_files_dir)
        test_files = [test_files_dir + "/goo.yaml"]
        self.verify_empty_report(test_files_dir=None, files=test_files)

    def test_empty_yaml(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/example_empty_yaml"
        self.verify_empty_report(test_files_dir=test_files_dir)
        test_files = [test_files_dir + "/example_empty_file.yaml"]
        self.verify_empty_report(test_files_dir=None, files=test_files)

    def verify_empty_report(self, test_files_dir, files=None):
        runner_filter = RunnerFilter(framework=None, checks=None, skip_checks=None)
        runner_registry = RunnerRegistry(
            banner, runner_filter, tf_runner(), cfn_runner(), k8_runner()
        )
        reports = runner_registry.run(root_folder=test_files_dir, files=files)
        for report in reports:
            self.assertEqual(report.failed_checks, [])
            self.assertEqual(report.skipped_checks, [])
            self.assertEqual(report.passed_checks, [])
        return runner_registry

    def test_compact_json_output(self):
        test_files_dir = os.path.dirname(os.path.realpath(__file__)) + "/example_s3_tf"
        runner_filter = RunnerFilter(framework=None, checks=None, skip_checks=None)
        runner_registry = RunnerRegistry(
            banner, runner_filter, tf_runner(), cfn_runner(), k8_runner()
        )
        reports = runner_registry.run(root_folder=test_files_dir)

        config = argparse.Namespace(
            file=['./example_s3_tf/main.tf'],
            compact=True,
            output=['json'],
            quiet=False,
            soft_fail=False,
            soft_fail_on=None,
            hard_fail_on=None,
            output_file_path=None,
            use_enforcement_rules=None
        )

        with patch('sys.stdout', new=io.StringIO()) as captured_output:
            runner_registry.print_reports(scan_reports=reports, config=config)

        output = json.loads(captured_output.getvalue())
        passed_checks = output["results"]["passed_checks"]
        failed_checks = output["results"]["failed_checks"]

        assert all(check["code_block"] is None for check in passed_checks)
        assert all(check["connected_node"] is None for check in passed_checks)
        assert all(check["code_block"] is None for check in failed_checks)
        assert all(check["connected_node"] is None for check in failed_checks)

    def test_compact_csv_output(self):
        test_files_dir = os.path.dirname(os.path.realpath(__file__)) + "/example_s3_tf"
        runner_filter = RunnerFilter(framework=None, checks=None, skip_checks=None)
        runner_registry = RunnerRegistry(
            banner, runner_filter, tf_runner(), cfn_runner(), k8_runner()
        )
        reports = runner_registry.run(root_folder=test_files_dir)

        config = argparse.Namespace(
            file=['./example_s3_tf/main.tf'],
            compact=True,
            output=['csv'],
            quiet=False,
            soft_fail=False,
            soft_fail_on=None,
            hard_fail_on=None,
            output_file_path=None,
            use_enforcement_rules=None
        )

        with patch('sys.stdout', new=io.StringIO()) as captured_output:
            runner_registry.print_reports(scan_reports=reports, config=config)

        output = captured_output.getvalue()

        self.assertIn('Persisting SBOM to ', output)
        iac_file_path = re.search("Persisting SBOM to (.*iac.csv)", output).group(1)
        with open(iac_file_path) as file:
            content = file.readlines()
            header = content[:1][0]
            self.assertEqual('Resource,Path,Git Org,Git Repository,Misconfigurations,Severity\n', header)
            rows = content[1:]
            self.assertIn('aws_s3_bucket', rows[0])
        oss_file_path = re.search("Persisting SBOM to (.*oss_packages.csv)", output).group(1)
        with open(oss_file_path) as file:
            content = file.readlines()
            header = content[:1][0]
            self.assertEqual('Package,Version,Path,Git Org,Git Repository,Vulnerability,Severity,Licenses\n', header)
            row = content[1:][0]
            self.assertIn('bridgecrew.cloud', row)

    def test_runner_file_filter(self):
        checkov_runners = [value for attr, value in CheckType.__dict__.items() if not attr.startswith("__")]

        runner_filter = RunnerFilter(framework=['all'], runners=checkov_runners)
        runner_registry = RunnerRegistry(
            banner, runner_filter, *DEFAULT_RUNNERS
        )
        runner_registry.filter_runners_for_files([])
        self.assertEqual(set(runner_registry.runners), set(DEFAULT_RUNNERS))

        runner_filter = RunnerFilter(framework=['all'], runners=checkov_runners)
        runner_registry = RunnerRegistry(
            banner, runner_filter, *DEFAULT_RUNNERS
        )
        runner_registry.filter_runners_for_files(['main.tf'])
        self.assertEqual(set(r.check_type for r in runner_registry.runners), {'terraform', 'secrets'})

        runner_registry = RunnerRegistry(
            banner, runner_filter, *DEFAULT_RUNNERS
        )
        runner_registry.filter_runners_for_files(['main.tf', 'requirements.txt'])
        self.assertEqual(set(r.check_type for r in runner_registry.runners), {'terraform', 'secrets', 'sca_package'})

        runner_filter = RunnerFilter(framework=['terraform'], runners=checkov_runners)
        runner_registry = RunnerRegistry(
            banner, runner_filter, *DEFAULT_RUNNERS
        )
        runner_registry.filter_runners_for_files(['main.tf'])
        self.assertEqual(set(r.check_type for r in runner_registry.runners), {'terraform'})

        runner_filter = RunnerFilter(framework=['all'], skip_framework=['secrets'], runners=checkov_runners)
        runner_registry = RunnerRegistry(
            banner, runner_filter, *DEFAULT_RUNNERS
        )
        runner_registry.filter_runners_for_files(['main.tf'])
        self.assertEqual(set(r.check_type for r in runner_registry.runners), {'terraform'})

        runner_filter = RunnerFilter(framework=['all'], skip_framework=['terraform'], runners=checkov_runners)
        runner_registry = RunnerRegistry(
            banner, runner_filter, *DEFAULT_RUNNERS
        )
        runner_registry.filter_runners_for_files(['main.tf'])
        self.assertEqual(set(r.check_type for r in runner_registry.runners), {'secrets'})

        runner_filter = RunnerFilter(framework=['all'], runners=checkov_runners)
        runner_registry = RunnerRegistry(
            banner, runner_filter, *DEFAULT_RUNNERS
        )
        runner_registry.filter_runners_for_files(['manifest.json'])
        self.assertIn("kubernetes", set(r.check_type for r in runner_registry.runners))

    def test_runners_have_code_category(self):
        checkov_runners = [value for attr, value in CheckType.__dict__.items() if not attr.startswith("__")]
        for runner in checkov_runners:
            self.assertIn(runner, CodeCategoryMapping)

    def test_get_enriched_resources(self):
        test_files_dir = os.path.dirname(os.path.realpath(__file__)) + "/plan_with_tf_modules_for_enrichment"
        runner_filter = RunnerFilter(download_external_modules=True)
        runner_registry = RunnerRegistry(
            banner, runner_filter, tf_runner()
        )
        reports = runner_registry.run(root_folder=test_files_dir)

        config = argparse.Namespace(
            file=['./plan_with_tf_modules_for_enrichment/tfplan.json'],
            compact=True,
            output=['json'],
            quiet=True,
            soft_fail=False,
            soft_fail_on=None,
            hard_fail_on=None,
            output_file_path=None,
            use_enforcement_rules=None
        )

        with patch('sys.stdout', new=io.StringIO()) as captured_output:
            runner_registry.print_reports(scan_reports=reports, config=config)

        output = captured_output.getvalue()

    def test_extract_git_info_from_account_id(self):
        account_id = "owner/name"
        expected_git_org = "owner"
        expected_git_repo = "name"
        result_git_org, result_git_repo = RunnerRegistry.extract_git_info_from_account_id(account_id)
        self.assertEqual(expected_git_repo, result_git_repo)
        self.assertEqual(expected_git_org, result_git_org)

        account_id = "owner/with/slash/separator/name"
        expected_git_org = "owner/with/slash/separator"
        expected_git_repo = "name"
        result_git_org, result_git_repo = RunnerRegistry.extract_git_info_from_account_id(account_id)
        self.assertEqual(expected_git_repo, result_git_repo)
        self.assertEqual(expected_git_org, result_git_org)

        account_id = "name"
        expected_git_org = ""
        expected_git_repo = ""
        result_git_org, result_git_repo = RunnerRegistry.extract_git_info_from_account_id(account_id)
        self.assertEqual(expected_git_repo, result_git_repo)
        self.assertEqual(expected_git_org, result_git_org)

        account_id = ""
        expected_git_org = ""
        expected_git_repo = ""
        result_git_org, result_git_repo = RunnerRegistry.extract_git_info_from_account_id(account_id)
        self.assertEqual(expected_git_repo, result_git_repo)
        self.assertEqual(expected_git_org, result_git_org)

    def test_merge_reports(self):
        # given
        runner_registry = RunnerRegistry(banner, RunnerFilter(), *DEFAULT_RUNNERS)
        reports = [
            [
                Report(check_type=CheckType.TERRAFORM),
                Report(check_type=CheckType.SCA_IMAGE),
            ],
            Report(check_type=CheckType.CLOUDFORMATION),
            Report(check_type=CheckType.SCA_IMAGE),
        ]

        # when
        merged_reports = runner_registry._merge_reports(reports=reports)

        # then
        merged_report_check_types = [
            report.check_type
            for report in merged_reports
        ]
        self.assertCountEqual(merged_report_check_types,[
            CheckType.TERRAFORM,
            CheckType.CLOUDFORMATION,
            CheckType.SCA_IMAGE,
        ])


def test_non_compact_json_output(capsys):
    # given
    test_files_dir = os.path.dirname(os.path.realpath(__file__)) + "/example_s3_tf"
    runner_filter = RunnerFilter(framework=None, checks=None, skip_checks=None)
    runner_registry = RunnerRegistry(
        banner, runner_filter, tf_runner(), cfn_runner(), k8_runner()
    )
    reports = runner_registry.run(root_folder=test_files_dir)

    config = argparse.Namespace(
        file=['./example_s3_tf/main.tf'],
        compact=False,
        output=['json'],
        quiet=False,
        soft_fail=False,
        soft_fail_on=None,
        hard_fail_on=None,
        output_file_path=None,
        use_enforcement_rules=None
    )

    # when
    runner_registry.print_reports(scan_reports=reports, config=config)

    # then
    captured = capsys.readouterr()

    assert 'code_block' in captured.out


if __name__ == "__main__":
    unittest.main()
