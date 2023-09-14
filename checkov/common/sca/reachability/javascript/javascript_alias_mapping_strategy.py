from __future__ import annotations

import logging
import os.path
from typing import List, Dict, Set, Any, Callable
import re
import json
import os

from checkov.common.sca.reachability.alias_mapping_strategy import AliasMappingStrategy

MODULE_EXPORTS_PATTERN = r'module\.exports\s*=\s*({.*?});'
EXPORT_DEFAULT_PATTERN = r'export\s*default\s*({.*?});'


class JavascriptAliasMappingStrategy(AliasMappingStrategy):

    @staticmethod
    def __parse_export(file_content: str, pattern: str) -> Dict[str, Any] | None:
        module_export_match = re.search(pattern, file_content, re.DOTALL)

        if module_export_match:
            module_exports_str = module_export_match.group(1)
            # for having for all the keys and values doube quotes and removing spaces
            module_exports_str = re.sub(r'\s+', '', re.sub(r'([{\s,])(\w+):', r'\1"\2":', module_exports_str)
                                        .replace("'", "\""))
            module_exports: Dict[str, Any] = json.loads(module_exports_str)
            return module_exports
        return None

    @staticmethod
    def _parse_webpack_file(alias_mapping: Dict[str, List[str]], file_content: str, relevant_packages: Set[str])\
            -> None:
        module_exports_json = JavascriptAliasMappingStrategy.__parse_export(file_content, MODULE_EXPORTS_PATTERN)

        if module_exports_json:
            aliases = module_exports_json.get("resolve", {}).get("alias", {})
            for imported_name in aliases:
                package_name = aliases[imported_name]
                if package_name in relevant_packages:
                    alias_mapping.setdefault(package_name, []).append(imported_name)

    @staticmethod
    def _parse_tsconfig_file(alias_mapping: Dict[str, List[str]], file_content: str, relevant_packages: Set[str])\
            -> None:
        tsconfig_json = json.loads(file_content)
        paths = tsconfig_json.get("compilerOptions", {}).get("paths", {})
        for imported_name in paths:
            for package_relative_path in paths[imported_name]:
                package_name = os.path.basename(package_relative_path)
                if package_name in relevant_packages:
                    alias_mapping.setdefault(package_name, []).append(imported_name)

    @staticmethod
    def _parse_babel_file(alias_mapping: Dict[str, List[str]], file_content: str, relevant_packages: Set[str])\
            -> None:
        babelrc_json = json.loads(file_content)
        plugins = babelrc_json.get("plugins", {})
        for plugin in plugins:
            if len(plugin) > 1:
                plugin_object = plugin[1]
                aliases = plugin_object.get("alias", {})
                for imported_name in aliases:
                    package_name = aliases[imported_name]
                    if package_name in relevant_packages:
                        alias_mapping.setdefault(package_name, []).append(imported_name)

    @staticmethod
    def _parse_rollup_file(alias_mapping: Dict[str, List[str]], file_content: str, relevant_packages: Set[str])\
            -> None:
        export_default_match = re.search(EXPORT_DEFAULT_PATTERN, file_content, re.DOTALL)

        if export_default_match:
            export_default_str = export_default_match.group(1)
            # for having for all the keys and values doube quotes and removing spaces
            export_default_str = re.sub(r'\s+', '', re.sub(r'([{\s,])(\w+):', r'\1"\2":', export_default_str)
                                        .replace("'", "\""))

            # Defining a regular expression pattern to match the elements within the "plugins" list
            pattern = r'alias\(\{[^)]*\}\)'
            matches = re.findall(pattern, export_default_str)

            for alias_object_str in matches:
                alias_object = json.loads(alias_object_str[6:-1])  # removing 'alias(' and ')'
                for entry in alias_object.get("entries", []):
                    if entry["replacement"] in relevant_packages:
                        alias_mapping.setdefault(entry["replacement"], []).append(entry["find"])

    @staticmethod
    def _parse_package_json_file(alias_mapping: Dict[str, List[str]], file_content: str, relevant_packages: Set[str])\
            -> None:
        package_json = json.loads(file_content)
        aliases: Dict[str, str] = dict()
        if "alias" in package_json:
            aliases.update(package_json["alias"])
        if package_json.get("aliasify", {}).get("aliases"):
            aliases.update(package_json["aliasify"]["aliases"])
        for imported_name in aliases:
            if aliases[imported_name]:
                alias_mapping.setdefault(aliases[imported_name], []).append(imported_name)

    @staticmethod
    def _parse_snowpack_file(alias_mapping: Dict[str, List[str]], file_content: str, relevant_packages: Set[str])\
            -> None:
        module_exports_json = JavascriptAliasMappingStrategy.__parse_export(file_content, MODULE_EXPORTS_PATTERN)

        if module_exports_json:
            aliases = module_exports_json.get("alias", {})
            for imported_name in aliases:
                package_name = aliases[imported_name]
                if package_name in relevant_packages:
                    if package_name in relevant_packages:
                        alias_mapping.setdefault(package_name, []).append(imported_name)

    @staticmethod
    def _parse_vite_file(alias_mapping: Dict[str, List[str]], file_content: str, relevant_packages: Set[str])\
            -> None:
        export_default_match = JavascriptAliasMappingStrategy.__parse_export(file_content, EXPORT_DEFAULT_PATTERN)

        if export_default_match:
            aliases = export_default_match.get("resolve", {}).get("alias", {})
            for imported_name in aliases:
                package_name = aliases[imported_name]
                if package_name in relevant_packages:
                    alias_mapping.setdefault(package_name, []).append(imported_name)

    @staticmethod
    def _get_file_name_to_function_map() -> Dict[str, Callable[[Dict[str, List[str]], str, Set[str]], None]]:
        return {
            "webpack.config.js": JavascriptAliasMappingStrategy._parse_webpack_file,
            "tsconfig.json": JavascriptAliasMappingStrategy._parse_tsconfig_file,
            ".babelrc": JavascriptAliasMappingStrategy._parse_babel_file,
            "babel.config.js": JavascriptAliasMappingStrategy._parse_babel_file,
            "rollup.config.js": JavascriptAliasMappingStrategy._parse_rollup_file,
            "package.json": JavascriptAliasMappingStrategy._parse_package_json_file,
            "snowpack.config.js": JavascriptAliasMappingStrategy._parse_snowpack_file,
            "vite.config.js": JavascriptAliasMappingStrategy._parse_vite_file
        }

    def create_alias_mapping(self, root_dir: str, relevant_packages: Set[str]) -> Dict[str, List[str]]:
        logging.debug("[JavascriptAliasMappingStrategy](create_alias_mapping) - starting")
        alias_mapping: dict[str, list[str]] = dict()
        file_name_to_function_map = self._get_file_name_to_function_map()
        for curr_root, _, f_names in os.walk(root_dir):
            for file_name in f_names:
                if file_name in file_name_to_function_map:
                    logging.debug(f"[JavascriptAliasMappingStrategy](create_alias_mapping) - starting parsing ${file_name}")
                    with open(os.path.join(curr_root, file_name)) as f:
                        file_content = f.read()
                        try:
                            file_name_to_function_map[file_name](alias_mapping, file_content, relevant_packages)
                            logging.debug(
                                f"[JavascriptAliasMappingStrategy](create_alias_mapping) - done parsing for ${file_name}")
                        except Exception:
                            logging.error(f"[JavascriptAliasMappingStrategy](create_alias_mapping) - failure when "
                                          f"parsing the file '${file_name}'. file content:\n{file_content}.\n",
                                          exc_info=True)

        return alias_mapping
