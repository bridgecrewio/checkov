from typing import Any

import pytest

from checkov.common.util.data_structures_utils import find_in_dict


@pytest.mark.parametrize(
    "key_path,expected_value",
    [
        ("key_99", None),
        ("key_1/key_2/key_3", None),
        ("key_1/key_2/[10]/key_3", None),
        ("key_1/key_5", "string"),
        ("key_1/key_2/[0]/key_3", 1),
        ("key_1/key_2/[1]/key_4", True),
    ],
    ids=["key_not_exists", "nested_key_not_exists", "index_not_exists", "key", "index", "index_1"],
)
def test_find_in_dict(key_path: str, expected_value: Any) -> None:
    input_dict = {
        "key_1": {
            "key_2": [
                {
                    "key_3": 1,
                },
                {
                    "key_4": True,
                },
            ],
            "key_5": "string",
        }
    }

    # when
    actual_value = find_in_dict(input_dict, key_path)

    # then
    assert actual_value == expected_value
