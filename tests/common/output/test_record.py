import pytest

from checkov.common.output.record import Record


@pytest.mark.parametrize(
    "input_path,expected_path",
    [
        ("s3\\main.tf", "/s3/main.tf"),
        ("s3/main.tf", "/s3/main.tf"),
        ("/abs_path/to/s3/main.tf", "/abs_path/to/s3/main.tf"),
        ("../../s3/main.tf", "/s3/main.tf"),
    ],
    ids=["windows", "rel_path", "abs_path", "recursive_rel_path"],
)
def test_determine_repo_file_path(input_path: str, expected_path: str):
    assert Record._determine_repo_file_path(input_path) == expected_path
