from pathlib import PurePosixPath

import pytest

from checkov.common.util.str_utils import removeprefix
from checkov.common.util.str_utils import convert_to_seconds
from checkov.common.util.str_utils import get_rootless_path


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


@pytest.mark.parametrize(
    "input_path,expected",
    [
        ("/my-project.api\\client\\Dockerfile.base", "my-project.api\\client\\Dockerfile.base"),
        ("C:\\work\\repo\\Dockerfile", "work\\repo\\Dockerfile"),
        ("\\\\srv\\share\\repo\\Dockerfile", "repo\\Dockerfile"),
        ("\\work\\repo\\Dockerfile", "work\\repo\\Dockerfile"),
        ("my-project.api\\client\\Dockerfile.base", "my-project.api\\client\\Dockerfile.base"),
        ("/my-project.api/client/Dockerfile.base", "my-project.api/client/Dockerfile.base"),
        ("my-project.api/client/Dockerfile.base", "my-project.api/client/Dockerfile.base"),
        ("/a\\b\\c\\d\\Dockerfile", "a\\b\\c\\d\\Dockerfile"),
        ("Dockerfile", "Dockerfile"),
    ],
    ids=[
        "win_slash_prefixed",
        "win_drive_absolute",
        "win_unc",
        "win_root_relative",
        "win_plain_relative",
        "posix_slash_prefixed",
        "posix_relative",
        "nested_deep",
        "single_file",
    ],
)
def test_get_rootless_path(input_path: str, expected: str) -> None:
    assert get_rootless_path(input_path) == expected


def test_get_rootless_path_must_not_be_used_on_posix() -> None:
    """Documents why callers guard on ``IS_WINDOWS``.

    A leading '//' is a valid POSIX root, but Windows semantics read it as a UNC share
    and drop two segments. Callers must keep the ``anchor`` expression on POSIX.
    """
    input_path = "//srv/share/repo/Dockerfile"

    posix_result = input_path.replace(PurePosixPath(input_path).anchor, "", 1)

    assert posix_result == "srv/share/repo/Dockerfile"
    assert get_rootless_path(input_path) != posix_result
