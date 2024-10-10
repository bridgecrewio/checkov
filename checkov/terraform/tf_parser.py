from __future__ import annotations

import json
import logging
import os
import platform
import threading
from collections import defaultdict
from pathlib import Path
from typing import Optional, Dict, Mapping, Set, Tuple, Callable, Any, List, cast, TYPE_CHECKING, overload, TextIO, Type

import hcl2

from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.runners.base_runner import filter_ignored_paths, IGNORE_HIDDEN_DIRECTORY_ENV
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR, RESOLVED_MODULE_ENTRY_NAME
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.common.util.deep_merge import pickle_deep_merge
from checkov.common.util.env_vars_config import env_vars_config
from checkov.common.util.stopit import ThreadingTimeout, SignalTimeout
from checkov.common.util.stopit.utils import BaseTimeout
from checkov.common.util.type_forcers import force_list
from checkov.common.variables.context import EvaluationContext
from checkov.terraform import validate_malformed_definitions, clean_bad_definitions
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.module import Module
from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.module_finder import load_tf_modules
from checkov.terraform.module_loading.registry import module_loader_registry as default_ml_registry, \
    ModuleLoaderRegistry
from checkov.common.util.parser_utils import is_acceptable_module_param
from checkov.terraform.modules.module_utils import safe_index, \
    remove_module_dependency_from_path, \
    clean_parser_types, serialize_definitions, _Hcl2Payload
from checkov.terraform.modules.module_objects import TFModule, TFDefinitionKey

if TYPE_CHECKING:
    from typing_extensions import TypeGuard


def _filter_ignored_paths(root: str, paths: list[str], excluded_paths: list[str] | None) -> None:
    filter_ignored_paths(root, paths, excluded_paths)
    for path in force_list(paths):
        if path == default_ml_registry.external_modules_folder_name:
            paths.remove(path)


