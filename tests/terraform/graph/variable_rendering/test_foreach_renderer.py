import json
import os
from unittest import mock

import pytest

from checkov.common.util.json_utils import object_hook, CustomJSONEncoder
from checkov.terraform.graph_builder.foreach.abstract_handler import ForeachAbstractHandler
from checkov.terraform.graph_builder.foreach.builder import ForeachBuilder
from checkov.terraform.graph_builder.foreach.module_handler import ForeachModuleHandler
from checkov.terraform.graph_builder.foreach.resource_handler import ForeachResourceHandler

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


@pytest.fixture()
def checkov_source_path() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


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
@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
def test_static_foreach_resource(block_index, expected_res, obj):
    dir_name = 'foreach_resources/static_foreach_value'
    local_graph = build_and_get_graph_by_path(dir_name)[0]
    foreach_handler = ForeachResourceHandler(local_graph)
    res = foreach_handler._get_static_foreach_statement(block_index)
    if obj:
        assert_object_equal(res, expected_res)
    else:
        assert res == expected_res


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
def test_dynamic_foreach_resource():
    dir_name = 'foreach_resources/dynamic_foreach_value'
    local_graph = build_and_get_graph_by_path(dir_name)[0]
    foreach_handler = ForeachResourceHandler(local_graph)
    res = foreach_handler._handle_dynamic_statement([6, 7, 8, 9, 10])
    expected_res = {
        6: {'a_group': 'eastus', 'another_group': 'westus2'}, 7: ['s3-bucket-a', 's3-bucket-b'], 8: 5, 9: 2, 10: None
    }
    assert_object_equal(res, expected_res)


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
def test_foreach_resource():
    dir_name = 'foreach_resources'
    local_graph = build_and_get_graph_by_path(dir_name)[0]
    foreach_handler = ForeachResourceHandler(local_graph)
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
    dir_name = 'foreach_resources'
    local_graph = build_and_get_graph_by_path(dir_name)[0]
    foreach_handler = ForeachAbstractHandler(local_graph)
    blocks = [6, 7, 8, 9, 10, 21, 22, 24, 25]
    sub_graph = foreach_handler._build_sub_graph(blocks)
    assert all(sub_graph.vertices[i] for i in blocks)
    assert not all(sub_graph.vertices[i] for i in range(len(sub_graph.vertices)))
    assert len(sub_graph.edges) < len(local_graph.edges)


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
def test_new_resources_count():
    dir_name = 'foreach_examples/count_dup_resources'
    local_graph = build_and_get_graph_by_path(dir_name)[0]
    vertices_names = [vertice.name for vertice in local_graph.vertices]
    main_count_resource = 'aws_s3_bucket.count_var_resource'
    assert main_count_resource in vertices_names

    foreach_builder = ForeachBuilder(local_graph)
    foreach_builder.handle({'resource': [3], 'module': []})
    for i, resource in enumerate([local_graph.vertices[3], local_graph.vertices[8], local_graph.vertices[9]]):
        assert resource.name.endswith(f"[{i}]")
        assert resource.id.endswith(f"[{i}]")
        assert list(resource.config['aws_s3_bucket'].keys())[0].endswith(f'[{i}]')
    new_vertices_names = [vertice.name for vertice in local_graph.vertices]
    assert main_count_resource not in new_vertices_names


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
def test_new_resources_foreach():
    dir_name = 'foreach_examples/foreach_dup_resources'
    local_graph = build_and_get_graph_by_path(dir_name)[0]
    foreach_builder = ForeachBuilder(local_graph)
    foreach_builder.handle({'resource': [0, 1], 'module': []})
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


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "True"})
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
        ({"test_key": {"a": {"b": "${test_val}"}}}, {"test_val": "new_val"}, {"test_key": {"a": {"b": "new_val"}}}, ['test_key.a.b']),
        ({'ports': '${each.value.port}', 'protocol': 'tcp'}, {'each.value': {'name': 'name-open-ssh', 'port': '22', 'range': '0.0.0.0/0', 'tag': 'allow-ssh'}}, {'ports': '22', 'protocol': 'tcp'}, ['ports'])
    ]
)
def test_update_attrs(attrs, k_v_to_change, expected_attrs, expected_res):
    local_graph = build_and_get_graph_by_path('')[0]
    foreach_handler = ForeachAbstractHandler(local_graph)
    res = foreach_handler._update_attributes(attrs, k_v_to_change)
    assert attrs == expected_attrs
    assert res == expected_res


