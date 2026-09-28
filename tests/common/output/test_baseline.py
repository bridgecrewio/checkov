import argparse
from pathlib import Path
import json 

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

def test_baseline_same_resource_in_different_directories():
    test_folder = Path(__file__).parent / "fixtures" / "baseline_same_resources"
    check = ["CKV_AWS_356"] 
    report = Runner().run(root_folder=str(test_folder), runner_filter=RunnerFilter(checks=check))
    
    baseline = Baseline()
    baseline.add_findings_from_report(report)

    baseline_dict = baseline.to_dict()
    baseline_dict["failed_checks"] = [item for item in baseline_dict["failed_checks"] if "prod" not in item["file"]]

    baseline_file_path = test_folder / ".checkov.baseline"
    try:
        with open(baseline_file_path, "w") as f :
            json.dump(baseline_dict, f, indent=4)
        baseline.from_json(str(baseline_file_path))

        modified_report = Runner().run(root_folder=str(test_folder), runner_filter=RunnerFilter(checks=check))
        baseline.compare_and_reduce_reports([modified_report])
        failed_files = [item.file_path for item in modified_report.failed_checks]

        assert any("prod" in f for f in failed_files)
        assert not any("dev" in f for f in failed_files)

    finally:
        if baseline_file_path.exists():
            baseline_file_path.unlink()