class TFParser:
    def __init__(self, module_class: type[Module] = Module) -> None:
        self.module_class = module_class
        self._parsed_directories: set[str] = set()
        self.external_modules_source_map: Dict[Tuple[str, str], str] = {}
        self.module_address_map: Dict[Tuple[str, str], str] = {}
        self.loaded_files_map: dict[str, dict[str, list[dict[str, Any]]] | None] = {}
        self.external_variables_data: list[tuple[str, Any, str]] = []
        self.temp_tf_definition: dict[str, Any] = {}

    def _init(self, directory: str,
              out_evaluations_context: Dict[TFDefinitionKey, Dict[str, EvaluationContext]] | None,
              out_parsing_errors: Dict[str, Exception] | None,
              env_vars: Mapping[str, str] | None,
              download_external_modules: bool,
              external_modules_download_path: str,
              excluded_paths: Optional[List[str]] = None,
              tf_var_files: Optional[List[str]] = None) -> None:
        self.directory = directory
        self.out_definitions: dict[TFDefinitionKey, dict[str, list[dict[str, Any]]]] = {}
        self.out_evaluations_context = {} if out_evaluations_context is None else out_evaluations_context
        self.out_parsing_errors = {} if out_parsing_errors is None else out_parsing_errors
        self.env_vars = dict(os.environ) if env_vars is None else env_vars
        self.download_external_modules = download_external_modules
        self.external_modules_download_path = external_modules_download_path
        self.external_modules_source_map = {}
        self.module_address_map = {}
        self.tf_var_files = tf_var_files
        self.dirname_cache: dict[str, str] = {}
        self.excluded_paths = excluded_paths
        self.visited_definition_keys: set[TFDefinitionKey] = set()
        self.module_to_resolved: dict[tuple[TFDefinitionKey | None, str], list[TFDefinitionKey]] = {}
        self.keys_to_remove: set[TFDefinitionKey] = set()

    def _check_process_dir(self, directory: str) -> bool:
        if directory not in self._parsed_directories:
            self._parsed_directories.add(directory)
            return True
        else:
            return False

    def parse_directory(
            self,
            directory: str,
            out_evaluations_context: Dict[TFDefinitionKey, Dict[str, EvaluationContext]] | None = None,
            out_parsing_errors: Dict[str, Exception] | None = None,
            env_vars: Mapping[str, str] | None = None,
            download_external_modules: bool = False,
            external_modules_download_path: str = DEFAULT_EXTERNAL_MODULES_DIR,
            excluded_paths: Optional[List[str]] = None,
            vars_files: Optional[List[str]] = None,
            external_modules_content_cache: Optional[Dict[str, ModuleContent | None]] = None,
    ) -> dict[TFDefinitionKey, dict[str, list[dict[str, Any]]]]:
        self._init(directory, out_evaluations_context, out_parsing_errors, env_vars,
                   download_external_modules, external_modules_download_path, excluded_paths)
        self._parsed_directories.clear()
        default_ml_registry.root_dir = directory
        default_ml_registry.download_external_modules = download_external_modules
        default_ml_registry.external_modules_folder_name = external_modules_download_path
        default_ml_registry.module_content_cache = external_modules_content_cache if external_modules_content_cache else {}
        load_tf_modules(directory)
        self._parse_directory(dir_filter=lambda d: self._check_process_dir(d), vars_files=vars_files)
        self._update_resolved_modules()
        return self.out_definitions

    def parse_file(self, file: str, parsing_errors: dict[str, Exception]) -> Optional[Dict[str, Any]]:
        if file.endswith(".tf") or file.endswith(".tf.json") or file.endswith(".hcl"):
            parse_result = load_or_die_quietly(file, parsing_errors)
            if parse_result:
                parse_result = serialize_definitions(parse_result)
                parse_result = clean_parser_types(parse_result)
                return parse_result

        return None

    def _parse_directory(self, include_sub_dirs: bool = True,
                         module_loader_registry: ModuleLoaderRegistry = default_ml_registry,
                         dir_filter: Callable[[str], bool] = lambda _: True,
                         vars_files: Optional[List[str]] = None) -> None:

        keys_referenced_as_modules: set[TFDefinitionKey] = set()

        if include_sub_dirs:
            for sub_dir, d_names, _ in os.walk(self.directory):
                _filter_ignored_paths(sub_dir, d_names, self.excluded_paths)
                if dir_filter(os.path.abspath(sub_dir)):
                    self._internal_dir_load(sub_dir, module_loader_registry, dir_filter,
                                            keys_referenced_as_modules, vars_files=vars_files,
                                            excluded_paths=self.excluded_paths)
        else:
            self._internal_dir_load(self.directory, module_loader_registry, dir_filter,
                                    keys_referenced_as_modules, vars_files=vars_files)

        for key in keys_referenced_as_modules:
            if key in self.out_definitions:
                del self.out_definitions[key]

    def _internal_dir_load(
            self,
            directory: str,
            module_loader_registry: ModuleLoaderRegistry,
            dir_filter: Callable[[str], bool],
            keys_referenced_as_modules: set[TFDefinitionKey],
            specified_vars: Optional[Mapping[str, str]] = None,
            vars_files: Optional[List[str]] = None,
            excluded_paths: Optional[List[str]] = None,
            nested_modules_data: dict[str, Any] | None = None,
    ) -> None:

        dir_contents = list(os.scandir(directory))
        if excluded_paths or IGNORE_HIDDEN_DIRECTORY_ENV:
            filter_ignored_paths(directory, dir_contents, excluded_paths)

        tf_files_to_load = self.handle_variables(dir_contents, vars_files, specified_vars)
        files_to_data = self._load_files(tf_files_to_load)
        for file, data in sorted(files_to_data, key=lambda x: x[0]):
            if not data:
                continue
            self.out_definitions[TFDefinitionKey(file)] = data
            self.add_external_vars_from_data(data, file)

        force_final_module_load = False
        for i in range(0, 10):
            logging.debug(f"Module load loop {i}")
            dir_filter(directory)
            has_more_modules = self._load_modules(
                directory, module_loader_registry, dir_filter,
                keys_referenced_as_modules, force_final_module_load,
                nested_modules_data=nested_modules_data
            )
            made_var_changes = False
            if not has_more_modules:
                break
            elif not made_var_changes:
                force_final_module_load = True

    def _load_files(
            self,
            files: list[os.DirEntry[str]],
    ) -> list[tuple[str, dict[str, list[dict[str, Any]]] | None]]:
        def _load_file(
                file: os.DirEntry[str]
        ) -> tuple[tuple[str, dict[str, list[dict[str, Any]]] | None], dict[str, Exception]]:
            parsing_errors: dict[str, Exception] = {}
            result = load_or_die_quietly(file, parsing_errors)
            for path, e in parsing_errors.items():
                parsing_errors[path] = e

            return (file.path, result), parsing_errors

        files_to_data: list[tuple[str, dict[str, list[dict[str, Any]]] | None]] = []
        files_to_parse = []
        for file in files:
            data = self.loaded_files_map.get(file.path)
            if data:
                files_to_data.append((file.path, data))
            else:
                files_to_parse.append(file)

        results = [_load_file(f) for f in files_to_parse]
        for result, parsing_errors in results:
            self.out_parsing_errors.update(parsing_errors)
            files_to_data.append(result)
            if result[0] not in self.loaded_files_map:
                self.loaded_files_map[result[0]] = result[1]
        return files_to_data

    def _load_modules(self, root_dir: str, module_loader_registry: ModuleLoaderRegistry,
                      dir_filter: Callable[[str], bool],
                      keys_referenced_as_modules: Set[TFDefinitionKey], ignore_unresolved_params: bool = False,
                      nested_modules_data: dict[str, Any] | None = None) -> bool:
        all_module_definitions: dict[TFDefinitionKey, dict[str, list[dict[str, Any]]]] = {}
        skipped_a_module = False
        for file in list(self.out_definitions.keys()):
            if not self.should_loaded_file(file, root_dir):
                continue

            #  Dont run over the nested because we already run on them - dont remove.
            if file.tf_source_modules:
                continue

            file_data = self.out_definitions.get(file)
            if file_data is None:
                continue
            module_calls = file_data.get("module")
            if not module_calls or not isinstance(module_calls, list):
                continue

            for module_call in module_calls:
                if not isinstance(module_call, dict):
                    continue

                for module_call_name, module_call_data in module_call.items():
                    if not isinstance(module_call_data, dict):
                        continue

                    file_key = self.get_file_key_with_nested_data(file, nested_modules_data)
                    current_nested_data = (file_key, module_call_name)
                    resolved_loc_list = []
                    if current_nested_data in self.module_to_resolved:
                        resolved_loc_list = self.module_to_resolved[current_nested_data]
                    self.module_to_resolved[current_nested_data] = resolved_loc_list

                    specified_vars = {
                        k: v[0] if isinstance(v, list) and v else v
                        for k, v in module_call_data.items()
                        if k != "source" and k != "version"
                    }
                    skip_module = self.should_skip_a_module(specified_vars, ignore_unresolved_params)
                    if skip_module:
                        # keep module skip info till the end
                        skipped_a_module = True
                        continue

                    version = self.get_module_version(module_call_data)
                    source = self.get_module_source(module_call_data, module_call_name, file)
                    if not source:
                        continue

                    try:
                        content_path = self.get_content_path(module_loader_registry, root_dir, source, version)
                        if not content_path:
                            continue
                        new_nested_modules_data = {'module_name': module_call_name, 'file': file,
                                                   'nested_modules_data': nested_modules_data}
                        self._internal_dir_load(
                            directory=content_path,
                            module_loader_registry=module_loader_registry,
                            dir_filter=dir_filter, specified_vars=specified_vars,
                            keys_referenced_as_modules=keys_referenced_as_modules,
                            nested_modules_data=new_nested_modules_data
                        )

                        module_definitions = {
                            path: definition
                            for path, definition in self.out_definitions.items()
                            if self.get_dirname(path) == content_path and not path.tf_source_modules
                        }
                        if not module_definitions:
                            continue

                        keys = list(module_definitions.keys())
                        for key in keys:
                            if not self.should_process_key(key, file):
                                continue
                            keys_referenced_as_modules.add(key)
                            new_key = self.get_new_nested_module_key(key, file, module_call_name, nested_modules_data)
                            if new_key in self.visited_definition_keys:
                                del module_definitions[key]
                                del self.out_definitions[key]
                                continue

                            module_definitions[new_key] = module_definitions[key]
                            del module_definitions[key]
                            del self.out_definitions[key]
                            self.keys_to_remove.add(key)

                            self.visited_definition_keys.add(new_key)
                            if new_key not in resolved_loc_list:
                                resolved_loc_list.append(new_key)

                        if all_module_definitions:
                            pickle_deep_merge(all_module_definitions, module_definitions)
                        else:
                            all_module_definitions = module_definitions

                        self.external_modules_source_map[(source, version)] = content_path
                    except Exception as e:
                        logging.warning(
                            f"Unable to load module - source: {source}, version: {version}, error: {str(e)}")

        if all_module_definitions:
            pickle_deep_merge(self.out_definitions, all_module_definitions)
        return skipped_a_module

    def parse_hcl_module(
            self,
            source_dir: str,
            source: str,
            download_external_modules: bool = False,
            external_modules_download_path: str = DEFAULT_EXTERNAL_MODULES_DIR,
            parsing_errors: dict[str, Exception] | None = None,
            excluded_paths: list[str] | None = None,
            vars_files: list[str] | None = None,
            external_modules_content_cache: dict[str, ModuleContent | None] | None = None,
    ) -> tuple[Module, dict[TFDefinitionKey, dict[str, Any]]]:
        tf_definitions = self.parse_directory(
            directory=source_dir, out_evaluations_context={},
            out_parsing_errors=parsing_errors if parsing_errors is not None else {},
            download_external_modules=download_external_modules,
            external_modules_download_path=external_modules_download_path, excluded_paths=excluded_paths,
            vars_files=vars_files, external_modules_content_cache=external_modules_content_cache
        )
        tf_definitions = clean_parser_types(tf_definitions)
        tf_definitions = serialize_definitions(tf_definitions)

        module, tf_definitions = self.parse_hcl_module_from_tf_definitions(tf_definitions, source_dir, source)

        return module, tf_definitions

    def parse_multi_graph_hcl_module(
            self,
            source_dir: str,
            source: str,
            download_external_modules: bool = False,
            external_modules_download_path: str = DEFAULT_EXTERNAL_MODULES_DIR,
            parsing_errors: dict[str, Exception] | None = None,
            excluded_paths: list[str] | None = None,
            vars_files: list[str] | None = None,
            external_modules_content_cache: dict[str, ModuleContent | None] | None = None,
    ) -> list[tuple[Module, list[dict[TFDefinitionKey, dict[str, Any]]]]]:
        """
        This function is similar to parse_hcl_module, except that it creates a list of tuples instead of a single tuple.
        The objective is to create a collection of TF definitions based on directory, instead of a single big structure.
        This will allow us to boost performance by running on several smaller objects rather than a single one.
        """
        tf_definitions = self.parse_directory(
            directory=source_dir, out_evaluations_context={},
            out_parsing_errors=parsing_errors if parsing_errors is not None else {},
            download_external_modules=download_external_modules,
            external_modules_download_path=external_modules_download_path, excluded_paths=excluded_paths,
            vars_files=vars_files, external_modules_content_cache=external_modules_content_cache
        )
        tf_definitions = clean_parser_types(tf_definitions)
        tf_definitions = serialize_definitions(tf_definitions)

        dirs_to_definitions = self.create_definition_by_dirs(tf_definitions)

        definitions_dir_and_source_iterable = [(definitions, source_path, source) for source_path, definitions in
                                               dirs_to_definitions.items()]
        modules_and_definitions_tuple: list[tuple[Module, list[dict[TFDefinitionKey, dict[str, Any]]]]] = \
            list(parallel_runner.run_function(self.parse_hcl_module_from_multi_tf_definitions,
                                              definitions_dir_and_source_iterable))

        return modules_and_definitions_tuple

    def create_definition_by_dirs(self, tf_definitions: dict[TFDefinitionKey, dict[str, list[dict[str, Any]]]]
                                  ) -> dict[str, list[dict[TFDefinitionKey, dict[str, Any]]]]:
        dirs_to_definitions: dict[str, list[dict[TFDefinitionKey, dict[str, Any]]]] = defaultdict(list)
        for tf_definition_key, tf_value in tf_definitions.items():
            source_module = tf_definition_key.tf_source_modules
            if source_module is None:
                # No module - add new entry to dirs_to_definitions with the path as key
                dir_path = os.path.dirname(tf_definition_key.file_path)
                dirs_to_definitions[dir_path].append({tf_definition_key: tf_value})
            else:
                # iterate over nested modules while adding directories on the way
                while source_module is not None:
                    if source_module.nested_tf_module is None:
                        dir_path = os.path.dirname(source_module.path)
                        dirs_to_definitions[dir_path].append({tf_definition_key: tf_value})
                    source_module = source_module.nested_tf_module
        return dirs_to_definitions

    def _remove_unused_path_recursive(self, path: TFDefinitionKey) -> None:
        self.out_definitions.pop(path, None)
        for key in list(self.module_to_resolved.keys()):
            file_key = None
            if isinstance(key[0], TFDefinitionKey):
                file_key = key[0]
            elif key[0] is not None:
                file_key, module_index, module_name = key
            if path == file_key:
                for resolved_path in self.module_to_resolved[key]:
                    self._remove_unused_path_recursive(resolved_path)
                self.module_to_resolved.pop(key, None)

    def _update_resolved_modules(self) -> None:
        for key in list(self.module_to_resolved.keys()):
            file_key, module_name = key
            if file_key in self.keys_to_remove:
                for path in self.module_to_resolved[key]:
                    self._remove_unused_path_recursive(path)
                self.module_to_resolved.pop(key, None)

        for key, resolved_list in self.module_to_resolved.items():
            file_key, module_name = key
            if file_key not in self.out_definitions:
                continue

            idx = self.get_idx_by_module_name(self.out_definitions[file_key]['module'], module_name)
            if idx is None:
                continue

            self.out_definitions[file_key]['module'][idx][module_name][RESOLVED_MODULE_ENTRY_NAME] = resolved_list

    @staticmethod
    def get_idx_by_module_name(module_data_list: list[dict[str, Any]], module_name: str) -> int | None:
        for idx, module_data in enumerate(module_data_list):
            if module_name in module_data:
                return idx

        return None

    @overload
    def parse_hcl_module_from_tf_definitions(
            self,
            tf_definitions: dict[str, dict[str, Any]],
            source_dir: str,
            source: str,
    ) -> tuple[Module, dict[str, dict[str, Any]]]:
        ...

    @overload
    def parse_hcl_module_from_tf_definitions(
            self,
            tf_definitions: dict[TFDefinitionKey, dict[str, Any]],
            source_dir: str,
            source: str,
    ) -> tuple[Module, dict[TFDefinitionKey, dict[str, Any]]]:
        ...

    def parse_hcl_module_from_tf_definitions(
            self,
            tf_definitions: dict[str, dict[str, Any]] | dict[TFDefinitionKey, dict[str, Any]],
            source_dir: str,
            source: str,
    ) -> tuple[Module, dict[str, dict[str, Any]] | dict[TFDefinitionKey, dict[str, Any]]]:
        module = self.get_new_module(
            source_dir=source_dir,
            external_modules_source_map=self.external_modules_source_map,
        )
        self.add_tfvars(module, source)
        copy_of_tf_definitions = pickle_deepcopy(tf_definitions)
        module.temp_tf_definition = tf_definitions  # type:ignore  # will be TFDefinitionKey and not string
        for file_path, blocks in copy_of_tf_definitions.items():
            for block_type in blocks:
                try:
                    module.add_blocks(block_type, blocks[block_type], file_path, source)
                except Exception as e:
                    logging.warning(f'Failed to add block {blocks[block_type]}. Error:')
                    logging.warning(e, exc_info=False)
        return module, tf_definitions

    def parse_hcl_module_from_multi_tf_definitions(
            self,
            tf_definitions: list[dict[TFDefinitionKey, dict[str, Any]]],
            source_dir: str,
            source: str,
    ) -> tuple[Module, list[dict[TFDefinitionKey, dict[str, Any]]]]:
        module = self.get_new_module(
            source_dir=source_dir,
            external_modules_source_map=self.external_modules_source_map,
        )
        self.add_tfvars_with_source_dir(module, source, source_dir)
        copy_of_tf_definitions = pickle_deepcopy(tf_definitions)
        for tf_def in copy_of_tf_definitions:
            for file_path, blocks in tf_def.items():
                for block_type in blocks:
                    try:
                        module.add_blocks(block_type, blocks[block_type], file_path, source)
                    except Exception as e:
                        logging.warning(f'Failed to add block {blocks[block_type]}. Error:')
                        logging.warning(e, exc_info=False)
        return module, tf_definitions

    def get_file_key_with_nested_data(
            self, file: TFDefinitionKey | None, nested_data: dict[str, Any] | None
    ) -> TFDefinitionKey | None:
        if not nested_data or file is None:
            return file
        nested_str = self.get_file_key_with_nested_data(nested_data.get("file"), nested_data.get('nested_modules_data'))
        nested_module_name = nested_data.get('module_name')
        return get_tf_definition_object_from_module_dependency(file, nested_str, nested_module_name)

    def get_new_nested_module_key(
            self, key: TFDefinitionKey, file: TFDefinitionKey | None, module_name: str | None,
            nested_data: Optional[dict[str, Any]]
    ) -> TFDefinitionKey:
        if not nested_data or not file:
            return get_tf_definition_object_from_module_dependency(key, file, module_name)
        visited_key_to_add = get_tf_definition_object_from_module_dependency(key, file, module_name)
        self.visited_definition_keys.add(visited_key_to_add)
        nested_key = self.get_new_nested_module_key(file, nested_data.get('file'),
                                                    nested_data.get('module_name'),
                                                    nested_data.get('nested_modules_data'))
        return get_tf_definition_object_from_module_dependency(key, nested_key, module_name)

    def add_tfvars(self, module: Module, source: str) -> None:
        if not self.external_variables_data:
            return
        for (var_name, default, path) in self.external_variables_data:
            if ".tfvars" in path:
                block = [{var_name: {"default": default}}]
                module.add_blocks(BlockType.TF_VARIABLE, block, path, source)

    def add_tfvars_with_source_dir(self, module: Module, source: str, source_dir: str) -> None:
        if not self.external_variables_data:
            return
        for var_name, default, path in self.external_variables_data:
            if ".tfvars" in path:
                if Path(source_dir) in Path(path).parents:
                    block = [{var_name: {"default": default}}]
                    module.add_blocks(BlockType.TF_VARIABLE, block, path, source)

    def get_dirname(self, path: TFDefinitionKey) -> str:
        file_path = path.file_path
        dirname_path = self.dirname_cache.get(file_path)
        if not dirname_path:
            dirname_path = os.path.dirname(file_path)
            self.dirname_cache[file_path] = dirname_path
        return dirname_path

    def should_loaded_file(self, file: TFDefinitionKey, root_dir: str) -> bool:
        return not self.get_dirname(file) != root_dir

    def get_module_source(
            self, module_call_data: dict[str, Any], module_call_name: str, file: TFDefinitionKey
    ) -> Optional[str]:
        source = module_call_data.get("source")
        if not source or not isinstance(source, list):
            return None
        source = source[0]
        if not self.is_valid_source(source, module_call_name):
            return None

        if source.startswith("./") or source.startswith("../"):
            file_to_load = file.file_path
            source = os.path.normpath(
                os.path.join(os.path.dirname(remove_module_dependency_from_path(file_to_load)), source))
        return source

    def add_external_vars_from_data(self, data: dict[str, Any], file: str) -> None:
        var_blocks = data.get("variable")
        if var_blocks and isinstance(var_blocks, list):
            for var_block in var_blocks:
                if not isinstance(var_block, dict):
                    continue
                for var_name, var_definition in var_block.items():
                    if not isinstance(var_definition, dict):
                        continue

                    default_value = var_definition.get("default")
                    if default_value is not None and isinstance(default_value, list):
                        self.external_variables_data.append((var_name, default_value[0], file))

    def handle_variables(
            self,
            dir_contents: list[os.DirEntry[str]],
            vars_files: None | list[str],
            specified_vars: Mapping[str, str] | None,
    ) -> list[os.DirEntry[str]]:
        tf_files_to_load = []
        hcl_tfvars: Optional[os.DirEntry[str]] = None
        json_tfvars: Optional[os.DirEntry[str]] = None
        auto_vars_files: List[os.DirEntry[str]] = []
        explicit_var_files: List[os.DirEntry[str]] = []
        for file in dir_contents:
            try:
                if not file.is_file():
                    continue
            except OSError:
                continue

            if file.name == "terraform.tfvars.json":
                json_tfvars = file
            elif file.name == "terraform.tfvars":
                hcl_tfvars = file
            elif file.name.endswith(".auto.tfvars.json") or file.name.endswith(".auto.tfvars"):
                auto_vars_files.append(file)
            elif vars_files and file.path in vars_files:
                explicit_var_files.append(file)
            elif file.name.endswith(".tf") or file.name.endswith('.hcl'):  # TODO: add support for .tf.json
                tf_files_to_load.append(file)

        for key, value in self.env_vars.items():
            if not key.startswith("TF_VAR_"):
                continue
            self.external_variables_data.append((key[7:], value, f"env:{key}"))
        if hcl_tfvars:  # terraform.tfvars
            data = load_or_die_quietly(hcl_tfvars, self.out_parsing_errors, clean_definitions=False)
            if data:
                self.external_variables_data.extend([(k, safe_index(v, 0), hcl_tfvars.path) for k, v in data.items()])
        if json_tfvars:  # terraform.tfvars.json
            data = load_or_die_quietly(json_tfvars, self.out_parsing_errors)
            if data:
                self.external_variables_data.extend([(k, v, json_tfvars.path) for k, v in data.items()])

        auto_var_files_to_data = self._load_files(auto_vars_files)
        for var_file, data in sorted(auto_var_files_to_data, key=lambda x: x[0]):
            if data:
                self.external_variables_data.extend([(k, v, var_file) for k, v in data.items()])

        explicit_var_files_to_data = self._load_files(explicit_var_files)
        # it's possible that os.scandir returned the var files in a different order than they were specified
        if vars_files:
            for var_file, data in sorted(explicit_var_files_to_data, key=lambda x: vars_files.index(x[0])):
                if data:
                    self.external_variables_data.extend([(k, v, var_file) for k, v in data.items()])

        if specified_vars:  # specified
            self.external_variables_data.extend([(k, v, "manual specification") for k, v in specified_vars.items()])

        return tf_files_to_load

    @staticmethod
    def get_module_version(module_call_data: dict[str, Any]) -> str:
        version = module_call_data.get("version", "latest")
        if version and isinstance(version, list):
            version = version[0]
        return cast(str, version)

    @staticmethod
    def should_process_key(key: TFDefinitionKey, file: TFDefinitionKey) -> bool:
        return bool(not key.tf_source_modules or file.tf_source_modules)

    @staticmethod
    def is_valid_source(source: Any, module_call_name: str) -> TypeGuard[str]:
        if not isinstance(source, str):
            logging.debug(f"Skipping loading of {module_call_name} as source is not a string, it is: {source}")
            return False
        elif source in ['./', '.']:
            logging.debug(f"Skipping loading of {module_call_name} as source is the current dir")
            return False
        return True

    @staticmethod
    def should_skip_a_module(specified_vars: dict[str, Any], ignore_unresolved_params: bool) -> bool:
        if not ignore_unresolved_params:
            has_unresolved_params = False
            for k, v in specified_vars.items():
                if not is_acceptable_module_param(v) or not is_acceptable_module_param(k):
                    has_unresolved_params = True
                    break
            if has_unresolved_params:
                return True
        return False

    @staticmethod
    def get_content_path(module_loader_registry: ModuleLoaderRegistry, root_dir: str, source: str, version: str) -> \
            Optional[str]:
        content = module_loader_registry.load(root_dir, source, version)
        if not content or not content.loaded():
            logging.info(f'Got no content for {source}:{version}')
            return None
        return content.path()

    @staticmethod
    def get_new_module(
            source_dir: str,
            external_modules_source_map: dict[tuple[str, str], str],
    ) -> Module:
        return Module(
            source_dir=source_dir,
            external_modules_source_map=external_modules_source_map,
        )


