from __future__ import annotations

import logging
import os.path
from typing import List, Dict, Set, Callable
import os

from checkov.common.sca.reachability.typing import FileParserOutput
from checkov.common.sca.reachability.commons import add_package_aliases
from checkov.common.sca.reachability.abstract_alias_mapping_strategy import AbstractAliasMappingStrategy
from checkov.common.sca.reachability.nodejs.utils import parse_webpack_file, parse_tsconfig_file, parse_babel_file, \
    parse_rollup_file, parse_package_json_file, parse_snowpack_file, parse_vite_file


file_name_to_parser_map: Dict[str, Callable[[str, Set[str]], FileParserOutput]] = {
    "webpack.config.js": parse_webpack_file,
    "tsconfig.json": parse_tsconfig_file,
    ".babelrc": parse_babel_file,
    "babel.config.js": parse_babel_file,
    "rollup.config.js": parse_rollup_file,
    "package.json": parse_package_json_file,
    "snowpack.config.js": parse_snowpack_file,
    "vite.config.js": parse_vite_file
}

class NodejsAliasMappingStrategy(AbstractAliasMappingStrategy):
    def create_alias_mapping(self, root_dir: str, relevant_packages: Set[str]) -> Dict[str, List[str]]:
        logging.debug("[NodejsAliasMappingStrategy](create_alias_mapping) - starting")
        alias_mapping: dict[str, list[str]] = dict()
        for curr_root, _, f_names in os.walk(root_dir):
            for file_name in f_names:
                if file_name in file_name_to_parser_map:
                    logging.debug(f"[NodejsAliasMappingStrategy](create_alias_mapping) - starting parsing ${file_name}")
                    with open(os.path.join(curr_root, file_name)) as f:
                        file_content = f.read()
                        try:
                            output = file_name_to_parser_map[file_name](file_content, relevant_packages)
                            for package_name in output:
                                alias_mapping[package_name] = output[package_name]["packageAliases"]
                            logging.debug(
                                f"[NodejsAliasMappingStrategy](create_alias_mapping) - done parsing for ${file_name}")
                        except Exception:
                            logging.error(f"[NodejsAliasMappingStrategy](create_alias_mapping) - failure when "
                                          f"parsing the file '${file_name}'. file content:\n{file_content}.\n",
                                          exc_info=True)
        return alias_mapping