@mock.patch.dict(os.environ, {"CHECKOV_NEW_TF_PARSER": "True"})
@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "True"})
@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_MODULES_FOREACH_HANDLING": "True"})
def test_new_tf_parser_with_foreach_modules(checkov_source_path):
    dir_name = 'parser_dup_nested'
    local_graph, tf_definitions = build_and_get_graph_by_path(dir_name, render_var=True)
    assert len(tf_definitions.keys()) == 14
    assert len([block for block in local_graph.vertices if block.block_type == 'resource']) == 8
    assert len([block for block in local_graph.vertices if block.block_type == 'module']) == 12

    assert len(local_graph.vertices) == 63
    assert len(local_graph.vertices_by_module_dependency) == 13

    assert local_graph.vertices_by_module_dependency[None]['module'] == [0, 1, 33, 48]

    first_module_vertex = local_graph.vertices[0]
    assert first_module_vertex.name == 's3_module["a"]' and first_module_vertex.for_each_index == 'a'

    second_module_vertex = local_graph.vertices[1]
    assert second_module_vertex.name == 's3_module2[0]' and second_module_vertex.for_each_index == 0

    thirty_third_module_vertex = local_graph.vertices[33]
    assert thirty_third_module_vertex.name == 's3_module["b"]' and thirty_third_module_vertex.for_each_index == 'b'

    forty_eight_module_vertex = local_graph.vertices[48]
    assert forty_eight_module_vertex.name == 's3_module2[1]' and forty_eight_module_vertex.for_each_index == 1

    assert local_graph.vertices[34].source_module == {33}
    assert local_graph.vertices[49].source_module == {48}

    # check foreach_idx is updated correctly
    first_key = list(tf_definitions.keys())[0]
    first_value = tf_definitions[first_key]

    first_tf_module = first_value['module'][0]['s3_module["a"]']['__resolved__'][0]
    second_tf_module = first_value['module'][1]['s3_module2[0]']['__resolved__'][0]
    third_tf_module = first_value['module'][2]['s3_module["b"]']['__resolved__'][0]
    fourth_tf_module = first_value['module'][3]['s3_module2[1]']['__resolved__'][0]
    assert first_tf_module in tf_definitions
    assert second_tf_module in tf_definitions
    assert third_tf_module in tf_definitions
    assert fourth_tf_module in tf_definitions

    first_nested_module = tf_definitions[first_tf_module]
    second_nested_module = tf_definitions[second_tf_module]
    third_nested_module = tf_definitions[third_tf_module]
    fourth_nested_module = tf_definitions[fourth_tf_module]

    assert len(tf_definitions[first_nested_module['module'][0]['inner_s3_module']['__resolved__'][0]]['resource']) == 1
    assert len(tf_definitions[first_nested_module['module'][1]['inner_s3_module2']['__resolved__'][0]]['resource']) == 1
    assert len(tf_definitions[second_nested_module['module'][0]['inner_s3_module']['__resolved__'][0]]['resource']) == 1
    assert len(tf_definitions[second_nested_module['module'][1]['inner_s3_module2']['__resolved__'][0]]['resource']) == 1
    assert len(tf_definitions[third_nested_module['module'][0]['inner_s3_module']['__resolved__'][0]]['resource']) == 1
    assert len(tf_definitions[third_nested_module['module'][1]['inner_s3_module2']['__resolved__'][0]]['resource']) == 1
    assert len(tf_definitions[fourth_nested_module['module'][0]['inner_s3_module']['__resolved__'][0]]['resource']) == 1
    assert len(tf_definitions[fourth_nested_module['module'][1]['inner_s3_module2']['__resolved__'][0]]['resource']) == 1

    assert first_tf_module.file_path == os.path.join(checkov_source_path, 'tests/terraform/graph/variable_rendering/resources/parser_dup_nested/module/main.tf')

    first_source_module = first_tf_module.tf_source_modules
    assert first_source_module.name == 's3_module'
    assert first_source_module.nested_tf_module is None
    assert first_source_module.foreach_idx == 'a'


@mock.patch.dict(os.environ, {"CHECKOV_NEW_TF_PARSER": "True"})
@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "True"})
@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_MODULES_FOREACH_HANDLING": "True"})
def test_tf_definitions_for_foreach_on_modules(checkov_source_path):
    dir_name = 'parser_dup_nested'
    _, tf_definitions = build_and_get_graph_by_path(dir_name, render_var=True)

    file_path = os.path.join(os.path.dirname(__file__), 'expected_foreach_modules_tf_definitions.json')
    with open(file_path, 'r') as f:
        expected_data = json.load(f, object_hook=object_hook)

    tf_definitions_json = json.dumps(tf_definitions, cls=CustomJSONEncoder)
    tf_definitions_json = tf_definitions_json.replace(checkov_source_path, '...')
    tf_definitions_after_handling_checkov_source = json.loads(tf_definitions_json, object_hook=object_hook)
    assert tf_definitions_after_handling_checkov_source == expected_data


