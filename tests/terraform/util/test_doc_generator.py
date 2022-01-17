from typing import List, Set, Optional

import pytest

from checkov.common.util.docs_generator import get_checks


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
        (["all"], {"arm", "Cloudformation", "dockerfile", "Kubernetes", "secrets", "serverless", "Terraform",
                   "github_configuration", "gitlab_configuration"}),
        (None, {"arm", "Cloudformation", "dockerfile", "Kubernetes", "secrets", "serverless", "Terraform",
                "github_configuration", "gitlab_configuration"}),
        (["terraform"], {"Terraform"}),
        (["cloudformation", "serverless"], {"Cloudformation", "serverless"}),
    ],
    ids=["all", "none", "terraform", "multiple"],
)
def test_get_checks_returned_frameworks(input_frameworks: Optional[List[str]], expected_frameworks: Set[str]):
    # when
    checks = get_checks(input_frameworks)

    # then
    actual_frameworks = {c[4] for c in checks}

    assert actual_frameworks == expected_frameworks
