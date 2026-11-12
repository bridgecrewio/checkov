import argparse
import json
from pathlib import Path

from checkov.common.output.baseline import Baseline
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


def test_to_dict():
    # given
    test_folder = Path(__file__).parent / "fixtures"
    checks = ["CKV_AWS_18", "CKV_AWS_19", "CKV_AWS_21", "CKV2_AWS_6"]  # 1 pass, 2 fail, 1 skip
    report = Runner().run(root_folder=str(test_folder), runner_filter=RunnerFilter(checks=checks))

    baseline = Baseline()
    baseline.add_findings_from_report(report)

    # when
    output = baseline.to_dict()

    # then
    assert output == {
        "failed_checks": [
            {
                "file": "/main.tf",
                "findings": [
                    {
                        "resource": "aws_s3_bucket.destination",
                        "check_ids": ["CKV2_AWS_6", "CKV_AWS_18"],
                    }
                ],
            },
            {
                "file": "/main_2.tf",
                "findings": [
                    {
                        "resource": "aws_s3_bucket.destination_2",
                        "check_ids": ["CKV2_AWS_6", "CKV_AWS_18"],
                    },
                    {
                        "resource": "aws_s3_bucket.destination_3",
                        "check_ids": ["CKV2_AWS_6", "CKV_AWS_18"],
                    },
                ],
            },
        ]
    }


def _run_cross_file_fixture() -> list:
    # the same resource address, aws_s3_bucket.this, in two different files, both failing CKV_AWS_18
    test_folder = Path(__file__).parent / "fixtures_baseline_cross_file"
    return [Runner().run(root_folder=str(test_folder), runner_filter=RunnerFilter(checks=["CKV_AWS_18"]))]


def _baseline_from(tmp_path: Path, failed_checks: list) -> Baseline:
    baseline_file = tmp_path / ".checkov.baseline"
    baseline_file.write_text(json.dumps({"failed_checks": failed_checks}))
    baseline = Baseline()
    baseline.from_json(str(baseline_file))
    return baseline


def test_baseline_only_suppresses_the_file_it_recorded(tmp_path):
    # given a baseline recorded when only /main.tf had the violation
    baseline = _baseline_from(
        tmp_path,
        [{"file": "/main.tf", "findings": [{"resource": "aws_s3_bucket.this", "check_ids": ["CKV_AWS_18"]}]}],
    )
    reports = _run_cross_file_fixture()

    # when
    baseline.compare_and_reduce_reports(reports)

    # then the unrelated resource with the same address in another file is still reported
    assert [(c.file_path, c.resource) for c in reports[0].failed_checks] == [
        ("/environments/staging/main.tf", "aws_s3_bucket.this")
    ]


def test_baseline_created_from_the_scan_suppresses_both_files(tmp_path):
    # given a baseline created from the same scan
    created = Baseline()
    for report in _run_cross_file_fixture():
        created.add_findings_from_report(report)
    baseline = _baseline_from(tmp_path, created.to_dict()["failed_checks"])
    reports = _run_cross_file_fixture()

    # when
    baseline.compare_and_reduce_reports(reports)

    # then
    assert reports[0].failed_checks == []


def test_baseline_file_path_with_windows_separators_still_matches(tmp_path):
    # given a baseline created on Windows
    baseline = _baseline_from(
        tmp_path,
        [
            {
                "file": "\\environments\\staging\\main.tf",
                "findings": [{"resource": "aws_s3_bucket.this", "check_ids": ["CKV_AWS_18"]}],
            }
        ],
    )
    reports = _run_cross_file_fixture()

    # when
    baseline.compare_and_reduce_reports(reports)

    # then
    assert [(c.file_path, c.resource) for c in reports[0].failed_checks] == [("/main.tf", "aws_s3_bucket.this")]


def test_baseline_entry_without_file_matches_any_file(tmp_path):
    # given a hand-written baseline entry without a file key
    baseline = _baseline_from(
        tmp_path,
        [{"findings": [{"resource": "aws_s3_bucket.this", "check_ids": ["CKV_AWS_18"]}]}],
    )
    reports = _run_cross_file_fixture()

    # when
    baseline.compare_and_reduce_reports(reports)

    # then it keeps the resource + check id matching
    assert reports[0].failed_checks == []
