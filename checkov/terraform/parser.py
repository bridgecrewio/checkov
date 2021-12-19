import datetime
import json
import logging
import os
import re
from copy import deepcopy
from json import dumps, loads, JSONEncoder
from pathlib import Path
from typing import Optional, Dict, Mapping, Set, Tuple, Callable, Any, List, Type

import deep_merge
import hcl2
from lark import Tree

from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.runners.base_runner import filter_ignored_paths
from checkov.common.util.config_utils import should_scan_hcl_files
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR, RESOLVED_MODULE_ENTRY_NAME
from checkov.common.util.json_utils import CustomJSONEncoder
from checkov.common.variables.context import EvaluationContext
from checkov.terraform.checks.utils.dependency_path_handler import unify_dependency_path
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.module import Module
from checkov.terraform.graph_builder.utils import remove_module_dependency_in_path
from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.module_finder import load_tf_modules
from checkov.terraform.module_loading.registry import module_loader_registry as default_ml_registry, \
    ModuleLoaderRegistry
from checkov.terraform.parser_utils import eval_string, find_var_blocks

external_modules_download_path = os.environ.get('EXTERNAL_MODULES_DIR', DEFAULT_EXTERNAL_MODULES_DIR)


def _filter_ignored_paths(root, paths, excluded_paths):
    filter_ignored_paths(root, paths, excluded_paths)
    [paths.remove(path) for path in list(paths) if path in [default_ml_registry.external_modules_folder_name]]


