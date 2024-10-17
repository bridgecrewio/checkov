from pathlib import Path
from typing import Dict

from checkov.common.util.parser_utils import eval_string
from checkov.terraform.tf_parser import load_or_die_quietly


def test_eval_string_to_list() -> None:
    # given
    expected = ["a", "b", "c"]

    # when
    actual = eval_string('["a", "b", "c"]')

    assert actual == expected


def test__load_or_die_quietly_with_bom() -> None:
    # given
    test_file = Path(__file__).parent / "resources/file_bom/with_bom.tf"
    parsing_errors: Dict[str, Exception] = {}

    # when
    definition = load_or_die_quietly(file=test_file, parsing_errors=parsing_errors)

    # then
    assert not parsing_errors
    assert definition == {
        "resource": [
            {
                "aws_s3_bucket": {
                    "example": {"bucket": ["example"], "__start_line__": 1, "__end_line__": 3},
                },
            }
        ]
    }


def test__load_or_die_quietly_without_bom() -> None:
    # given
    test_file = Path(__file__).parent / "resources/file_bom/without_bom.tf"
    parsing_errors: Dict[str, Exception] = {}

    # when
    definition = load_or_die_quietly(file=test_file, parsing_errors=parsing_errors)

    # then
    assert not parsing_errors
    assert definition == {
        "resource": [
            {
                "aws_s3_bucket": {
                    "example": {"bucket": ["example"], "__start_line__": 1, "__end_line__": 3},
                },
            }
        ]
    }


def test__load_or_die_quietly_with_timeout() -> None:
    test_file = Path(__file__).parent / "resources/hcl_timeout/main.tf"
    parsing_errors: Dict[str, Exception] = {}

    # when
    definition = load_or_die_quietly(file=test_file, parsing_errors=parsing_errors)

    # then
    assert parsing_errors
    assert str(test_file) in parsing_errors
    assert 'seconds to parse' in str(parsing_errors[str(test_file)])