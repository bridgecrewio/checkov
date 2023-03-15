import json
import os
from unittest import mock

import pytest

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


def load_expected_data(path):
    dir_name = os.path.realpath(os.path.join(TEST_DIRNAME, path))
    with open(dir_name, "r") as f:
        return json.load(f)


def assert_object_equal(res, expected_res):
    assert len(res) == len(expected_res)
    if isinstance(res, dict):
        assert dict(sorted(res.items(), key=lambda item: item[0])) == dict(sorted(expected_res.items(), key=lambda item: item[0]))
    if isinstance(res, list):
        assert res.sort() == expected_res.sort()


def build_and_get_graph_by_path(path, render_var=False):
    from checkov.terraform.graph_manager import TerraformGraphManager
    resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, 'resources', path))
    graph_manager = TerraformGraphManager('m', ['m'])
    local_graph, tf_definitions = graph_manager.build_graph_from_source_directory(resources_dir, render_variables=render_var)
    return local_graph, tf_definitions


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
    local_graph = build_and_get_graph_by_path(dir_name)[0]
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
    local_graph = build_and_get_graph_by_path(dir_name)[0]
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
    local_graph = build_and_get_graph_by_path(dir_name)[0]
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
    local_graph = build_and_get_graph_by_path(dir_name)[0]
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
    local_graph = build_and_get_graph_by_path(dir_name)[0]
    vertices_names = [vertice.name for vertice in local_graph.vertices]
    main_count_resource = 'aws_s3_bucket.count_var_resource'
    assert main_count_resource in vertices_names

    foreach_handler = ForeachHandler(local_graph)
    foreach_handler.handle_foreach_rendering({'resource': [3], 'module': []})
    for i, resource in enumerate([local_graph.vertices[3], local_graph.vertices[8], local_graph.vertices[9]]):
        assert resource.name.endswith(f"[{i}]")
        assert resource.id.endswith(f"[{i}]")
        assert list(resource.config['aws_s3_bucket'].keys())[0].endswith(f'[{i}]')
    new_vertices_names = [vertice.name for vertice in local_graph.vertices]
    assert main_count_resource not in new_vertices_names


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
def test_new_resources_foreach():
    from checkov.terraform.graph_builder.foreach_handler import ForeachHandler
    dir_name = 'foreach_examples/foreach_dup_resources'
    local_graph = build_and_get_graph_by_path(dir_name)[0]
    foreach_handler = ForeachHandler(local_graph)
    foreach_handler.handle_foreach_rendering({'resource': [0, 1], 'module': []})
    for resource in [local_graph.vertices[0], local_graph.vertices[1], local_graph.vertices[5], local_graph.vertices[6]]:
        assert resource.name.endswith("[\"bucket_a\"]") or resource.name.endswith("[\"bucket_b\"]")
        assert resource.id.endswith("[\"bucket_a\"]") or resource.id.endswith("[\"bucket_b\"]")
        config_name = list(resource.config['aws_s3_bucket'].keys())[0]
        assert config_name.endswith("[\"bucket_a\"]") or config_name.endswith("[\"bucket_b\"]")


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "True"})
def test_resources_flow():
    dir_name = 'foreach_examples/depend_resources'
    local_graph, _ = build_and_get_graph_by_path(dir_name, render_var=True)
    assert local_graph.vertices_by_block_type['variable'] == [1, 2]
    assert local_graph.vertices_by_block_type['resource'] == [0, 3]

    assert local_graph.vertices_block_name_map['variable'] == {'foreach_map': [1], 'test': [2]}
    assert local_graph.vertices_block_name_map['resource'] == {'aws_s3_bucket.foreach_map[\"bucket_a\"]': [0], 'aws_s3_bucket.foreach_map[\"bucket_b\"]': [3]}

    assert local_graph.edges[0].dest == 2
    assert local_graph.edges[0].origin == 0
    assert local_graph.edges[0].label == 'location'

    assert local_graph.edges[1].dest == 2
    assert local_graph.edges[1].origin == 3
    assert local_graph.edges[1].label == 'location'

    assert len(local_graph.vertices) == 4
    resources = [ver for ver in local_graph.vertices if ver.block_type == 'resource']
    assert len(resources) == 2

    resource_a_name = 'aws_s3_bucket.foreach_map[\"bucket_a\"]'
    assert resources[0].name == resource_a_name
    assert resources[0].id == resource_a_name
    assert resources[0].attributes.get('__address__') == resource_a_name
    assert resources[0].config.get('aws_s3_bucket').get('foreach_map[\"bucket_a\"]').get('__address__') == resource_a_name
    assert resources[0].attributes.get('location') == ["test"]
    assert resources[0].attributes.get('name') == ["bucket_a"]
    assert resources[0].attributes.get('region') == ["us-west-2"]
    assert list(resources[0].config.get('aws_s3_bucket').keys())[0] == 'foreach_map[\"bucket_a\"]'


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "True"})
def test_tf_definitions_and_breadcrumbs():
    from checkov.terraform.graph_builder.graph_to_tf_definitions import convert_graph_vertices_to_tf_definitions
    dir_name = 'foreach_examples/depend_resources'
    local_graph, _ = build_and_get_graph_by_path(dir_name, render_var=True)
    tf_definitions, breadcrumbs = convert_graph_vertices_to_tf_definitions(local_graph.vertices, dir_name)
    expected_data = load_expected_data('expected_data_foreach.json')
    tf_definitions_to_check = {}
    for path, res in tf_definitions.items():
        path_list = path.split('/')[-2:]
        real_path = os.path.join(path_list[0], path_list[1])
        tf_definitions_to_check[real_path] = tf_definitions[path]
    assert_object_equal(tf_definitions_to_check, expected_data['tf_definitions'])

    expected_breadcrumbs = expected_data['breadcrumbs']
    assert len(breadcrumbs) == len(expected_breadcrumbs)
    assert len(breadcrumbs[list(breadcrumbs.keys())[0]]) == len(expected_breadcrumbs[list(expected_breadcrumbs.keys())[0]])
    resource_vertices = [vertex for vertex in local_graph.vertices if vertex.block_type == 'resource']
    for resource_vertex in resource_vertices:
        assert len(resource_vertex.foreach_attrs) == 2

    for name in ['["bucket_a"]', '["bucket_b"]']:
        assert f'aws_s3_bucket.foreach_map{name}' in breadcrumbs[list(breadcrumbs.keys())[0]]

        location_var = 'location'
        assert list(breadcrumbs[list(breadcrumbs.keys())[0]][f'aws_s3_bucket.foreach_map{name}'].keys()) == [location_var]
        assert list(expected_breadcrumbs[list(expected_breadcrumbs.keys())[0]][f'aws_s3_bucket.foreach_map{name}'].keys()) == [location_var]

        assert breadcrumbs[list(breadcrumbs.keys())[0]][f'aws_s3_bucket.foreach_map{name}'][location_var][0]['type'] == 'variable'
        assert expected_breadcrumbs[list(expected_breadcrumbs.keys())[0]][f'aws_s3_bucket.foreach_map{name}'][location_var][0]['type'] == 'variable'

        assert breadcrumbs[list(breadcrumbs.keys())[0]][f'aws_s3_bucket.foreach_map{name}'][location_var][0]['name'] == 'test'
        assert expected_breadcrumbs[list(expected_breadcrumbs.keys())[0]][f'aws_s3_bucket.foreach_map{name}'][location_var][0]['name'] == 'test'

        assert breadcrumbs[list(breadcrumbs.keys())[0]][f'aws_s3_bucket.foreach_map{name}'][location_var][0]['path'].endswith('depend_resources/variable.tf')
        assert expected_breadcrumbs[list(expected_breadcrumbs.keys())[0]][f'aws_s3_bucket.foreach_map{name}'][location_var][0]['path'].endswith('depend_resources/variable.tf')