class Parser:
    def __init__(self, module_class: Type[Module] = Module):
        self.module_class = module_class
        self._parsed_directories = set()
        self.external_modules_source_map: Dict[Tuple[str, str], str] = {}
        self.module_address_map: Dict[Tuple[str, str], str] = {}
        self.loaded_files_map = {}

        # This ensures that we don't try to double-load modules
        # Tuple is <file>, <module_index>, <name> (see _load_modules)
        self._loaded_modules: Set[Tuple[str, int, str]] = set()
        self.external_variables_data = []

    def _init(self, directory: str, out_definitions: Optional[Dict],
              out_evaluations_context: Dict[str, Dict[str, EvaluationContext]],
              out_parsing_errors: Dict[str, Exception],
              env_vars: Mapping[str, str],
              download_external_modules: bool,
              external_modules_download_path: str,
              excluded_paths: Optional[List[str]] = None,
              tf_var_files: Optional[List[str]] = None):
        self.directory = directory
        self.out_definitions = out_definitions
        self.out_evaluations_context = out_evaluations_context
        self.out_parsing_errors = out_parsing_errors
        self.env_vars = env_vars
        self.download_external_modules = download_external_modules
        self.external_modules_download_path = external_modules_download_path
        self.external_modules_source_map = {}
        self.module_address_map = {}
        self.tf_var_files = tf_var_files
        self.scan_hcl = should_scan_hcl_files()

        if self.out_evaluations_context is None:
            self.out_evaluations_context = {}
        if self.out_parsing_errors is None:
            self.out_parsing_errors = {}
        if self.env_vars is None:
            self.env_vars = dict(os.environ)
        self.excluded_paths = excluded_paths

    def _check_process_dir(self, directory):
        if directory not in self._parsed_directories:
            self._parsed_directories.add(directory)
            return True
        else:
            return False

    def parse_directory(self, directory: str, out_definitions: Optional[Dict],
                        out_evaluations_context: Dict[str, Dict[str, EvaluationContext]] = None,
                        out_parsing_errors: Dict[str, Exception] = None,
                        env_vars: Mapping[str, str] = None,
                        download_external_modules: bool = False,
                        external_modules_download_path: str = DEFAULT_EXTERNAL_MODULES_DIR,
                        excluded_paths: Optional[List[str]] = None,
                        vars_files: Optional[List[str]] = None,
                        external_modules_content_cache: Optional[Dict[str, ModuleContent]] = None):
        self._init(directory, out_definitions, out_evaluations_context, out_parsing_errors, env_vars,
                   download_external_modules, external_modules_download_path, excluded_paths)
        self._parsed_directories.clear()
        default_ml_registry.root_dir = directory
        default_ml_registry.download_external_modules = download_external_modules
        default_ml_registry.external_modules_folder_name = external_modules_download_path
        default_ml_registry.module_content_cache = external_modules_content_cache if external_modules_content_cache else {}
        load_tf_modules(directory)
        self._parse_directory(dir_filter=lambda d: self._check_process_dir(d), vars_files=vars_files)

    def parse_file(self, file: str, parsing_errors: Dict[str, Exception] = None, scan_hcl = False) -> Optional[Dict]:
        if file.endswith(".tf") or file.endswith(".tf.json") or (scan_hcl and file.endswith(".hcl")):
            parse_result = _load_or_die_quietly(Path(file), parsing_errors)
            if parse_result:
                parse_result = self._serialize_definitions(parse_result)
                parse_result = self._clean_parser_types(parse_result)
                return parse_result
        else:
            return None

    def _parse_directory(self, include_sub_dirs: bool = True,
                         module_loader_registry: ModuleLoaderRegistry = default_ml_registry,
                         dir_filter: Callable[[str], bool] = lambda _: True,
                         vars_files: Optional[List[str]] = None):
        """
    Load and resolve configuration files starting in the given directory, merging the
    resulting data into `tf_definitions`. This loads data according to the Terraform Code Organization
    specification (https://www.terraform.io/docs/configuration/index.html#code-organization), starting
    in the given directory and possibly moving out from there.

    The resulting data dictionary generally follows the layout of HCL parsing with a couple distinctions:
    - Data is broken out by file from which the data was loaded. So: <file>: <data>
      - Loaded modules will also be keyed by referrer info: <file>[<referring_file>#<index>]: <data>
    - Module block will included a "__resolved__" key with a list of the file/referrer names under
      which data for the file was loaded. For example: "__resolved__": ["main.tf#0"]. The values will
      correspond to the file names mentioned in the first bullet.
    - All variables that can be resolved will be resolved.


        :param include_sub_dirs:           If true, subdirectories will be walked.

        :param module_loader_registry:     Registry used for resolving modules. This allows customization of how
                                           much resolution is performed (and easier testing) by using a manually
                                           constructed registry rather than the default.
        :param dir_filter:                 Determines whether or not a directory should be processed. Returning
                                           True will allow processing. The argument will be the absolute path of
                                           the directory.
        """
        keys_referenced_as_modules: Set[str] = set()

        if include_sub_dirs:
            for sub_dir, d_names, f_names in os.walk(self.directory):
                # filter subdirectories for future iterations (we filter files while iterating the directory)
                _filter_ignored_paths(sub_dir, d_names, self.excluded_paths)
                if dir_filter(os.path.abspath(sub_dir)):
                    self._internal_dir_load(sub_dir, module_loader_registry, dir_filter,
                                            keys_referenced_as_modules, vars_files=vars_files,
                                            root_dir=self.directory, excluded_paths=self.excluded_paths)
        else:
            self._internal_dir_load(self.directory, module_loader_registry, dir_filter,
                                    keys_referenced_as_modules, vars_files=vars_files)

        # Ensure anything that was referenced as a module is removed
        for key in keys_referenced_as_modules:
            if key in self.out_definitions:
                del self.out_definitions[key]

    def _internal_dir_load(self, directory: str,
                           module_loader_registry: ModuleLoaderRegistry,
                           dir_filter: Callable[[str], bool],
                           keys_referenced_as_modules: Set[str],
                           specified_vars: Optional[Mapping[str, str]] = None,
                           module_load_context: Optional[str] = None,
                           vars_files: Optional[List[str]] = None,
                           root_dir: Optional[str] = None,
                           excluded_paths: Optional[List[str]] = None):
        """
    See `parse_directory` docs.
        :param directory:                  Directory in which .tf and .tfvars files will be loaded.
        :param module_loader_registry:     Registry used for resolving modules. This allows customization of how
                                       much resolution is performed (and easier testing) by using a manually
                                       constructed registry rather than the default.
        :param dir_filter:                 Determines whether or not a directory should be processed. Returning
                                       True will allow processing. The argument will be the absolute path of
                                       the directory.
        :param specified_vars:     Specifically defined variable values, overriding values from any other source.
        """

        # Stage 1: Look for applicable files in the directory:
        #          https://www.terraform.io/docs/configuration/index.html#code-organization
        #          Load the raw data for non-variable files, but perform no processing other than loading
        #          variable default values.
        #          Variable files are also flagged for later processing.
        var_value_and_file_map: Dict[str, Tuple[Any, str]] = {}
        hcl_tfvars: Optional[os.DirEntry] = None
        json_tfvars: Optional[os.DirEntry] = None
        auto_vars_files: List[os.DirEntry] = []  # *.auto.tfvars / *.auto.tfvars.json
        explicit_var_files: List[os.DirEntry] = []  # files passed with --var-file; only process the ones that are in this directory

        dir_contents = list(os.scandir(directory))
        if excluded_paths:
            filter_ignored_paths(root_dir, dir_contents, excluded_paths)

        tf_files_to_load = []
        for file in dir_contents:
            # Ignore directories and hidden files
            try:
                if not file.is_file() or file.name.startswith("."):
                    continue
            except OSError:
                # Skip files that can't be accessed
                continue

            # Variable files
            # See: https://www.terraform.io/docs/configuration/variables.html#variable-definitions-tfvars-files
            if file.name == "terraform.tfvars.json":
                json_tfvars = file
            elif file.name == "terraform.tfvars":
                hcl_tfvars = file
            elif file.name.endswith(".auto.tfvars.json") or file.name.endswith(".auto.tfvars"):
                auto_vars_files.append(file)
            elif vars_files and file.path in vars_files:
                explicit_var_files.append(file)

            # Resource files
            elif file.name.endswith(".tf") or (self.scan_hcl and file.name.endswith('.hcl')):  # TODO: add support for .tf.json
                tf_files_to_load.append(file)

        files_to_data = self._load_files(tf_files_to_load)

        for file, data in sorted(files_to_data, key=lambda x: x[0]):
            if not data:
                continue
            self.out_definitions[file] = data

            # Load variable defaults
            #  (see https://www.terraform.io/docs/configuration/variables.html#declaring-an-input-variable)
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
                            var_value_and_file_map[var_name] = default_value[0], file

        # Stage 2: Load vars in proper order:
        #          https://www.terraform.io/docs/configuration/variables.html#variable-definition-precedence
        #          Defaults are loaded in stage 1.
        #          Then loading in this order with later taking precedence:
        #             - Environment variables
        #             - The terraform.tfvars file, if present.
        #             - The terraform.tfvars.json file, if present.
        #             - Any *.auto.tfvars or *.auto.tfvars.json files, processed in lexical order of
        #               their filenames.
        #          Overriding everything else, variables form `specified_vars`, which are considered
        #          directly set.
        for key, value in self.env_vars.items():  # env vars
            if not key.startswith("TF_VAR_"):
                continue
            var_value_and_file_map[key[7:]] = value, f"env:{key}"
            self.external_variables_data.append((key[7:], value, f"env:{key}"))
        if hcl_tfvars:  # terraform.tfvars
            data = _load_or_die_quietly(hcl_tfvars, self.out_parsing_errors, clean_definitions=False)
            if data:
                var_value_and_file_map.update({k: (_safe_index(v, 0), hcl_tfvars.path) for k, v in data.items()})
                self.external_variables_data.extend([(k, _safe_index(v, 0), hcl_tfvars.path) for k, v in data.items()])
        if json_tfvars:  # terraform.tfvars.json
            data = _load_or_die_quietly(json_tfvars, self.out_parsing_errors)
            if data:
                var_value_and_file_map.update({k: (v, json_tfvars.path) for k, v in data.items()})
                self.external_variables_data.extend([(k, v, json_tfvars.path) for k, v in data.items()])

        auto_var_files_to_data = self._load_files(auto_vars_files)
        for var_file, data in sorted(auto_var_files_to_data, key=lambda x: x[0]):
            if data:
                var_value_and_file_map.update({k: (v, var_file) for k, v in data.items()})
                self.external_variables_data.extend([(k, v, var_file) for k, v in data.items()])

        explicit_var_files_to_data = self._load_files(explicit_var_files)
        # it's possible that os.scandir returned the var files in a different order than they were specified
        for var_file, data in sorted(explicit_var_files_to_data, key=lambda x: vars_files.index(x[0])):
            if data:
                var_value_and_file_map.update({k: (v, var_file) for k, v in data.items()})
                self.external_variables_data.extend([(k, v, var_file) for k, v in data.items()])

        if specified_vars:  # specified
            var_value_and_file_map.update({k: (v, "manual specification") for k, v in specified_vars.items()})
            self.external_variables_data.extend([(k, v, "manual specification") for k, v in specified_vars.items()])

        # Stage 4: Load modules
        #          This stage needs to be done in a loop (again... alas, no DAG) because modules might not
        #          be loadable until other modules are loaded. This happens when parameters to one module
        #          depend on the output of another. For such cases, the base module must be loaded, then
        #          a parameter resolution pass needs to happen, then the second module can be loaded.
        #
        #          One gotcha is that we need to make sure we load all modules at some point, even if their
        #          parameters don't resolve. So, if we hit a spot where resolution doesn't change anything
        #          and there are still modules to be loaded, they will be forced on the next pass.
        force_final_module_load = False
        for i in range(0, 10):  # circuit breaker - no more than 10 loops
            logging.debug("Module load loop %d", i)

            # Stage 4a: Load eligible modules
            has_more_modules = self._load_modules(directory, module_loader_registry,
                                                  dir_filter, module_load_context,
                                                  keys_referenced_as_modules,
                                                  force_final_module_load)

            # Stage 4b: Variable resolution round 2 - now with (possibly more) modules
            made_var_changes = False
            if not has_more_modules:
                break  # nothing more to do
            elif not made_var_changes:
                # If there are more modules to load but no variables were resolved, then to a final module
                # load, forcing things through without complete resolution.
                force_final_module_load = True

    def _load_files(self, files):
        def _load_file(file):
            parsing_errors = {}
            result = _load_or_die_quietly(file, parsing_errors)
            # the exceptions type can un-pickleable
            for path, e in parsing_errors.items():
                parsing_errors[path] = Exception(str(e))

            return (file.path, result), parsing_errors

        files_to_data = []
        files_to_parse = []
        for file in files:
            data = self.loaded_files_map.get(file.path)
            if data:
                files_to_data.append((file.path, data))
            else:
                files_to_parse.append(file)

        results = parallel_runner.run_function(_load_file, files_to_parse)
        for result, parsing_errors in results:
            self.out_parsing_errors.update(parsing_errors)
            files_to_data.append(result)
            if result[0] not in self.loaded_files_map:
                self.loaded_files_map[result[0]] = result[1]
        return files_to_data

    def _load_modules(self, root_dir: str, module_loader_registry: ModuleLoaderRegistry,
                      dir_filter: Callable[[str], bool], module_load_context: Optional[str],
                      keys_referenced_as_modules: Set[str], ignore_unresolved_params: bool = False) -> bool:
        """
        Load modules which have not already been loaded and can be loaded (don't have unresolved parameters).

        :param ignore_unresolved_params:    If true, not-yet-loaded modules will be loaded even if they are
                                            passed parameters that are not fully resolved.
        :return:                            True if there were modules that were not loaded due to unresolved
                                            parameters.
        """
        all_module_definitions = {}
        all_module_evaluations_context = {}
        skipped_a_module = False
        for file in list(self.out_definitions.keys()):
            # Don't process a file in a directory other than the directory we're processing. For example,
            # if we're down dealing with <top_dir>/<module>/something.tf, we don't want to rescan files
            # up in <top_dir>.
            if os.path.dirname(file) != root_dir:
                continue
            # Don't process a file reference which has already been processed
            if file.endswith("]"):
                continue

            file_data = self.out_definitions.get(file)
            if file_data is None:
                continue
            module_calls = file_data.get("module")
            if not module_calls or not isinstance(module_calls, list):
                continue

            for module_index, module_call in enumerate(module_calls):

                if not isinstance(module_call, dict):
                    continue

                # There should only be one module reference per outer dict, but... safety first
                for module_call_name, module_call_data in module_call.items():
                    if not isinstance(module_call_data, dict):
                        continue

                    module_address = (file, module_index, module_call_name)
                    if module_address in self._loaded_modules:
                        continue

                    # Variables being passed to module, "source" and "version" are reserved
                    specified_vars = {k: v[0] if isinstance(v, list) else v for k, v in module_call_data.items()
                                      if k != "source" and k != "version"}

                    if not ignore_unresolved_params:
                        has_unresolved_params = False
                        for k, v in specified_vars.items():
                            if not is_acceptable_module_param(v) or not is_acceptable_module_param(k):
                                has_unresolved_params = True
                                break
                        if has_unresolved_params:
                            skipped_a_module = True
                            continue
                    self._loaded_modules.add(module_address)

                    source = module_call_data.get("source")
                    if not source or not isinstance(source, list):
                        continue
                    source = source[0]
                    if not isinstance(source, str):
                        logging.debug(f"Skipping loading of {module_call_name} as source is not a string, it is: {source}")
                        continue

                    # Special handling for local sources to make sure we aren't double-parsing
                    if source.startswith("./") or source.startswith("../"):
                        source = os.path.normpath(
                            os.path.join(os.path.dirname(_remove_module_dependency_in_path(file)), source))

                    version = module_call_data.get("version", "latest")
                    if version and isinstance(version, list):
                        version = version[0]
                    try:
                        content = module_loader_registry.load(root_dir, source, version)
                        if not content.loaded():
                            logging.info(f'Got no content for {source}:{version}')
                            continue

                        self._internal_dir_load(directory=content.path(),
                                                module_loader_registry=module_loader_registry,
                                                dir_filter=dir_filter, specified_vars=specified_vars,
                                                module_load_context=module_load_context,
                                                keys_referenced_as_modules=keys_referenced_as_modules)

                        module_definitions = {path: self.out_definitions[path] for path in
                                              list(self.out_definitions.keys()) if
                                              os.path.dirname(path) == content.path()}

                        if not module_definitions:
                            continue

                        # NOTE: Modules are put into the main TF definitions structure "as normal" with the
                        #       notable exception of the file name. For loaded modules referrer information is
                        #       appended to the file name to create this format:
                        #         <file_name>[<referred_file>#<referrer_index>]
                        #       For example:
                        #         /the/path/module/my_module.tf[/the/path/main.tf#0]
                        #       The referrer and index allow a module allow a module to be loaded multiple
                        #       times with differing data.
                        #
                        #       In addition, the referring block will have a "__resolved__" key added with a
                        #       list pointing to the location of the module data that was resolved. For example:
                        #         "__resolved__": ["/the/path/module/my_module.tf[/the/path/main.tf#0]"]

                        resolved_loc_list = module_call_data.get(RESOLVED_MODULE_ENTRY_NAME)
                        if resolved_loc_list is None:
                            resolved_loc_list = []
                            module_call_data[RESOLVED_MODULE_ENTRY_NAME] = resolved_loc_list

                        # NOTE: Modules can load other modules, so only append referrer information where it
                        #       has not already been added.
                        keys = list(module_definitions.keys())
                        for key in keys:
                            if key.endswith("]") or file.endswith("]"):
                                continue
                            keys_referenced_as_modules.add(key)
                            new_key = f"{key}[{file}#{module_index}]"
                            module_definitions[new_key] = module_definitions[key]
                            del module_definitions[key]
                            del self.out_definitions[key]
                            if new_key not in resolved_loc_list:
                                resolved_loc_list.append(new_key)
                            if (file, module_call_name) not in self.module_address_map:
                                self.module_address_map[(file, module_call_name)] = str(module_index)
                        resolved_loc_list.sort()  # For testing, need predictable ordering

                        if all_module_definitions:
                            deep_merge.merge(all_module_definitions, module_definitions)
                        else:
                            all_module_definitions = module_definitions

                        self.external_modules_source_map[(source, version)] = content.path()
                    except Exception as e:
                        logging.warning("Unable to load module (source=\"%s\" version=\"%s\"): %s",
                                        source, version, e)

        if all_module_definitions:
            deep_merge.merge(self.out_definitions, all_module_definitions)
        if all_module_evaluations_context:
            deep_merge.merge(self.out_evaluations_context, all_module_evaluations_context)
        return skipped_a_module

    def parse_hcl_module(
        self,
        source_dir: str,
        source: str,
        download_external_modules: bool = False,
        external_modules_download_path: str = DEFAULT_EXTERNAL_MODULES_DIR,
        parsing_errors: Optional[Dict[str, Exception]] = None,
        excluded_paths: Optional[List[str]] = None,
        vars_files: Optional[List[str]] = None,
        external_modules_content_cache: Optional[Dict[str, ModuleContent]] = None
    ) -> Tuple[Module, Dict[str, Dict[str, Any]]]:
        tf_definitions: Dict[str, Dict[str, Any]] = {}
        self.parse_directory(directory=source_dir, out_definitions=tf_definitions, out_evaluations_context={},
                             out_parsing_errors=parsing_errors if parsing_errors is not None else {},
                             download_external_modules=download_external_modules,
                             external_modules_download_path=external_modules_download_path, excluded_paths=excluded_paths,
                             vars_files=vars_files, external_modules_content_cache=external_modules_content_cache)
        tf_definitions = self._clean_parser_types(tf_definitions)
        tf_definitions = self._serialize_definitions(tf_definitions)

        module, tf_definitions = self.parse_hcl_module_from_tf_definitions(tf_definitions, source_dir, source)
        return module, tf_definitions

    def parse_hcl_module_from_tf_definitions(
        self,
        tf_definitions: Dict[str, Dict[str, Any]],
        source_dir: str,
        source: str,
    ) -> Tuple[Module, Dict[str, Dict[str, Any]]]:
        module_dependency_map, tf_definitions, dep_index_mapping = self.get_module_dependency_map(tf_definitions)
        module = self.get_new_module(
            source_dir=source_dir,
            module_dependency_map=module_dependency_map,
            module_address_map=self.module_address_map,
            external_modules_source_map=self.external_modules_source_map,
            dep_index_mapping=dep_index_mapping,
        )
        self.add_tfvars(module, source)
        copy_of_tf_definitions = deepcopy(tf_definitions)
        for file_path, blocks in copy_of_tf_definitions.items():
            for block_type in blocks:
                try:
                    module.add_blocks(block_type, blocks[block_type], file_path, source)
                except Exception as e:
                    logging.error(f'Failed to add block {blocks[block_type]}. Error:')
                    logging.error(e, exc_info=True)
        return module, tf_definitions

    @staticmethod
    def _clean_parser_types(conf: dict) -> dict:
        sorted_keys = list(conf.keys())
        if len(conf.keys()) > 0 and all(isinstance(x, type(list(conf.keys())[0])) for x in conf.keys()):
            sorted_keys = sorted(filter(lambda x: x is not None, conf.keys()))
        # Create a new dict where the keys are sorted alphabetically
        sorted_conf = {key: conf[key] for key in sorted_keys}
        for attribute, values in sorted_conf.items():
            if attribute == 'alias':
                continue
            if isinstance(values, list):
                sorted_conf[attribute] = Parser._clean_parser_types_lst(values)
            elif isinstance(values, dict):
                sorted_conf[attribute] = Parser._clean_parser_types(conf[attribute])
            elif isinstance(values, str) and values in ('true', 'false'):
                sorted_conf[attribute] = True if values == 'true' else False
            elif isinstance(values, set):
                sorted_conf[attribute] = Parser._clean_parser_types_lst(list(values))
            elif isinstance(values, Tree):
                sorted_conf[attribute] = str(values)
        return sorted_conf

    @staticmethod
    def _clean_parser_types_lst(values: list) -> list:
        for i in range(len(values)):
            val = values[i]
            if isinstance(val, dict):
                values[i] = Parser._clean_parser_types(val)
            elif isinstance(val, list):
                values[i] = Parser._clean_parser_types_lst(val)
            elif isinstance(val, str):
                if val == 'true':
                    values[i] = True
                elif val == 'false':
                    values[i] = False
            elif isinstance(val, set):
                values[i] = Parser._clean_parser_types_lst(list(val))
        str_values_in_lst = [val for val in values if isinstance(val, str)]
        str_values_in_lst.sort()
        result_values = [val for val in values if not isinstance(val, str)]
        result_values.extend(str_values_in_lst)
        return result_values

    @staticmethod
    def _serialize_definitions(tf_definitions):
        return loads(dumps(tf_definitions, cls=CustomJSONEncoder))

    @staticmethod
    def get_next_vertices(evaluated_files: list, unevaluated_files: list) -> (list, list):
        """
        This function implements a lazy separation of levels for the evaluated files. It receives the evaluated
        files, and returns 2 lists:
        1. The next level of files - files from the unevaluated_files which have no unresolved dependency (either
            no dependency or all dependencies were evaluated).
        2. unevaluated - files which have yet to be evaluated, and still have pending dependencies

        Let's say we have this dependency tree:
        a -> b
        x -> b
        y -> c
        z -> b
        b -> c
        c -> d

        The first run will return [a, y, x, z] as the next level since all of them have no dependencies
        The second run with the evaluated being [a, y, x, z] will return [b] as the next level.
        Please mind that [c] has some resolved dependencies (from y), but has unresolved dependencies from [b].
        The third run will return [c], and the fourth will return [d].
        """
        next_level, unevaluated, do_not_eval_yet = [], [], []
        for key in unevaluated_files:
            found = False
            for eval_key in evaluated_files:
                if eval_key in key:
                    found = True
                    break
            if not found:
                do_not_eval_yet.append(key.split('[')[0])
                unevaluated.append(key)
            else:
                next_level.append(key)

        move_to_uneval = list(filter(lambda k: k.split('[')[0] in do_not_eval_yet, next_level))
        for k in move_to_uneval:
            next_level.remove(k)
            unevaluated.append(k)
        return next_level, unevaluated

    @staticmethod
    def get_module_dependency_map(tf_definitions):
        """
        :param tf_definitions, with paths in format 'dir/main.tf[module_dir/main.tf#0]'
        :return module_dependency_map: mapping between directories and the location of its module definition:
                {'dir': 'module_dir/main.tf'}
        :return tf_definitions: with paths in format 'dir/main.tf'
        """
        module_dependency_map = {}
        copy_of_tf_definitions = {}
        dep_index_mapping: Dict[Tuple[str, str], List[str]] = {}
        origin_keys = list(filter(lambda k: not k.endswith(']'), tf_definitions.keys()))
        unevaluated_keys = list(filter(lambda k: k.endswith(']'), tf_definitions.keys()))
        for file_path in origin_keys:
            dir_name = os.path.dirname(file_path)
            module_dependency_map[dir_name] = [[]]
            copy_of_tf_definitions[file_path] = deepcopy(tf_definitions[file_path])

        next_level, unevaluated_keys = Parser.get_next_vertices(origin_keys, unevaluated_keys)
        while next_level:
            for file_path in next_level:
                path, module_dependency, module_dependency_num = remove_module_dependency_in_path(file_path)
                dir_name = os.path.dirname(path)
                current_deps = deepcopy(module_dependency_map[os.path.dirname(module_dependency)])
                for dep in current_deps:
                    dep.append(module_dependency)
                if dir_name not in module_dependency_map:
                    module_dependency_map[dir_name] = current_deps
                elif current_deps not in module_dependency_map[dir_name]:
                    module_dependency_map[dir_name] += current_deps
                copy_of_tf_definitions[path] = deepcopy(tf_definitions[file_path])
                origin_keys.append(path)
                dep_index_mapping.setdefault((path, module_dependency), []).append(module_dependency_num)
            next_level, unevaluated_keys = Parser.get_next_vertices(origin_keys, unevaluated_keys)
        for key, dep_trails in module_dependency_map.items():
            hashes = set()
            deduped = []
            for trail in dep_trails:
                trail_hash = unify_dependency_path(trail)
                if trail_hash in hashes:
                    continue
                hashes.add(trail_hash)
                deduped.append(trail)
            module_dependency_map[key] = deduped
        return module_dependency_map, copy_of_tf_definitions, dep_index_mapping

    @staticmethod
    def get_new_module(
            source_dir: str,
            module_dependency_map: Dict[str, List[List[str]]],
            module_address_map: Dict[Tuple[str, str], str],
            external_modules_source_map: Dict[Tuple[str, str], str],
            dep_index_mapping: Dict[Tuple[str, str], List[str]],
    ) -> Module:
        return Module(
            source_dir=source_dir,
            module_dependency_map=module_dependency_map,
            module_address_map=module_address_map,
            external_modules_source_map=external_modules_source_map,
            dep_index_mapping=dep_index_mapping
        )

    def add_tfvars(self, module, source):
        if not self.external_variables_data:
            return
        for (var_name, default, path) in self.external_variables_data:
            if ".tfvars" in path:
                block = {var_name: {"default": default}}
                module.add_blocks(BlockType.TF_VARIABLE, block, path, source)


