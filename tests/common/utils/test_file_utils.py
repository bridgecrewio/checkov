import os

from checkov.common.util.file_utils import read_file_safe, get_file_size_safe

def test_sanity_read_file():
    file_to_check = f"{os.path.dirname(os.path.realpath(__file__))}/resources/existing_file"
    file_content = read_file_safe(file_to_check)
    assert file_content == "BLA"


def test_failure_read_file():
    file_to_check = f"non_existing_file"
    file_content = read_file_safe(file_to_check)
    assert file_content == ""


def test_sanity_get_file_size():
    file_to_check = f"{os.path.dirname(os.path.realpath(__file__))}/resources/existing_file"
    file_size = get_file_size_safe(file_to_check)
    assert file_size == 3


def test_failure_get_file_size():
    file_to_check = f"non_existing_file"
    file_size = get_file_size_safe(file_to_check)
    assert file_size == -1
