import os
import argparse
import json
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter
from tests.common.banner import banner
from tests.common.runner.test_runner import TestRunner


def test_json_output_with_explain(capsys):
    # given
    test_files_dir = os.path.dirname(os.path.realpath(__file__)) + "/example_s3_tf"
    runner_filter = RunnerFilter(framework=None, checks=None, skip_checks=None)
    runner_registry = RunnerRegistry(
        banner, runner_filter, TestRunner()
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
        use_enforcement_rules=None,
        explain=True,
        explain_lang='en'
    )

    # when
    runner_registry.print_reports(scan_reports=reports, config=config)

    # then
    captured = capsys.readouterr()
    report_json = json.loads(captured.out)

    # Verify that explain fields are present in the JSON output
    for report in report_json:
        if 'results' in report:
            for check_type in ['passed_checks', 'failed_checks', 'skipped_checks']:
                if check_type in report['results']:
                    for check in report['results'][check_type]:
                        assert 'explain' in check
                        assert 'explain_lang' in check
                        assert check['explain_lang'] == 'en'


def test_cli_output_with_explain(capsys):
    # given
    test_files_dir = os.path.dirname(os.path.realpath(__file__)) + "/example_s3_tf"
    runner_filter = RunnerFilter(framework=None, checks=None, skip_checks=None)
    runner_registry = RunnerRegistry(
        banner, runner_filter, TestRunner()
    )
    reports = runner_registry.run(root_folder=test_files_dir)

    config = argparse.Namespace(
        file=['./example_s3_tf/main.tf'],
        compact=False,
        output=['cli'],
        quiet=False,
        soft_fail=False,
        soft_fail_on=None,
        hard_fail_on=None,
        output_file_path=None,
        use_enforcement_rules=None,
        explain=True,
        explain_lang='en'
    )

    # when
    runner_registry.print_reports(scan_reports=reports, config=config)

    # then
    captured = capsys.readouterr()

    # Verify that explain information is present in the CLI output
    assert 'Rule Explanation:' in captured.out
    assert 'Risk Cause:' in captured.out
    assert 'Impact:' in captured.out
    assert 'Fix Example:' in captured.out


def test_sarif_output_with_explain(capsys):
    # given
    test_files_dir = os.path.dirname(os.path.realpath(__file__)) + "/example_s3_tf"
    runner_filter = RunnerFilter(framework=None, checks=None, skip_checks=None)
    runner_registry = RunnerRegistry(
        banner, runner_filter, TestRunner()
    )
    reports = runner_registry.run(root_folder=test_files_dir)

    config = argparse.Namespace(
        file=['./example_s3_tf/main.tf'],
        compact=False,
        output=['sarif'],
        quiet=False,
        soft_fail=False,
        soft_fail_on=None,
        hard_fail_on=None,
        output_file_path=None,
        use_enforcement_rules=None,
        explain=True,
        explain_lang='en'
    )

    # when
    runner_registry.print_reports(scan_reports=reports, config=config)

    # then
    captured = capsys.readouterr()
    sarif_json = json.loads(captured.out)

    # Verify that explain information is present in the SARIF output
    assert 'rules' in sarif_json['runs'][0]
    for rule in sarif_json['runs'][0]['rules']:
        assert 'help' in rule
        assert 'text' in rule['help']
        # The explain information should be included in the help text
        assert any(keyword in rule['help']['text'] for keyword in ['Risk Cause', 'Impact', 'Fix Example'])


if __name__ == '__main__':
    test_json_output_with_explain()
    test_cli_output_with_explain()
    test_sarif_output_with_explain()
    print("All tests passed!")
