import os
from typing import Dict, Any
from checkov.common.sca.reachability.package_alias_mapping.nodejs.nodejs_alias_mapping_strategy import NodejsAliasMappingStrategy

current_dir = os.path.dirname(os.path.realpath(__file__))


def test_create_alias_mapping_from_webpack_file():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "webpack")
    alias_mapping: Dict[str, Any] = {"languages": {}}
    strategy_object.update_alias_mapping(alias_mapping, "supplygoat", root_dir, {'axios'})
    assert alias_mapping == {'languages': {'nodejs': {'repositories': {'supplygoat': {'files': {'webpack.config.js': {'packageAliases': {'axios': {'packageAliases': ['ax']}}}}}}}}}


def test_create_alias_mapping_from_babelrc_file():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "babel", "babelrc")
    alias_mapping: Dict[str, Any] = {"languages": {}}
    strategy_object.update_alias_mapping(alias_mapping, "supplygoat", root_dir, {'axios'})
    assert alias_mapping == {'languages': {'nodejs': {'repositories': {'supplygoat': {'files': {'.babelrc': {'packageAliases': {'axios': {'packageAliases': ['ax']}}}}}}}}}


def test_create_alias_mapping_from_babel_config_file():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "babel", "babel_config")
    alias_mapping: Dict[str, Any] = {"languages": {}}
    strategy_object.update_alias_mapping(alias_mapping, "supplygoat", root_dir, {'axios'})
    assert alias_mapping == {'languages': {'nodejs': {'repositories': {'supplygoat': {'files': {'babel.config.js': {'packageAliases': {'axios': {'packageAliases': ['ax']}}}}}}}}}


def test_create_alias_mapping_from_rollup_file():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "rollup")
    alias_mapping: Dict[str, Any] = {"languages": {}}
    strategy_object.update_alias_mapping(alias_mapping, "supplygoat", root_dir, {'axios'})
    assert alias_mapping == {'languages': {'nodejs': {'repositories': {'supplygoat': {'files': {'rollup.config.js': {'packageAliases': {'axios': {'packageAliases': ['ax']}}}}}}}}}


def test_create_alias_mapping_from_package_json_alias():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "package_json", "package_json_with_alias")
    alias_mapping: Dict[str, Any] = {"languages": {}}
    strategy_object.update_alias_mapping(alias_mapping, "supplygoat", root_dir, {'axios'})
    assert alias_mapping == {'languages': {'nodejs': {'repositories': {'supplygoat': {'files': {'package.json': {'packageAliases': {'axios': {'packageAliases': ['ax']}}}}}}}}}


def test_create_alias_mapping_from_package_json_aliasify():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "package_json", "package_json_with_aliasify")
    alias_mapping: Dict[str, Any] = {"languages": {}}
    strategy_object.update_alias_mapping(alias_mapping, "supplygoat", root_dir, {'axios'})
    assert alias_mapping == {'languages': {'nodejs': {'repositories': {'supplygoat': {'files': {'package.json': {'packageAliases': {'axios': {'packageAliases': ['ax']}}}}}}}}}


def test_create_alias_mapping_from_snowpack():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "snowpack")
    alias_mapping: Dict[str, Any] = {"languages": {}}
    strategy_object.update_alias_mapping(alias_mapping, "supplygoat", root_dir, {'axios'})
    assert alias_mapping == {'languages': {'nodejs': {'repositories': {'supplygoat': {'files': {'snowpack.config.js': {'packageAliases': {'axios': {'packageAliases': ['ax']}}}}}}}}}


def test_create_alias_mapping_from_vite():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "vite")
    alias_mapping: Dict[str, Any] = {"languages": {}}
    strategy_object.update_alias_mapping(alias_mapping, "supplygoat", root_dir, {'axios'})
    assert alias_mapping == {'languages': {'nodejs': {'repositories': {'supplygoat': {'files': {'vite.config.js': {'packageAliases': {'axios': {'packageAliases': ['ax']}}}}}}}}}


def test_create_alias_mapping_mix():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "mix")
    alias_mapping: Dict[str, Any] = {"languages": {}}
    strategy_object.update_alias_mapping(alias_mapping, "supplygoat", root_dir, {'axios'})
    assert alias_mapping == {'languages': {'nodejs': {'repositories': {'supplygoat': {'files': {'vite.config.js': {'packageAliases': {'axios': {'packageAliases': ['ax']}}}, 'package_json_with_alias/package.json': {'packageAliases': {'axios': {'packageAliases': ['ax']}}}}}}}}}


def test_create_alias_mapping_from_fake():
    strategy_object = NodejsAliasMappingStrategy()
    root_dir = os.path.join(current_dir, "examples", "fake_file")
    alias_mapping: Dict[str, Any] = {"languages": {}}
    strategy_object.update_alias_mapping(alias_mapping, "supplygoat", root_dir, {'axios'})
    assert alias_mapping == {'languages': {}}