@pytest.mark.parametrize(
    "attrs,k_v_to_change,expected_attrs,expected_res",
    [
        ({"test_key": ["${test_val}"]}, {"test_val": "new_val"}, {"test_key": ["new_val"]}, ['test_key']),
        ({"test_key": ["${test}"]}, {"test_val": "new_val"}, {"test_key": ["${test}"]}, []),
        ({"test_key": ["${test_val} ${test_val}"]}, {"test_val": "new_val"}, {"test_key": ["new_val new_val"]}, ['test_key']),
        ({"test_key": {"nested_key": ["${test_val}"]}}, {"test_val": "new_val"}, {"test_key": {"nested_key": ["new_val"]}}, ['test_key.nested_key']),
        ({"test_key": ["${test_val} test_val"]}, {"test_val": "new_val"}, {"test_key": ["new_val new_val"]}, ['test_key']),
        ({"test_key": ["${test_val}"]}, {"test_val": 123}, {"test_key": [123]}, ['test_key']),
        ({"test_key": ["${test_val}"]}, {"test_val": True}, {"test_key": [True]}, ['test_key']),
        ({"test_key": {"a": "${test_val}"}}, {"test_val": "new_val"}, {"test_key": {"a": "new_val"}}, ['test_key.a']),
        ({"test_key": {"a": {"b": "${test_val}"}}}, {"test_val": "new_val"}, {"test_key": {"a": {"b": "new_val"}}}, ['test_key.a.b'])
    ]
)
def test_update_attrs(attrs, k_v_to_change, expected_attrs, expected_res):
    from checkov.terraform.graph_builder.foreach_handler import ForeachHandler
    local_graph = build_and_get_graph_by_path('')[0]
    foreach_handler = ForeachHandler(local_graph)
    res = foreach_handler._update_attributes(attrs, k_v_to_change)
    assert attrs == expected_attrs
    assert res == expected_res