def _load_or_die_quietly(file: os.PathLike, parsing_errors: Dict,
                         clean_definitions: bool = True) -> Optional[Mapping]:
    """
Load JSON or HCL, depending on filename.
    :return: None if the file can't be loaded
    """

    file_path = os.fspath(file)
    file_name = os.path.basename(file_path)

    try:
        logging.debug(f"Parsing {file_path}")

        with open(file_path, "r") as f:
            if file_name.endswith(".json"):
                return json.load(f)
            else:
                raw_data = hcl2.load(f)
                non_malformed_definitions = validate_malformed_definitions(raw_data)
                if clean_definitions:
                    return clean_bad_definitions(non_malformed_definitions)
                else:
                    return non_malformed_definitions
    except Exception as e:
        logging.debug(f'failed while parsing file {file_path}', exc_info=e)
        parsing_errors[file_path] = e
        return None


def _is_valid_block(block):
    if not isinstance(block, dict):
        return True

    # if the block is empty, there's no need to process it further
    if len(block) == 0:
        return False

    entity_name, _ = next(iter(block.items()))
    if re.fullmatch(r'[^\W0-9][\w-]*', entity_name):
        return True
    return False


def validate_malformed_definitions(raw_data):
    raw_data_cleaned = raw_data
    for block_type, blocks in raw_data.items():
        raw_data_cleaned[block_type] = [block for block in blocks if _is_valid_block(block)]

    return raw_data_cleaned


