from typing import Optional, List, Set

import pytest

from checkov.main import checkov_runners
from checkov.runner_filter import RunnerFilter


@pytest.mark.parametrize(
    "input_frameworks,input_skip_frameworks,expected_frameworks",
    [
        (["all"], None, {"all"}),
        (None, None, {"all"}),
        (["terraform"], None, {"terraform"}),
        (["cloudformation", "serverless"], None, {"cloudformation", "serverless"}),
        (
            ["all"],
            ["terraform", "secrets"],
            {
                "arm",
                "cloudformation",
                "dockerfile",
                "helm",
                "json",
                "kubernetes",
                "serverless",
                "terraform_plan",
                "github_configuration",
                "gitlab_configuration",
                "kustomize",
                "sca_package"
            },
        ),
        (["cloudformation", "serverless"], ["serverless", "secrets"], {"cloudformation"}),
    ],
    ids=["all", "none", "terraform", "multiple", "all_with_skip", "multiple_with_skip"],
)
def test_runner_filter_constructor_framework(
    input_frameworks: Optional[List[str]], input_skip_frameworks: Optional[List[str]], expected_frameworks: Set[str]
):
    # when
    runner_filter = RunnerFilter(
        framework=input_frameworks,
        runners=checkov_runners,
        skip_framework=input_skip_frameworks,
    )

    # then
    assert set(runner_filter.framework) == expected_frameworks
