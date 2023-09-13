from checkov.common.sca.reachability.javascript.javascript_alias_mapping_strategy import JavascriptAliasMappingStrategy


def test_parse_webpack_file():
    strategy_object = JavascriptAliasMappingStrategy()
    alias_mapping: dict[str, list[str]] = dict()
    file_content = \
        "module.exports = {" \
        "  resolve: {" \
        "    alias: {" \
        "      ax: 'axios'" \
        "    }" \
        "  }" \
        "};"
    strategy_object.parse_webpack_file(alias_mapping, file_content, {'axios'})
    assert alias_mapping == {"axios": ["ax"]}


def test_parse_babel_file():
    strategy_object = JavascriptAliasMappingStrategy()
    alias_mapping: dict[str, list[str]] = dict()
    file_content = \
        '{' \
        '  "plugins": [' \
        '    ["module-resolver", {' \
        '      "alias": {' \
        '        "ax": "axios"' \
        '      }' \
        '    }]' \
        '  ]' \
        '}'
    strategy_object.parse_babel_file(alias_mapping, file_content, {'axios'})
    assert alias_mapping == {"axios": ["ax"]}


def test_parse_rollup_file():
    strategy_object = JavascriptAliasMappingStrategy()
    alias_mapping: dict[str, list[str]] = dict()
    file_content = \
        "import alias from '@rollup/plugin-alias';" \
        "export default {" \
        "  plugins: [" \
        "    alias({" \
        "      entries: [" \
        "        { find: 'ax', replacement: 'axios' }" \
        "      ]" \
        "    })" \
        "  ]" \
        "};"
    strategy_object.parse_rollup_file(alias_mapping, file_content, {'axios'})
    assert alias_mapping == {"axios": ["ax"]}


def test_parse_package_json_alias():
    strategy_object = JavascriptAliasMappingStrategy()
    alias_mapping: dict[str, list[str]] = dict()
    file_content = \
        '{' \
        '  "alias": {' \
        '    "ax": "axios"' \
        '  }' \
        '}'
    strategy_object.parse_package_json_file(alias_mapping, file_content, {'axios'})
    assert alias_mapping == {"axios": ["ax"]}


def test_parse_package_json_aliasify():
    strategy_object = JavascriptAliasMappingStrategy()
    alias_mapping: dict[str, list[str]] = dict()
    file_content = \
        '{' \
        '  "aliasify": {' \
        '    "aliases": {' \
        '      "ax": "axios"' \
        '    }' \
        '  }' \
        '}'
    strategy_object.parse_package_json_file(alias_mapping, file_content, {'axios'})
    assert alias_mapping == {"axios": ["ax"]}


def test_parse_snowpack():
    strategy_object = JavascriptAliasMappingStrategy()
    alias_mapping: dict[str, list[str]] = dict()
    file_content = \
        'module.exports = {' \
        '  alias: {' \
        '    "ax": "axios"' \
        '  }' \
        '};'
    strategy_object.parse_snowpack_file(alias_mapping, file_content, {'axios'})
    assert alias_mapping == {"axios": ["ax"]}


def test_parse_vite():
    strategy_object = JavascriptAliasMappingStrategy()
    alias_mapping: dict[str, list[str]] = dict()
    file_content = \
        'export default {' \
        '  resolve: {' \
        '    alias: {' \
        '      "ax": "axios"' \
        '    }' \
        '  }' \
        '};'
    strategy_object.parse_vite_file(alias_mapping, file_content, {'axios'})
    assert alias_mapping == {"axios": ["ax"]}