def clean_bad_definitions(tf_definition_list):
    return {
        block_type: list(filter(lambda definition_list: block_type == 'locals' or
                                                        not isinstance(definition_list, dict)
                                                        or len(definition_list.keys()) == 1,
                                tf_definition_list[block_type]))
        for block_type in tf_definition_list.keys()
    }


def _to_native_value(value: str) -> Any:
    if value.startswith('"') or value.startswith("'"):
        return value[1:-1]
    else:
        return eval_string(value)


def _remove_module_dependency_in_path(path):
    """
    :param path: path that looks like "dir/main.tf[other_dir/x.tf#0]
    :return: only the outer path: dir/main.tf
    """
    resolved_module_pattern = re.compile(r'\[.+\#.+\]')
    if re.findall(resolved_module_pattern, path):
        path = re.sub(resolved_module_pattern, '', path)
    return path


def _safe_index(sequence_hopefully, index) -> Optional[Any]:
    try:
        return sequence_hopefully[index]
    except IndexError as e:
        logging.debug(f'Failed to parse index int ({index}) out of {sequence_hopefully}')
        logging.debug(e, stack_info=True)
        return None


def is_acceptable_module_param(value: Any) -> bool:
    """
    This function determines if a value should be passed to a module as a parameter. We don't want to pass
    unresolved var, local or module references because they can't be resolved from the module, so they need
    to be resolved prior to being passed down.
    """
    value_type = type(value)
    if value_type is dict:
        for k, v in value.items():
            if not is_acceptable_module_param(v) or not is_acceptable_module_param(k):
                return False
        return True
    if value_type is set or value_type is list:
        for v in value:
            if not is_acceptable_module_param(v):
                return False
        return True

    if value_type is not str:
        return True

    for vbm in find_var_blocks(value):
        if vbm.is_simple_var():
            return False
    return True
