from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.bridgecrew.check_type import CheckType
from checkov.docs_generator import get_checks


def test_get_checks_returned_check_number():
    checks = get_checks(["all"])
    assert len(checks) > 0

    checks = get_checks()
    assert len(checks) > 0

    checks = get_checks(["example"])
    assert len(checks) == 0


@pytest.mark.parametrize(
    "input_frameworks,expected_frameworks",
    [
        (
            ["all"],
            {
                "Ansible",
                "Argo Workflows",
                "arm",
                "Azure Pipelines",
                "Bicep",
                "Cloudformation",
                "dockerfile",
                "Kubernetes",
                "secrets",
                "serverless",
                "Terraform",
                "github_configuration",
                "gitlab_configuration",
                "bitbucket_configuration",
                "bitbucket_pipelines",
                "circleci_pipelines",
                "github_actions",
                "OpenAPI",
                "gitlab_ci",
            },
        ),
        (
            None,
            {
                "Ansible",
                "Argo Workflows",
                "arm",
                "Azure Pipelines",
                "Bicep",
                "Cloudformation",
                "dockerfile",
                "Kubernetes",
                "secrets",
                "serverless",
                "Terraform",
                "github_configuration",
                "bitbucket_pipelines",
                "circleci_pipelines",
                "gitlab_configuration",
                "bitbucket_configuration",
                "github_actions",
                "OpenAPI",
                "gitlab_ci",
            },
        ),
        (["terraform"], {"Terraform"}),
        (["cloudformation", "serverless"], {"Cloudformation", "serverless"}),
    ],
    ids=["all", "none", "terraform", "multiple"],
)
def test_get_checks_returned_frameworks(input_frameworks: list[str] | None, expected_frameworks: set[str]):
    # when
    checks = get_checks(input_frameworks)

    # then
    actual_frameworks = {c[4] for c in checks}

    assert actual_frameworks == expected_frameworks


def test_get_checks_graph_registries():
    """
    For a runner that has graph_checks, the graph registry for that runner should be loaded and returned by the
    get_checks method.
    """
    checkov_runners = [value for attr, value in CheckType.__dict__.items() if not attr.startswith("__")]
    for runner in checkov_runners:
        graph_registry = get_graph_checks_registry(runner)
        if Path(graph_registry.checks_dir).is_dir():
            assert f'get_graph_checks_registry("{runner}")' in inspect.getsource(get_checks)
