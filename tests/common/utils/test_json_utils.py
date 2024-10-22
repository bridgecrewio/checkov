import json
from datetime import datetime
from typing import Dict, Any

import pytest
from lark import Tree

from checkov.common.util.json_utils import CustomJSONEncoder


@pytest.mark.parametrize(
    "input_dict",
    [
        ({"key": {"v", "val", "value"}}),
        ({"key": datetime.now()}),
        ({"key": Tree("data", ["child_1", "child_2"])}),
        ({"key": lambda x: x}),
    ],
    ids=["set", "date", "lark_tree", "function"],
)
def test_custom_json_encoder(input_dict: Dict[str, Any]):
    # when
    result = json.dumps(input_dict, cls=CustomJSONEncoder)

    # then
    # this assertion should never fail, but json.dumps() could
    assert isinstance(result, str)
