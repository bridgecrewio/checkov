import os
from checkov.common.sca.reachability.nodejs.nodejs_alias_mapping_strategy import NodejsAliasMappingStrategy

current_dir = os.path.dirname(os.path.realpath(__file__))


def test_create_alias_mapping_from_webpack_file():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "webpack")
    alias_mapping = strategy_object.create_alias_mapping(root_dir, {'axios'})
    assert alias_mapping == {"axios": ["ax"]}


def test_create_alias_mapping_from_babelrc_file():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "babel", "babelrc")
    alias_mapping = strategy_object.create_alias_mapping(root_dir, {'axios'})
    assert alias_mapping == {"axios": ["ax"]}


def test_create_alias_mapping_from_babel_config_file():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "babel", "babel_config")
    alias_mapping = strategy_object.create_alias_mapping(root_dir, {'axios'})
    assert alias_mapping == {"axios": ["ax"]}


def test_create_alias_mapping_from_rollup_file():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "rollup")
    alias_mapping = strategy_object.create_alias_mapping(root_dir, {'axios'})
    assert alias_mapping == {"axios": ["ax"]}


def test_create_alias_mapping_from_package_json_alias():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "package_json", "package_json_with_alias")
    alias_mapping = strategy_object.create_alias_mapping(root_dir, {'axios'})
    assert alias_mapping == {"axios": ["ax"]}


def test_create_alias_mapping_from_package_json_aliasify():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "package_json", "package_json_with_aliasify")
    alias_mapping = strategy_object.create_alias_mapping(root_dir, {'axios'})
    assert alias_mapping == {"axios": ["ax"]}


def test_create_alias_mapping_from_snowpack():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "snowpack")
    alias_mapping = strategy_object.create_alias_mapping(root_dir, {'axios'})
    assert alias_mapping == {"axios": ["ax"]}


def test_create_alias_mapping_from_vite():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "vite")
    alias_mapping = strategy_object.create_alias_mapping(root_dir, {'axios'})
    assert alias_mapping == {"axios": ["ax"]}


def test_create_alias_mapping_from_fake():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "fake_file")
    alias_mapping = strategy_object.create_alias_mapping(root_dir, {'axios'})
    assert alias_mapping == {}
