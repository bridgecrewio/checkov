from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


def test_dynamics():
    # given
    test_files_dir = Path(__file__).parent.parent / "resources/dynamic_lambda_function"

    # when
    report = Runner().run(
        root_folder=str(test_files_dir),
        runner_filter=RunnerFilter(
            checks=[
                "CKV_AWS_45",
                "CKV_AWS_116",
                "CKV_AWS_173",
                "CKV_AWS_272",
            ]
        ),
    )

    # then
    summary = report.get_summary()

    assert summary["passed"] == 2
    assert summary["failed"] == 2
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0
