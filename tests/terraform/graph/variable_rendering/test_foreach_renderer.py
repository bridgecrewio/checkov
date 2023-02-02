import os
from unittest import mock

import pytest

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


def assert_object_equal(res, expected_res):
    assert len(res) == len(expected_res)
    if isinstance(res, dict):
        assert dict(sorted(res.items(), key=lambda item: item[0])) == dict(sorted(expected_res.items(), key=lambda item: item[0]))
    if isinstance(res, list):
        assert res.sort() == expected_res.sort()


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
def test_static_foreach_resource(block_index, expected_res, obj):
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


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
def test_dynamic_foreach_resource():
    from checkov.terraform.graph_builder.foreach_handler import ForeachHandler
    from checkov.terraform.graph_manager import TerraformGraphManager
    dir_name = 'foreach_resources/dynamic_foreach_value'
    resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, 'resources', dir_name))

    graph_manager = TerraformGraphManager('m', ['m'])
    local_graph, tf_definitions = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=False)
    foreach_handler = ForeachHandler(local_graph)
    res = foreach_handler._handle_dynamic_statement([6, 7, 8, 9, 10])
    expected_res = {
        6: {'a_group': 'eastus', 'another_group': 'westus2'}, 7: ['s3-bucket-a', 's3-bucket-b'], 8: 5, 9: 2, 10: None
    }
    assert_object_equal(res, expected_res)


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
def test_foreach_resource():
    from checkov.terraform.graph_builder.foreach_handler import ForeachHandler
    from checkov.terraform.graph_manager import TerraformGraphManager
    dir_name = 'foreach_resources'
    resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, 'resources', dir_name))

    graph_manager = TerraformGraphManager('m', ['m'])
    local_graph, tf_definitions = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=False)
    foreach_handler = ForeachHandler(local_graph)
    res = foreach_handler._get_statements([6, 7, 8, 9, 10, 19, 20, 21, 22, 23, 24, 25])
    expected_res = {
        6: {'a_group': 'eastus', 'another_group': 'westus2'},
        7: ['s3-bucket-a', 's3-bucket-b'],
        8: 5,
        9: 2,
        10: None,
        19: ['bucket_a', 'bucket_b'],
        20: {'key1': '${var.a}', 'key2': '${var.b}'},
        21: None,
        22: None,
        23: 5,
        24: None,
        25: None
    }
    for key, _ in expected_res.items():
        if isinstance(expected_res[key], (list, dict)):
            assert_object_equal(res[key], expected_res[key])
        else:
            assert res[key] == expected_res[key]
