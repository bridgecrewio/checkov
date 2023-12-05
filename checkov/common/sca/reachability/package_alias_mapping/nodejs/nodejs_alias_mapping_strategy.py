from __future__ import annotations

from typing import Dict, Set, Callable, Any

from checkov.common.sca.reachability.package_alias_mapping.abstract_alias_mapping_strategy import AbstractAliasMappingStrategy
from checkov.common.sca.reachability.package_alias_mapping.nodejs.utils import parse_webpack_file, parse_tsconfig_file, parse_babel_file, \
    parse_rollup_file, parse_package_json_file, parse_snowpack_file, parse_vite_file


class NodejsAliasMappingStrategy(AbstractAliasMappingStrategy):
    def get_language(self) -> str:
        return "nodejs"

    def get_file_name_to_parser_map(self) -> Dict[str, Callable[[str, Set[str]], Dict[str, Any]]]:
        return {
            "webpack.config.js": parse_webpack_file,
            "tsconfig.json": parse_tsconfig_file,
            ".babelrc": parse_babel_file,
            "babel.config.js": parse_babel_file,
            "rollup.config.js": parse_rollup_file,
            "package.json": parse_package_json_file,
            "snowpack.config.js": parse_snowpack_file,
            "vite.config.js": parse_vite_file
        }
