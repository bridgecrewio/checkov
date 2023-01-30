import os
from unittest import mock

import pytest

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@pytest.mark.parametrize(
    "block_index,expected_res",
    [
        (0, {'bucket_a', 'bucket_b'}),
        (1, {'key1': '${var.a}', 'key2': '${var.b}'}),
        (2, None)
    ]
)
def test_for_each_resource(block_index, expected_res):
    from checkov.terraform.graph_builder.foreach_handler import ForeachHandler
    from checkov.terraform.graph_manager import TerraformGraphManager
    dir_name = 'foreach_resources/static_foreach_value'
    resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, 'resources', dir_name))

    graph_manager = TerraformGraphManager('m', ['m'])
    local_graph, tf_definitions = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=False)
    foreach_handler = ForeachHandler(local_graph)
    res = foreach_handler._get_foreach_statement(block_index)
    assert res == expected_res