def is_nested_object(full_path: TFDefinitionKey) -> bool:
    return True if full_path.tf_source_modules else False


def get_tf_definition_object_from_module_dependency(
        path: TFDefinitionKey, module_dependency: TFDefinitionKey | None, module_dependency_name: str | None
) -> TFDefinitionKey:
    if not module_dependency:
        return path
    if not is_nested_object(module_dependency):
        return TFDefinitionKey(path.file_path, TFModule(path=module_dependency.file_path, name=module_dependency_name))
    return TFDefinitionKey(path.file_path, TFModule(path=module_dependency.file_path, name=module_dependency_name,
                                                    nested_tf_module=module_dependency.tf_source_modules))


def load_or_die_quietly(
        file: str | Path | os.DirEntry[str], parsing_errors: dict[str, Exception], clean_definitions: bool = True
) -> Optional[_Hcl2Payload]:
    """
    Load JSON or HCL, depending on filename.
    :return: None if the file can't be loaded
    """
    file_path = os.fspath(file)
    file_name = os.path.basename(file_path)

    if file_name.endswith('.tfvars'):
        clean_definitions = False

    try:
        logging.debug(f"Parsing {file_path}")

        with open(file_path, "r", encoding="utf-8-sig") as f:
            if file_name.endswith(".json"):
                return cast("_Hcl2Payload", json.load(f))
            else:
                raw_data = __parse_with_timeout(f)
                non_malformed_definitions = validate_malformed_definitions(raw_data)
                if clean_definitions:
                    return clean_bad_definitions(non_malformed_definitions)
                else:
                    return non_malformed_definitions
    except Exception as e:
        logging.debug(f'failed while parsing file {file_path}', exc_info=True)
        parsing_errors[file_path] = e
        return None


# if we are not running in a thread, run the hcl2.load function with a timeout, to prevent from getting stuck in parsing.
def __parse_with_timeout(f: TextIO) -> dict[str, list[dict[str, Any]]]:
    # setting up timeout class
    timeout_class: Optional[Type[BaseTimeout]] = None
    if platform.system() == 'Windows':
        timeout_class = ThreadingTimeout
    elif threading.current_thread() is threading.main_thread():
        timeout_class = SignalTimeout

    # if we're not running on the main thread, don't use timeout
    parsing_timeout = env_vars_config.HCL_PARSE_TIMEOUT_SEC or 0
    if not timeout_class or not parsing_timeout:
        return hcl2.load(f)

    with timeout_class(parsing_timeout) as to_ctx_mgr:
        raw_data = hcl2.load(f)
    if to_ctx_mgr.state == to_ctx_mgr.TIMED_OUT:
        logging.debug(f"reached timeout when parsing file {f} using hcl2")
        raise Exception(f"file took more than {parsing_timeout} seconds to parse")
    return raw_data
