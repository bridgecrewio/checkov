from __future__ import  annotations

import os.path
from abc import ABC
from typing import List, Dict, Set, Any
import re
import json
import os

MODULE_EXPORTS_PATTERN = r'module\.exports\s*=\s*({.*?});'
EXPORT_DEFAULT_PATTERN = r'export\s*default\s*({.*?});'


class JavascriptAliasMappingStrategy(ABC):

    def _parse_export(self, file_content: str, pattern: str) -> Dict[str, Any] | None:
        module_export_match = re.search(pattern, file_content, re.DOTALL)

        if module_export_match:
            module_exports_str = module_export_match.group(1)
            module_exports_str = re.sub(r'([{\s,])(\w+):', r'\1"\2":', module_exports_str).replace("'", "\"")
            print(module_exports_str)
            module_exports: Dict[str, Any]= json.loads(module_exports_str)
            return module_exports
        return None

    def parse_webpack_file(self, alias_mapping: Dict[str, List[str]], file_content: str, relevant_packages: Set[str])\
            -> None:
        module_exports_json = self._parse_export(file_content, MODULE_EXPORTS_PATTERN)

        if module_exports_json:
            aliases = module_exports_json.get("resolve", {}).get("alias", {})
            for imported_name in aliases:
                package_name = aliases[imported_name]
                if package_name in relevant_packages:
                    alias_mapping.setdefault(package_name, []).append(imported_name)

    def parse_tsconfig_file(self, alias_mapping: Dict[str, List[str]], file_content: str, relevant_packages: Set[str])\
            -> None:
        tsconfig_json = json.loads(file_content)
        paths = tsconfig_json.get("compilerOptions", {}).get("paths", {})
        for imported_name in paths:
            for package_relative_path in paths[imported_name]:
                package_name = os.path.basename(package_relative_path)
                if package_name in relevant_packages:
                    alias_mapping.setdefault(package_name, []).append(imported_name)


    def parse_babel_file(self, alias_mapping: Dict[str, List[str]], file_content: str, relevant_packages: Set[str])\
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

    def parse_rollup_file(self, alias_mapping: Dict[str, List[str]], file_content: str, relevant_packages: Set[str])\
            -> None:
        export_default_match = re.search(EXPORT_DEFAULT_PATTERN, file_content, re.DOTALL)

        if export_default_match:
            export_default_str = export_default_match.group(1)
            export_default_str = re.sub(r'([{\s,])(\w+):', r'\1"\2":', export_default_str).replace("'", "\"")
            export_default_str = re.sub(r'\s+', '', export_default_str)

            # Define a regular expression pattern to match the elements within the "plugins" list
            pattern = r'alias\(\{[^)]*\}\)'

            # Use the findall() function to find all matches of the pattern in the input string
            matches = re.findall(pattern, export_default_str)
            for alias_object_str in matches:
                alias_object = json.loads(alias_object_str[6:-1]) # removing 'alias(' and ')'
                print(alias_object)
                for entry in alias_object.get("entries", []):
                    alias_mapping.setdefault(entry["replacement"], []).append(entry["find"])


    def parse_package_json_file(self, alias_mapping: Dict[str, List[str]], file_content: str, relevant_packages: Set[str])\
            -> None:
        package_json = json.loads(file_content)
        aliases: Dict[str, str] = dict()
        if "alias" in package_json:
            aliases.update(package_json["alias"])
        if package_json.get("aliasify", {}).get("aliases"):
            aliases.update(package_json["aliasify"]["aliases"])
        for imported_name in aliases:
            alias_mapping.setdefault(aliases[imported_name], []).append(imported_name)

    def parse_snowpack_file(self, alias_mapping: Dict[str, List[str]], file_content: str, relevant_packages: Set[str])\
            -> None:
        module_exports_json = self._parse_export(file_content, MODULE_EXPORTS_PATTERN)

        if module_exports_json:
            aliases = module_exports_json.get("alias", {})
            for imported_name in aliases:
                package_name = aliases[imported_name]
                if package_name in relevant_packages:
                    alias_mapping.setdefault(package_name, []).append(imported_name)

    def parse_vite_file(self, alias_mapping: Dict[str, List[str]], file_content: str, relevant_packages: Set[str])\
            -> None:
        export_default_match = self._parse_export(file_content, EXPORT_DEFAULT_PATTERN)

        if export_default_match:
            aliases = export_default_match.get("resolve", {}).get("alias", {})
            for imported_name in aliases:
                package_name = aliases[imported_name]
                if package_name in relevant_packages:
                    alias_mapping.setdefault(package_name, []).append(imported_name)

    def create_alias_mapping(self, root_dir: str, relevant_packages: List[str]) -> Dict[str, List[str]]:
        return dict()
