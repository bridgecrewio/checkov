import os
from pathlib import Path
from unittest import mock

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


@mock.patch.dict(os.environ, {"CHECKOV_EXPERIMENTAL_TERRAFORM_MANAGED_MODULES": "True"})
def test_runner_with_tf_managed_modules():
    # given
    root_dir = Path(__file__).parent / "data/tf_managed_modules"

    # when
    result = Runner().run(
        root_folder=str(root_dir),
        runner_filter=RunnerFilter(checks=["CKV_AWS_338"], framework=["terraform"], download_external_modules=False),
    )

    # then
    summary = result.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 1
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    failed_resources = [check.resource for check in result.failed_checks]
    expected_failed_resources = ["module.log_group.aws_cloudwatch_log_group.this[0]"]

    assert failed_resources == expected_failed_resources


# test can be removed after setting this flow as default
@mock.patch.dict(os.environ, {"CHECKOV_EXPERIMENTAL_TERRAFORM_MANAGED_MODULES": "False"})
def test_runner_without_tf_managed_modules():
    # given
    root_dir = Path(__file__).parent / "data/tf_managed_modules"

    # when
    result = Runner().run(
        root_folder=str(root_dir),
        runner_filter=RunnerFilter(checks=["CKV_AWS_338"], framework=["terraform"], download_external_modules=False),
    )

    # then
    summary = result.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0
