import os
import pytest

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@pytest.mark.parametrize(
    "block_index,expected_res,obj",
    [
        (0, ['bucket_a', 'bucket_b'], True),
        (1, {'key1': '${var.a}', 'key2': '${var.b}'}, True),
        (2, None, False),
        (3, None, False),
        (4, 5, False),
        (5, None, False),
        (6, None, False)
    ]
)
def test_for_each_resource(block_index, expected_res, obj):
    from checkov.terraform.graph_builder.foreach_handler import ForeachHandler
    from checkov.terraform.graph_manager import TerraformGraphManager
    dir_name = 'foreach_resources/static_foreach_value'
    resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, 'resources', dir_name))

    graph_manager = TerraformGraphManager('m', ['m'])
    local_graph, tf_definitions = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=False)
    foreach_handler = ForeachHandler(local_graph)
    res = foreach_handler._get_foreach_statement(block_index)
    if obj:
        assert_object_equal(res, expected_res)
    else:
        assert res == expected_res


def assert_object_equal(res, expected_res):
    assert len(res) == len(expected_res)
    if isinstance(res, dict):
        assert dict(sorted(res.items(), key=lambda item: item[0])) == dict(sorted(expected_res.items(), key=lambda item: item[0]))
    if isinstance(res, list):
        assert res.sort() == expected_res.sort()

