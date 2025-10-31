import pytest

from checkov.common.graph.graph_builder.graph_components.blocks import Block


@pytest.mark.parametrize("input_key, expected_key", (
        ("a.b", "$.a.b"),
        ("a.0", "$.a[0]"),
        ("a.0.b.1.2.c", "$.a[0].b[1][2].c"),
        ("a.0./mock-part-of-key.d.e.1", "$.a[0].\"/mock-part-of-key\".d.e[1]"),
        ("a.0.Fn::Region.d.e.1", "$.a[0].\"Fn::Region\".d.e[1]")
))
def test__get_jsonpath_key(input_key: str, expected_key: str) -> None:
    result = Block._get_jsonpath_key(input_key)
    assert result == expected_key
