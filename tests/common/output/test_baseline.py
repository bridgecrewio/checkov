import argparse
import json
from pathlib import Path

import pytest

from checkov.common.output.baseline import Baseline, BaselineError
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


def test_from_json_missing_file(tmp_path):
    # given
    baseline_path = tmp_path / "missing.json"

    # when/then
    with pytest.raises(BaselineError) as exc_info:
        Baseline().from_json(str(baseline_path))

    assert "Unable to read baseline file" in str(exc_info.value)


def test_from_json_directory(tmp_path):
    # given
    baseline_path = tmp_path / "baseline_dir"
    baseline_path.mkdir()

    # when/then
    with pytest.raises(BaselineError) as exc_info:
        Baseline().from_json(str(baseline_path))

    assert "Unable to read baseline file" in str(exc_info.value)


def test_from_json_invalid_json(tmp_path):
    # given
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text("not json at all")

    # when/then
    with pytest.raises(BaselineError) as exc_info:
        Baseline().from_json(str(baseline_path))

    assert "Unable to parse baseline file" in str(exc_info.value)


def test_from_json_without_json_object(tmp_path):
    # given
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(json.dumps([]))

    # when/then
    with pytest.raises(BaselineError) as exc_info:
        Baseline().from_json(str(baseline_path))

    assert "expected a JSON object, got list" in str(exc_info.value)


def test_from_json_with_invalid_failed_checks(tmp_path):
    # given
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(json.dumps({"failed_checks": "not a list"}))

    # when/then
    with pytest.raises(BaselineError) as exc_info:
        Baseline().from_json(str(baseline_path))

    assert "'failed_checks' must be a list, got str" in str(exc_info.value)


def test_from_json_with_valid_file(tmp_path):
    # given
    failed_checks = [{"file": "/main.tf", "findings": [{"resource": "aws_s3_bucket.bad", "check_ids": ["CKV_AWS_20"]}]}]
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(json.dumps({"failed_checks": failed_checks}))

    # when
    baseline = Baseline()
    baseline.from_json(str(baseline_path))

    # then
    assert baseline.failed_checks == failed_checks