@mock.patch.dict(os.environ, {"CHECKOV_NEW_TF_PARSER": "True"})
@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "True"})
@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_MODULES_FOREACH_HANDLING": "True"})
def test_foreach_module_in_second_level_module(checkov_source_path):
    dir_name = 'foreach_module'
    graph, tf_definitions = build_and_get_graph_by_path(dir_name, render_var=True)

    assert len([block for block in graph.vertices if block.block_type == 'module']) == 10
    assert len([block for block in graph.vertices if block.block_type == 'resource']) == 8
    assert len(tf_definitions.keys()) == 11


@mock.patch.dict(os.environ, {"CHECKOV_NEW_TF_PARSER": "True"})
@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "True"})
@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_MODULES_FOREACH_HANDLING": "True"})
def test_foreach_module_in_both_levels_module(checkov_source_path):
    dir_name = 'foreach_module_dup_foreach'
    graph, tf_definitions = build_and_get_graph_by_path(dir_name, render_var=True)

    assert len([block for block in graph.vertices if block.block_type == 'module']) == 20
    assert len([block for block in graph.vertices if block.block_type == 'resource']) == 16
    assert len(tf_definitions.keys()) == 22


@mock.patch.dict(os.environ, {"CHECKOV_NEW_TF_PARSER": "True"})
@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "True"})
@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_MODULES_FOREACH_HANDLING": "True"})
def test_foreach_module_and_resource(checkov_source_path):
    dir_name = 'foreach_module_and_resource'
    graph, tf_definitions = build_and_get_graph_by_path(dir_name, render_var=True)

    assert len([block for block in graph.vertices if block.block_type == 'module']) == 2
    assert len([block for block in graph.vertices if block.block_type == 'resource']) == 4
    assert len(tf_definitions.keys()) == 3

    assert graph.vertices[4].config['aws_s3_bucket_public_access_block']['var_bucket["a"]']['__address__'] == 'module.s3_module["a"].aws_s3_bucket_public_access_block.var_bucket["a"]'
    assert graph.vertices[10].config['aws_s3_bucket_public_access_block']['var_bucket["a"]']['__address__'] == 'module.s3_module["b"].aws_s3_bucket_public_access_block.var_bucket["a"]'
    assert graph.vertices[12].config['aws_s3_bucket_public_access_block']['var_bucket["b"]']['__address__'] == 'module.s3_module["a"].aws_s3_bucket_public_access_block.var_bucket["b"]'
    assert graph.vertices[13].config['aws_s3_bucket_public_access_block']['var_bucket["b"]']['__address__'] == 'module.s3_module["b"].aws_s3_bucket_public_access_block.var_bucket["b"]'


@mock.patch.dict(os.environ, {"CHECKOV_NEW_TF_PARSER": "True"})
@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "True"})
@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_MODULES_FOREACH_HANDLING": "True"})
def test_foreach_module_with_more_than_two_resources(checkov_source_path):
    dir_name = 'foreach_module_with_more_than_two_resources'
    graph, tf_definitions = build_and_get_graph_by_path(dir_name, render_var=True)

    assert len([block for block in graph.vertices if block.block_type == 'module']) == 16
    assert len([block for block in graph.vertices if block.block_type == 'resource']) == 14
    assert len(tf_definitions.keys()) == 17


@mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "True"})
@pytest.mark.parametrize(
    "statement,expected",
    [
        ([{'main'}], True),
        (["${toset(['bucket_a', 'bucket_b'])}"], True),
        ({'key1': '${var.a}', 'key2': '${var.b}'}, True),
        ({'key2': '${var.b}', 'var.a': '${var.a}'}, False),
        ('${var.a}', False),
        ('bana', True)
    ]
)
def test__is_static_foreach_statement(statement, expected):
    abstract_handler = ForeachAbstractHandler(None)
    assert abstract_handler._is_static_foreach_statement(statement) == expected


def test__update_resolved_entry_for_tf_definition_with_empty_resolved_config_does_not_fail():
    from checkov.terraform import TFModule
    from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
    from checkov.terraform.graph_builder.graph_components.block_types import BlockType

    child = TerraformBlock(name='test', config={'test': {'__resolved__': []}}, path='', block_type=BlockType.MODULE,
                           attributes={})
    ForeachModuleHandler._update_resolved_entry_for_tf_definition(child, 1, TFModule('', ''))
    assert True  # Makes sure the above line doesn't fail
