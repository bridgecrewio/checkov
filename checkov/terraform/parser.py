from __future__ import annotations

import logging
import os
from typing import Optional, Dict, Mapping, Set, Tuple, Callable, Any, List

import deep_merge

from checkov.common.runners.base_runner import filter_ignored_paths, IGNORE_HIDDEN_DIRECTORY_ENV, strtobool
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR, RESOLVED_MODULE_ENTRY_NAME
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.common.util.type_forcers import force_list
from checkov.common.variables.context import EvaluationContext
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.module import Module
from checkov.terraform.module_loading.content import ModuleContent
from checkov.terraform.module_loading.module_finder import load_tf_modules
from checkov.terraform.module_loading.registry import module_loader_registry as default_ml_registry, \
    ModuleLoaderRegistry
from checkov.common.util.parser_utils import get_tf_definition_key_from_module_dependency, \
    TERRAFORM_NESTED_MODULE_PATH_ENDING, is_acceptable_module_param
from checkov.terraform.modules.module_utils import load_or_die_quietly, safe_index, \
    remove_module_dependency_from_path, get_module_dependency_map, get_module_dependency_map_support_nested_modules, \
    clean_parser_types, serialize_definitions


def _filter_ignored_paths(root: str, paths: list[str], excluded_paths: list[str] | None) -> None:
    filter_ignored_paths(root, paths, excluded_paths)
    for path in force_list(paths):
        if path == default_ml_registry.external_modules_folder_name:
            paths.remove(path)


