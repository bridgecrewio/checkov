import pytest

from checkov.terraform.module_loading.loaders.versions_parser import get_version_constraints


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("1.2.0", "=1.2.0"),
        ("1.2.0-rc1", "=1.2.0rc1"),
        (">= 1.2.0, < 2.0.0", ">=1.2.0,<2.0.0"),
        ("not-a-version", ""),
        ("<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=<=>=1.2.3", ""),
    ],
    ids=["sem_ver", "pre_release", "multi", "not_a_version", "back_tracking"],
)
def test_get_version_constraints(input_str: str, expected: str) -> None:
    result = get_version_constraints(input_str)

    assert ",".join(str(version) for version in result) == expected


@pytest.mark.parametrize(
    "input_str,other_version,expected",
    [
        ("~> 4.1.0", "4.1.2", True),
        ("~> 4.1.0", "4.2.0", False),
        ("~> 4.1", "4.11.0", True),
        ("~> 4.1", "5.0.0", False),
        ("~> 1.2.3.4", "1.2.3.9", True),
        ("~> 1.2.3.4", "1.2.4", False),
    ],
)
def test_versions_matching_pessimistic(input_str: str, other_version: str, expected: bool) -> None:
    version_constraint = get_version_constraints(input_str)[0]

    assert version_constraint.versions_matching(other_version) == expected
