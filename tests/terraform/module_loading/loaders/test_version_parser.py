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
