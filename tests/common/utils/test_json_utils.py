import json
from datetime import datetime
from typing import Dict, Any

import pytest
from lark import Tree

from checkov.common.util.json_utils import CustomJSONEncoder


@pytest.mark.parametrize(
    "input_dict",
    [
        pytest.param({"key": {"v", "val", "value"}}, id="set"),
        pytest.param({"key": datetime.now()}, id="date"),
        pytest.param({"key": Tree("data", ["child_1", "child_2"])}, id="lark_tree"),
        pytest.param({"key": lambda x: x}, id="function"),
        pytest.param({("key", "key2"): "value"}, id="tuple_key"),
    ],
)
def test_custom_json_encoder(input_dict: Dict[str, Any]):
    # when
    result = json.dumps(input_dict, cls=CustomJSONEncoder)

    # then
    # this assertion should never fail, but json.dumps() could
    assert isinstance(result, str)
