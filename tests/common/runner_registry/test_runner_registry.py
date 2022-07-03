import argparse
import unittest

import os
import io
from unittest.mock import patch
from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.output.report import CheckType
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.banner import banner
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.main import DEFAULT_RUNNERS
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner as tf_runner


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
        )

        with patch('sys.stdout', new=io.StringIO()) as captured_output:
            runner_registry.print_reports(scan_reports=reports, config=config)

        output = captured_output.getvalue()

        assert 'code_block' not in output
        assert 'connected_node' not in output

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
    )

    # when
    runner_registry.print_reports(scan_reports=reports, config=config)

    # then
    captured = capsys.readouterr()

    assert 'code_block' in captured.out


if __name__ == "__main__":
    unittest.main()
