from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.main import DEFAULT_RUNNERS
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture


TESTS_DIR = Path(__file__).parent.parent / "tests"


def test_all_frameworks_are_tested() -> None:
    # given
    checkov_runners = {value for attr, value in CheckType.__dict__.items() if not attr.startswith("__")}

    # remove frameworks, which are not applicable
    checkov_runners.difference_update(
        {
            CheckType.BITBUCKET_CONFIGURATION,
            CheckType.GITHUB_CONFIGURATION,
            CheckType.GITLAB_CONFIGURATION,
            CheckType.JSON,
            CheckType.SCA_IMAGE,
            CheckType.SCA_PACKAGE,
            CheckType.YAML,
        }
    )

    assert checkov_runners == {
        CheckType.ANSIBLE,
        CheckType.ARGO_WORKFLOWS,
        CheckType.ARM,
        CheckType.AZURE_PIPELINES,
        CheckType.BICEP,
        CheckType.BITBUCKET_PIPELINES,
        CheckType.CDK,
        CheckType.CIRCLECI_PIPELINES,
        CheckType.CLOUDFORMATION,
        CheckType.DOCKERFILE,
        CheckType.GITHUB_ACTIONS,
        CheckType.GITLAB_CI,
        CheckType.HELM,
        CheckType.KUBERNETES,
        CheckType.KUSTOMIZE,
        CheckType.OPENAPI,
        CheckType.SAST,
        CheckType.SAST_JAVA,
        CheckType.SAST_PYTHON,
        CheckType.SAST_JAVASCRIPT,
        CheckType.SAST_TYPESCRIPT,
        CheckType.SAST_GOLANG,
        CheckType.SECRETS,
        CheckType.SERVERLESS,
        CheckType.TERRAFORM,
        CheckType.TERRAFORM_JSON,
        CheckType.TERRAFORM_PLAN,
        CheckType.POLICY_3D
    }, "Don't forget to add a test case for the new runner here"


def test_ansible_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.ANSIBLE)


def test_argo_workflows_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.ARGO_WORKFLOWS)


def test_arm_framework(caplog: LogCaptureFixture) -> None:
    excluded_paths = ["arm/parser/examples/json/with_comments.json$"]

    run_framework_test(caplog=caplog, framework=CheckType.ARM, excluded_paths=excluded_paths)


def test_azure_pipelines_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.AZURE_PIPELINES)


def test_bicep_framework(caplog: LogCaptureFixture) -> None:
    excluded_paths = ["bicep/examples/malformed.bicep$"]

    run_framework_test(caplog=caplog, framework=CheckType.BICEP, excluded_paths=excluded_paths)


def test_bitbucket_pipelines_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.BITBUCKET_PIPELINES)


@pytest.mark.xfail(reason="locally it works, but in CI no results")
def test_cdk_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.CDK)


def test_circleci_pipelines_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.CIRCLECI_PIPELINES)


def test_cloudformation_framework(caplog: LogCaptureFixture) -> None:
    excluded_paths = [
        "cloudformation/parser/cfn_bad_name.yaml$",
        "cloudformation/parser/cfn_with_ref_bad.yaml$",
        "cloudformation/parser/success_triple_quotes_string.json$",
        "cloudformation/runner/resources/invalid.json$",
        "cloudformation/runner/resources/invalid.yaml$",
        "cloudformation/runner/resources/invalid_properties.json$",
        "cloudformation/runner/resources/invalid_properties.yaml$",
    ]

    run_framework_test(caplog=caplog, framework=CheckType.CLOUDFORMATION, excluded_paths=excluded_paths)


def test_dockerfile_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.DOCKERFILE)


def test_github_actions_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.GITHUB_ACTIONS)


def test_gitlab_ci_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.GITLAB_CI)


def test_helm_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.HELM)


def test_kubernetes_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.KUBERNETES)


@pytest.mark.skip(reason="kustomize needs a context to do a proper scan, which is hard to set here")
def test_kustomize_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.KUSTOMIZE)


def test_openapi_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.OPENAPI)


def test_secrets_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.SECRETS)


def test_serverless_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.SERVERLESS)


def test_terraform_framework(caplog: LogCaptureFixture) -> None:
    excluded_paths = [
        "terraform/runner/resources/example/invalid.tf$",
        "terraform/runner/resources/invalid_terraform_syntax/bad_tf_1.tf$",
        "terraform/runner/resources/invalid_terraform_syntax/bad_tf_2.tf$",
        "terraform/runner/resources/unbalanced_eval_brackets/main.tf$",
        "terraform/parser/resources/hcl_timeout/main.tf$",
    ]

    run_framework_test(caplog=caplog, framework=CheckType.TERRAFORM, excluded_paths=excluded_paths)


def test_terraform_json_framework(caplog: LogCaptureFixture) -> None:
    run_framework_test(caplog=caplog, framework=CheckType.TERRAFORM_JSON)


def test_terraform_plan_framework(caplog: LogCaptureFixture) -> None:
    excluded_paths = [
        "arm/parser/examples/json/with_comments.json$",
        "cloudformation/parser/fail.json$",
        "cloudformation/parser/success_triple_quotes_string.json$",
        "cloudformation/runner/resources/invalid.json$",
    ]

    run_framework_test(caplog=caplog, framework=CheckType.TERRAFORM_PLAN, excluded_paths=excluded_paths)


def run_framework_test(caplog: LogCaptureFixture, framework: str, excluded_paths: list[str] | None = None) -> None:
    # given
    caplog.set_level(logging.ERROR)
    runner_registry = RunnerRegistry(
        "", RunnerFilter(framework=[framework], excluded_paths=excluded_paths), *DEFAULT_RUNNERS
    )

    # when
    scan_reports = runner_registry.run(root_folder=str(TESTS_DIR))

    # then
    for report in scan_reports:
        assert report.failed_checks
        assert not report.parsing_errors, f"Found parsing errors for framework '{report.check_type}'"

    assert not caplog.text, caplog.text
