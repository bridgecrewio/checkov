from __future__ import annotations

import logging
import os.path
from json import JSONDecodeError
from typing import Dict, Set, Any
import re
import json
import os


MODULE_EXPORTS_PATTERN = r'module\.exports\s*=\s*({.*?});'
EXPORT_DEFAULT_PATTERN = r'export\s*default\s*({.*?});'


def load_json_with_comments(json_str: str) -> Any:
    # Regular expression to remove comments (both single line and multi-line)
    pattern = r'(?<!\\)(["\'])(?:(?=(\\?))\2.)*?\1|//.*?$|/\*[\s\S]*?\*/'
    regex = re.compile(pattern, re.MULTILINE)
    clean_json_str = regex.sub(lambda match: match.group(0) if match.group(1) else '', json_str)
    return json.loads(clean_json_str)


def _parse_export(file_content: str, pattern: str) -> Dict[str, Any] | None:
    module_export_match = re.search(pattern, file_content, re.DOTALL)

    if module_export_match:
        module_exports_str = module_export_match.group(1)
        # for having for all the keys and values double quotes and removing spaces
        module_exports_str = re.sub(r'\s+', '', re.sub(r'([{\s,])(\w+):', r'\1"\2":', module_exports_str)
                                    .replace("'", "\""))
        module_exports: Dict[str, Any] = json.loads(module_exports_str)
        return module_exports
    return None


def parse_webpack_file(file_content: str, relevant_packages: Set[str]) -> Dict[str, Any]:
    output: Dict[str, Any] = {"packageAliases": {}}
    module_exports_json = _parse_export(file_content, MODULE_EXPORTS_PATTERN)
    if module_exports_json:
        aliases = module_exports_json.get("resolve", {}).get("alias", {})
        for imported_name in aliases:
            package_name = aliases[imported_name]
            if package_name in relevant_packages:
                output["packageAliases"].setdefault(package_name, {"packageAliases": []})["packageAliases"].append(imported_name)
    return output


def parse_tsconfig_file(file_content: str, relevant_packages: Set[str]) -> Dict[str, Any]:
    output: Dict[str, Any] = {"packageAliases": {}}
    tsconfig_json = load_json_with_comments(file_content)
    paths = tsconfig_json.get("compilerOptions", {}).get("paths", {})
    for imported_name in paths:
        for package_relative_path in paths[imported_name]:
            package_name = os.path.basename(package_relative_path)
            if package_name in relevant_packages:
                output["packageAliases"].setdefault(package_name, {"packageAliases": []})["packageAliases"].append(imported_name)
    return output


def parse_babel_file(file_content: str, relevant_packages: Set[str]) -> Dict[str, Any]:
    output: Dict[str, Any] = {"packageAliases": {}}
    babelrc_json = load_json_with_comments(file_content)
    plugins = babelrc_json.get("plugins", {})
    for plugin in plugins:
        if len(plugin) > 1:
            plugin_object = plugin[1]
            aliases = plugin_object.get("alias", {})
            for imported_name in aliases:
                package_name = aliases[imported_name]
                if package_name in relevant_packages:
                    output["packageAliases"].setdefault(package_name, {"packageAliases": []})["packageAliases"].append(imported_name)
    return output


def parse_rollup_file(file_content: str, relevant_packages: Set[str]) -> Dict[str, Any]:
    output: Dict[str, Any] = {"packageAliases": {}}
    export_default_match = re.search(EXPORT_DEFAULT_PATTERN, file_content, re.DOTALL)
    if export_default_match:
        export_default_str = export_default_match.group(1)
        # for having for all the keys and values double quotes and removing spaces
        export_default_str = re.sub(r'\s+', '', re.sub(r'([{\s,])(\w+):', r'\1"\2":', export_default_str)
                                    .replace("'", "\""))

        # Defining a regular expression pattern to match the elements within the "plugins" list
        pattern = r'alias\(\{[^)]*\}\)'
        matches = re.findall(pattern, export_default_str)

        for alias_object_str in matches:
            alias_object = json.loads(alias_object_str[6:-1])  # removing 'alias(' and ')'
            for entry in alias_object.get("entries", []):
                package_name = entry["replacement"]
                if entry["replacement"] in relevant_packages:
                    imported_name = entry["find"]
                    output["packageAliases"].setdefault(package_name, {"packageAliases": []})["packageAliases"].append(imported_name)
    return output


def parse_package_json_file(file_content: str, relevant_packages: Set[str]) -> Dict[str, Any]:
    output: Dict[str, Any] = {"packageAliases": {}}
    try:
        package_json = load_json_with_comments(file_content)
    except JSONDecodeError:
        logging.warning('unable to parse package json file')
        return output

    aliases: Dict[str, str] = dict()
    if "alias" in package_json:
        aliases.update(package_json["alias"])
    if package_json.get("aliasify", {}).get("aliases"):
        aliases.update(package_json["aliasify"]["aliases"])
    for imported_name in aliases:
        package_name = aliases[imported_name]
        if package_name in relevant_packages:
            output["packageAliases"].setdefault(package_name, {"packageAliases": []})["packageAliases"].append(imported_name)
    return output


def parse_snowpack_file(file_content: str, relevant_packages: Set[str]) -> Dict[str, Any]:
    output: Dict[str, Any] = {"packageAliases": {}}
    module_exports_json = _parse_export(file_content, MODULE_EXPORTS_PATTERN)
    if module_exports_json:
        aliases = module_exports_json.get("alias", {})
        for imported_name in aliases:
            package_name = aliases[imported_name]
            if package_name in relevant_packages:
                if package_name in relevant_packages:
                    output["packageAliases"].setdefault(package_name, {"packageAliases": []})["packageAliases"].append(imported_name)
    return output


def parse_vite_file(file_content: str, relevant_packages: Set[str]) -> Dict[str, Any]:
    output: Dict[str, Any] = {"packageAliases": {}}
    export_default_match = _parse_export(file_content, EXPORT_DEFAULT_PATTERN)
    if export_default_match:
        aliases = export_default_match.get("resolve", {}).get("alias", {})
        for imported_name in aliases:
            package_name = aliases[imported_name]
            if package_name in relevant_packages:
                output["packageAliases"].setdefault(package_name, {"packageAliases": []})["packageAliases"].append(imported_name)
    return output
