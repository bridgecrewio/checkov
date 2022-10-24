import pytest

from checkov.common.util.str_utils import removeprefix


@pytest.mark.parametrize(
    "input_str,prefix,expected",
    [
        ("/path/to/something", "/path", "/to/something"),
        ("path/to/something", "path", "/to/something"),
        ("/path/path/to/something", "/path", "/path/to/something"),
        ("/path/to/something", "/not_found", "/path/to/something"),
        ("/path/to/something", "", "/path/to/something"),
    ],
    ids=["abs_path", "rel_path", "double_path", "not_found", "empty"],
)
def test_removeprefix(input_str: str, prefix: str, expected: str) -> None:
    assert removeprefix(input_str, prefix) == expected