class Parser:
    def __init__(self, module_class: type[Module] = Module) -> None:
        self.module_class = module_class
        self._parsed_directories: set[str] = set()
        self.external_modules_source_map: Dict[Tuple[str, str], str] = {}
        self.module_address_map: Dict[Tuple[str, str], str] = {}
        self.loaded_files_map = {}

        # This ensures that we don't try to double-load modules
        # Tuple is <file>, <module_index>, <name> (see _load_modules)
        self._loaded_modules: Set[Tuple[str, int, str]] = set()
        self.external_variables_data = []
        self.enable_nested_modules = strtobool(os.getenv('CHECKOV_ENABLE_NESTED_MODULES', 'True'))

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
        self.dirname_cache = {}

        if self.out_evaluations_context is None:
            self.out_evaluations_context = {}
        if self.out_parsing_errors is None:
            self.out_parsing_errors = {}
        if self.env_vars is None:
            self.env_vars = dict(os.environ)
        self.excluded_paths = excluded_paths
        self.visited_definition_keys = set()
        self.module_to_resolved = {}
        self.keys_to_remove = set()

    def _check_process_dir(self, directory: str) -> bool:
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
        if self.enable_nested_modules:
            self._update_resolved_modules()

    def parse_file(self, file: str, parsing_errors: Optional[Dict[str, Exception]] = None) -> Optional[Dict[str, Any]]:
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
            for sub_dir, d_names, _ in os.walk(self.directory):
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
                           vars_files: Optional[List[str]] = None,
                           root_dir: Optional[str] = None,
                           excluded_paths: Optional[List[str]] = None,
                           nested_modules_data=None):
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
        if excluded_paths or IGNORE_HIDDEN_DIRECTORY_ENV:
            filter_ignored_paths(directory, dir_contents, excluded_paths)

        tf_files_to_load = []
        for file in dir_contents:
            # Ignore directories and hidden files
            try:
                if not file.is_file():
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
            elif file.name.endswith(".tf") or file.name.endswith('.hcl'):  # TODO: add support for .tf.json
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
            data = load_or_die_quietly(hcl_tfvars, self.out_parsing_errors, clean_definitions=False)
            if data:
                var_value_and_file_map.update({k: (safe_index(v, 0), hcl_tfvars.path) for k, v in data.items()})
                self.external_variables_data.extend([(k, safe_index(v, 0), hcl_tfvars.path) for k, v in data.items()])
        if json_tfvars:  # terraform.tfvars.json
            data = load_or_die_quietly(json_tfvars, self.out_parsing_errors)
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
            # Add directory to self._parsed_directories to avoid loading it as sub dir
            if self.enable_nested_modules:
                dir_filter(directory)
            has_more_modules = self._load_modules(directory, module_loader_registry, dir_filter,
                                                  keys_referenced_as_modules, force_final_module_load,
                                                  nested_modules_data=nested_modules_data)

            # Stage 4b: Variable resolution round 2 - now with (possibly more) modules
            made_var_changes = False
            if not has_more_modules:
                break  # nothing more to do
            elif not made_var_changes:
                # If there are more modules to load but no variables were resolved, then to a final module
                # load, forcing things through without complete resolution.
                force_final_module_load = True

    def _load_files(self, files: list[os.DirEntry]):
        def _load_file(file: os.DirEntry):
            parsing_errors = {}
            result = load_or_die_quietly(file, parsing_errors)
            # the exceptions type can un-pickleable
            for path, e in parsing_errors.items():
                parsing_errors[path] = e

            return (file.path, result), parsing_errors

        files_to_data = []
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
                      keys_referenced_as_modules: Set[str], ignore_unresolved_params: bool = False,
                      nested_modules_data=None) -> bool:
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
            if self.get_dirname(file) != root_dir:
                continue
            # Don't process a file reference which has already been processed
            if file.endswith(TERRAFORM_NESTED_MODULE_PATH_ENDING):
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

                    if self.enable_nested_modules:
                        file_key = self.get_file_key_with_nested_data(file, nested_modules_data)
                        current_nested_data = (file_key, module_index, module_call_name)

                        resolved_loc_list = []
                        if current_nested_data in self.module_to_resolved:
                            resolved_loc_list = self.module_to_resolved[current_nested_data]
                        self.module_to_resolved[current_nested_data] = resolved_loc_list

                    module_address = (file, module_index, module_call_name)
                    if not self.enable_nested_modules:
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
                    elif source in ['./', '.']:
                        logging.debug(f"Skipping loading of {module_call_name} as source is the current dir")
                        continue

                    # Special handling for local sources to make sure we aren't double-parsing
                    if source.startswith("./") or source.startswith("../"):
                        source = os.path.normpath(
                            os.path.join(os.path.dirname(remove_module_dependency_from_path(file)), source))

                    version = module_call_data.get("version", "latest")
                    if version and isinstance(version, list):
                        version = version[0]
                    try:
                        content = module_loader_registry.load(root_dir, source, version)
                        if not content.loaded():
                            logging.info(f'Got no content for {source}:{version}')
                            continue

                        new_nested_modules_data = {'module_index': module_index, 'file': file,
                                                   'nested_modules_data': nested_modules_data}

                        self._internal_dir_load(directory=content.path(),
                                                module_loader_registry=module_loader_registry,
                                                dir_filter=dir_filter, specified_vars=specified_vars,
                                                keys_referenced_as_modules=keys_referenced_as_modules,
                                                nested_modules_data=new_nested_modules_data)

                        module_definitions = {
                            path: definition
                            for path, definition in self.out_definitions.items()
                            if self.get_dirname(path) == content.path()
                        }

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

                        if not self.enable_nested_modules:
                            resolved_loc_list = module_call_data.get(RESOLVED_MODULE_ENTRY_NAME)
                            if resolved_loc_list is None:
                                resolved_loc_list = []
                                module_call_data[RESOLVED_MODULE_ENTRY_NAME] = resolved_loc_list

                        # NOTE: Modules can load other modules, so only append referrer information where it
                        #       has not already been added.

                        keys = list(module_definitions.keys())
                        for key in keys:
                            if key.endswith(TERRAFORM_NESTED_MODULE_PATH_ENDING) or file.endswith(TERRAFORM_NESTED_MODULE_PATH_ENDING):
                                continue
                            keys_referenced_as_modules.add(key)
                            if self.enable_nested_modules:
                                new_key = self.get_new_nested_module_key(key, file, module_index, nested_modules_data)
                                if new_key in self.visited_definition_keys:
                                    del module_definitions[key]
                                    del self.out_definitions[key]
                                    continue
                            else:
                                new_key = get_tf_definition_key_from_module_dependency(key, file, module_index)
                            module_definitions[new_key] = module_definitions[key]
                            del module_definitions[key]
                            del self.out_definitions[key]
                            self.keys_to_remove.add(key)

                            if self.enable_nested_modules:
                                self.visited_definition_keys.add(new_key)
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
        parsing_errors: dict[str, Exception] | None = None,
        excluded_paths: list[str] | None = None,
        vars_files: list[str] | None = None,
        external_modules_content_cache: dict[str, ModuleContent] | None = None,
        create_graph: bool = True,
    ) -> tuple[Module | None, dict[str, dict[str, Any]]]:
        tf_definitions: dict[str, dict[str, Any]] = {}
        self.parse_directory(directory=source_dir, out_definitions=tf_definitions, out_evaluations_context={},
                             out_parsing_errors=parsing_errors if parsing_errors is not None else {},
                             download_external_modules=download_external_modules,
                             external_modules_download_path=external_modules_download_path, excluded_paths=excluded_paths,
                             vars_files=vars_files, external_modules_content_cache=external_modules_content_cache)
        tf_definitions = clean_parser_types(tf_definitions)
        tf_definitions = serialize_definitions(tf_definitions)

        module = None
        if create_graph:
            module, tf_definitions = self.parse_hcl_module_from_tf_definitions(tf_definitions, source_dir, source)

        return module, tf_definitions

    def _remove_unused_path_recursive(self, path):
        self.out_definitions.pop(path, None)
        for key in list(self.module_to_resolved.keys()):
            file_key, module_index, module_name = key
            if path == file_key:
                for resolved_path in self.module_to_resolved[key]:
                    self._remove_unused_path_recursive(resolved_path)
                self.module_to_resolved.pop(key, None)

    def _update_resolved_modules(self):
        for key in list(self.module_to_resolved.keys()):
            file_key, module_index, module_name = key
            if file_key in self.keys_to_remove:
                for path in self.module_to_resolved[key]:
                    self._remove_unused_path_recursive(path)
                self.module_to_resolved.pop(key, None)

        for key, resolved_list in self.module_to_resolved.items():
            file_key, module_index, module_name = key
            if file_key not in self.out_definitions:
                continue
            self.out_definitions[file_key]['module'][module_index][module_name][RESOLVED_MODULE_ENTRY_NAME] = resolved_list

    def parse_hcl_module_from_tf_definitions(
        self,
        tf_definitions: Dict[str, Dict[str, Any]],
        source_dir: str,
        source: str,
    ) -> Tuple[Module, Dict[str, Dict[str, Any]]]:
        if self.enable_nested_modules:
            module_dependency_map, tf_definitions, dep_index_mapping = get_module_dependency_map_support_nested_modules(tf_definitions)
        else:
            module_dependency_map, tf_definitions, dep_index_mapping = get_module_dependency_map(tf_definitions)
        module = self.get_new_module(
            source_dir=source_dir,
            module_dependency_map=module_dependency_map,
            module_address_map=self.module_address_map,
            external_modules_source_map=self.external_modules_source_map,
            dep_index_mapping=dep_index_mapping,
        )
        self.add_tfvars(module, source)
        copy_of_tf_definitions = pickle_deepcopy(tf_definitions)
        for file_path, blocks in copy_of_tf_definitions.items():
            for block_type in blocks:
                try:
                    module.add_blocks(block_type, blocks[block_type], file_path, source)
                except Exception as e:
                    logging.warning(f'Failed to add block {blocks[block_type]}. Error:')
                    logging.warning(e, exc_info=False)
        return module, tf_definitions

    def get_file_key_with_nested_data(self, file, nested_data):
        if not nested_data:
            return file
        nested_str = self.get_file_key_with_nested_data(nested_data.get("file"), nested_data.get('nested_modules_data'))
        nested_module_index = nested_data.get('module_index')
        return get_tf_definition_key_from_module_dependency(file, nested_str, nested_module_index)

    def get_new_nested_module_key(self, key, file, module_index, nested_data) -> str:
        if not nested_data:
            return get_tf_definition_key_from_module_dependency(key, file, module_index)
        visited_key_to_add = get_tf_definition_key_from_module_dependency(key, file, module_index)
        self.visited_definition_keys.add(visited_key_to_add)
        nested_key = self.get_new_nested_module_key('', nested_data.get('file'),
                                                    nested_data.get('module_index'),
                                                    nested_data.get('nested_modules_data'))
        return get_tf_definition_key_from_module_dependency(key, f"{file}{nested_key}", module_index)

    def add_tfvars(self, module: Module, source: str) -> None:
        if not self.external_variables_data:
            return
        for (var_name, default, path) in self.external_variables_data:
            if ".tfvars" in path:
                block = {var_name: {"default": default}}
                module.add_blocks(BlockType.TF_VARIABLE, block, path, source)

    def get_dirname(self, path: str) -> str:
        dirname_path = self.dirname_cache.get(path)
        if not dirname_path:
            dirname_path = os.path.dirname(path)
            self.dirname_cache[path] = dirname_path
        return dirname_path

    @staticmethod
    def get_new_module(
            source_dir: str,
            module_dependency_map: dict[str, list[list[str]]],
            module_address_map: dict[tuple[str, str], str],
            external_modules_source_map: dict[tuple[str, str], str],
            dep_index_mapping: dict[tuple[str, str], list[str]],
    ) -> Module:
        return Module(
            source_dir=source_dir,
            module_dependency_map=module_dependency_map,
            module_address_map=module_address_map,
            external_modules_source_map=external_modules_source_map,
            dep_index_mapping=dep_index_mapping
        )
