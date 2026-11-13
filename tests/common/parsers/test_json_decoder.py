import json

from checkov.common.parsers.json.decoder import Decoder
from checkov.common.parsers.node import DictNode, ListNode


def test_decode_arrays_with_marks():
    # given
    content = '{\n  "schemes": ["https", "http"],\n  "empty": [],\n  "nested": [[1], {"a": [true]}]\n}\n'

    # when
    result = json.loads(content, cls=Decoder)

    # then
    assert isinstance(result, DictNode)
    assert isinstance(result["schemes"], ListNode)
    assert result["schemes"] == ["https", "http"]
    assert result["schemes"].start_mark.line == 1
    assert isinstance(result["empty"], ListNode)
    assert result["empty"] == []
    assert isinstance(result["nested"][0], ListNode)
    assert isinstance(result["nested"][1]["a"], ListNode)
    assert result["nested"] == [[1], {"a": [True]}]
