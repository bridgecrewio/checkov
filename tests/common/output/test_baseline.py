import argparse
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
