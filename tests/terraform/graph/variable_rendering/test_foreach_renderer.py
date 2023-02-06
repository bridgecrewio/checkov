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


def build_and_get_graph_by_path(path):
    from checkov.terraform.graph_manager import TerraformGraphManager
    resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, 'resources', path))
    graph_manager = TerraformGraphManager('m', ['m'])
    local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=False)
    return local_graph


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
    dir_name = 'foreach_resources/static_foreach_value'
    local_graph = build_and_get_graph_by_path(dir_name)
    foreach_handler = ForeachHandler(local_graph)
    res = foreach_handler._get_static_foreach_statement(block_index)
    if obj:
        assert_object_equal(res, expected_res)
    else:
        assert res == expected_res


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
def test_dynamic_foreach_resource():
    from checkov.terraform.graph_builder.foreach_handler import ForeachHandler
    dir_name = 'foreach_resources/dynamic_foreach_value'
    local_graph = build_and_get_graph_by_path(dir_name)
    foreach_handler = ForeachHandler(local_graph)
    res = foreach_handler._handle_dynamic_statement([6, 7, 8, 9, 10])
    expected_res = {
        6: {'a_group': 'eastus', 'another_group': 'westus2'}, 7: ['s3-bucket-a', 's3-bucket-b'], 8: 5, 9: 2, 10: None
    }
    assert_object_equal(res, expected_res)


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
def test_foreach_resource():
    from checkov.terraform.graph_builder.foreach_handler import ForeachHandler
    dir_name = 'foreach_resources'
    local_graph = build_and_get_graph_by_path(dir_name)
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


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
def test_build_sub_graph():
    from checkov.terraform.graph_builder.foreach_handler import ForeachHandler
    dir_name = 'foreach_resources'
    local_graph = build_and_get_graph_by_path(dir_name)
    foreach_handler = ForeachHandler(local_graph)
    blocks = [6, 7, 8, 9, 10, 21, 22, 24, 25]
    sub_graph = foreach_handler._build_sub_graph(blocks)
    assert all(sub_graph.vertices[i] for i in blocks)
    assert not all(sub_graph.vertices[i] for i in range(len(sub_graph.vertices)))
    assert len(sub_graph.edges) < len(local_graph.edges)


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
def test_new_resources_count():
    from checkov.terraform.graph_builder.foreach_handler import ForeachHandler
    dir_name = 'foreach_examples/count_dup_resources'
    local_graph = build_and_get_graph_by_path(dir_name)

    vertices_names = [vertice.name for vertice in local_graph.vertices]
    main_count_resource = 'aws_s3_bucket.count_var_resource'
    assert main_count_resource in vertices_names

    foreach_handler = ForeachHandler(local_graph)
    foreach_handler.handle_foreach_rendering({'resource': [3], 'module': []})
    for i, resource in enumerate([local_graph.vertices[7], local_graph.vertices[8], local_graph.vertices[9]]):
        assert resource.name.endswith(f"[{i}]")
        assert resource.id.endswith(f"[{i}]")
        assert list(resource.config['aws_s3_bucket'].keys())[0].endswith(f'[{i}]')
    new_vertices_names = [vertice.name for vertice in local_graph.vertices]
    assert main_count_resource not in new_vertices_names


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
def test_new_resources_foreach():
    from checkov.terraform.graph_builder.foreach_handler import ForeachHandler
    dir_name = 'foreach_examples/foreach_dup_resources'
    local_graph = build_and_get_graph_by_path(dir_name)
    foreach_handler = ForeachHandler(local_graph)
    foreach_handler.handle_foreach_rendering({'resource': [0, 1], 'module': []})
    for resource in [local_graph.vertices[3], local_graph.vertices[4], local_graph.vertices[5], local_graph.vertices[6]]:
        assert resource.name.endswith("[bucket_a]") or resource.name.endswith("[bucket_b]")
        assert resource.id.endswith("[bucket_a]") or resource.id.endswith("[bucket_b]")
        config_name = list(resource.config['aws_s3_bucket'].keys())[0]
        assert config_name.endswith("[bucket_a]") or config_name.endswith("[bucket_b]")
