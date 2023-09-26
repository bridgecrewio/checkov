from pathlib import Path

from checkov.common.util.parser_utils import eval_string
from checkov.terraform.tf_parser import load_or_die_quietly


def test_eval_string_to_list():
    # given
    expected = ["a", "b", "c"]

    # when
    actual = eval_string('["a", "b", "c"]')

    assert actual == expected


def test__load_or_die_quietly_with_bom():
    # given
    test_file = Path(__file__).parent / "resources/file_bom/with_bom.tf"
    parsing_errors = {}

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


def test__load_or_die_quietly_without_bom():
    # given
    test_file = Path(__file__).parent / "resources/file_bom/without_bom.tf"
    parsing_errors = {}

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
