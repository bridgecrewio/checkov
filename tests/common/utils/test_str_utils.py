import pytest

from checkov.common.util.str_utils import removeprefix
from checkov.common.util.str_utils import convert_to_seconds


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


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("503s", 503),
        ("3h", 10800),
        ("8m", 480),
        ("2d", 172800),
        ("1w", 604800),
    ],
    ids=["503 seconds", "3 hours", "8 minutes", "2 days", "1 week"],
)
def test_convert_to_seconds(input_str: str, expected: str) -> None:
    assert convert_to_seconds(input_str) == expected


@pytest.mark.parametrize(
    "input_str",
    [
        "4",
        "5ss",
        "6c",
    ],
    ids=["no char", "two chars", "wrong char"]
)
def test_convert_to_seconds_fails(input_str: str) -> None:
    with pytest.raises(Exception) as a:
        convert_to_seconds(input_str)
        print(a)
