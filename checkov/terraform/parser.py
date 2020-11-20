import json
import logging
import os
import re
from pathlib import Path
from typing import Mapping, Optional, Dict, Any, List, Callable, Tuple

import deep_merge
import hcl2
import jmespath

from checkov.common.runners.base_runner import filter_ignored_directories
from checkov.common.variables.context import EvaluationContext, VarReference
from checkov.terraform.module_loading.registry import ModuleLoaderRegistry
from checkov.terraform.module_loading.registry import module_loader_registry as default_ml_registry


LOGGER = logging.getLogger(__name__)

_VAR_PATTERN = re.compile(r'\${([^{}]+?)}')
_SIMPLE_TYPES = frozenset(["string", "number", "bool"])

_RESOURCE_REF_PATTERN = re.compile(r'[\d\w]+(\.[\d\w]+)+')


class Parser:
    def __init__(self):
        self._parsed_directories = set()

    def _check_process_dir(self, directory):
        if directory not in self._parsed_directories:
            self._parsed_directories.add(directory)
            return True
        else:
            return False

    def parse_directory(self, directory: str, out_definitions: Optional[Dict],
                        out_evaluations_context: Dict[str, Dict[str, EvaluationContext]] = None,
                        out_parsing_errors: Dict[str, Exception] = None,
                        env_vars: Mapping[str, str] = None):

        self._parsed_directories.clear()
        _parse_directory(directory, True, out_definitions, out_evaluations_context,
                         out_parsing_errors, env_vars,
                         dir_filter=lambda d: self._check_process_dir(d))

    @staticmethod
    def parse_file(file: str, parsing_errors: Dict[str, Exception] = None) -> Optional[Dict]:
        if not file.endswith(".tf") and not file.endswith(".tf.json"):
            return None
        return _load_or_die_quietly(Path(file), parsing_errors)


def _parse_directory(directory: str, include_sub_dirs: bool, out_definitions: Dict,
                     out_evaluations_context: Optional[Dict[str, Dict[str, EvaluationContext]]] = None,
                     out_parsing_errors: Optional[Dict[str, Exception]] = None,
                     env_vars: Optional[Mapping[str, str]] = None,
                     module_loader_registry: ModuleLoaderRegistry = default_ml_registry,
                     dir_filter: Callable[[str], bool] = lambda _: True):
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

    :param directory:                  Directory in which .tf and .tfvars files will be loaded.
    :param include_sub_dirs:           If true, subdirectories will be walked.
    :param out_definitions:            Dict into which the "simple" TF data with variables resolved is put.
    :param out_evaluations_context:    Dict into which context about resource definitions is placed. Outer
                                       key is the file, inner key is a variable name.
    :param out_parsing_errors:         Dict into which parsing errors, keyed on file path, are placed.
    :param env_vars:                   Optional values to use for resolving environment variables in TF code.
                                       If nothing is specified, Checkov's local environment will be used.
    :param module_loader_registry:     Registry used for resolving modules. This allows customization of how
                                       much resolution is performed (and easier testing) by using a manually
                                       constructed registry rather than the default.
    :param dir_filter:                 Determines whether or not a directory should be processed. Returning
                                       True will allow processing. The argument will be the absolute path of
                                       the directory.
    """

    if out_evaluations_context is None:
        out_evaluations_context = {}
    if out_parsing_errors is None:
        out_parsing_errors = {}
    if env_vars is None:
        env_vars = dict(os.environ)

    if include_sub_dirs:
        for sub_dir, d_names, f_names in os.walk(directory):
            filter_ignored_directories(d_names)
            if dir_filter(os.path.abspath(sub_dir)):
                _internal_dir_load(sub_dir, out_definitions,
                                   out_evaluations_context, out_parsing_errors, env_vars, None,
                                   module_loader_registry, dir_filter)
    else:
        _internal_dir_load(directory, out_definitions, out_evaluations_context,
                           out_parsing_errors, env_vars, None, module_loader_registry, dir_filter)


def _internal_dir_load(directory: str, out_definitions: Dict,
                       out_evaluations_context: Dict[str, Dict[str, EvaluationContext]],
                       out_parsing_errors: Dict[str, Exception],
                       env_vars: Mapping[str, str],
                       specified_vars: Optional[Mapping[str, str]],
                       module_loader_registry: ModuleLoaderRegistry,
                       dir_filter: Callable[[str], bool],
                       module_load_context: Optional[str] = None):
    """
See `parse_directory` docs.
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
    auto_vars_files: Optional[List[os.DirEntry]] = None      # lazy creation
    for file in os.scandir(directory):
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
            continue
        elif file.name == "terraform.tfvars":
            hcl_tfvars = file
            continue
        elif file.name.endswith(".auto.tfvars.json") or file.name.endswith(".auto.tfvars"):
            if auto_vars_files is None:
                auto_vars_files = [file]
            else:
                auto_vars_files.append(file)
            continue

        # Resource files
        if file.name.endswith(".tf.json") or file.name.endswith(".tf"):
            data = _load_or_die_quietly(file, out_parsing_errors)
        else:
            continue

        if not data:        # failed loads or empty files
            continue

        out_definitions[file.path] = data

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
                        var_value_and_file_map[var_name] = default_value[0], file.path

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
    for key, value in env_vars.items():                                 # env vars
        if not key.startswith("TF_VAR_"):
            continue
        var_value_and_file_map[key[7:]] = value, f"env:{key}"
    if hcl_tfvars:                                                      # terraform.tfvars
        data = _load_or_die_quietly(hcl_tfvars, out_parsing_errors)
        if data:
            var_value_and_file_map.update({k: (v, hcl_tfvars.path) for k, v in data.items()})
    if json_tfvars:                                                     # terraform.tfvars.json
        data = _load_or_die_quietly(json_tfvars, out_parsing_errors)
        if data:
            var_value_and_file_map.update({k: (v, json_tfvars.path) for k, v in data.items()})
    if auto_vars_files:                                                 # *.auto.tfvars / *.auto.tfvars.json
        for var_file in sorted(auto_vars_files, key=lambda e: e.name):
            data = _load_or_die_quietly(var_file, out_parsing_errors)
            if data:
                var_value_and_file_map.update({k: (v, var_file.path) for k, v in data.items()})
    if specified_vars:                                                  # specified
        var_value_and_file_map.update({k: (v, "manual specification") for k, v in specified_vars.items()})

    # IMPLEMENTATION NOTE: When resolving `module.` references, access to the entire data map is needed. It
    #                      may be a little overboard, but I don't want to just pass the entire data map down
    #                      because it break encapsulations and I don't want to cause confusion about what data
    #                      set it being processed. To avoid this, here's a Callable that will get the data
    #                      map for a particular module reference. (Might be OCD, but...)
    module_data_retrieval = lambda module_ref: out_definitions.get(module_ref)

    # Stage 3: Variable resolution round 1 - no modules yet
    _process_vars_and_locals(out_definitions, out_evaluations_context, directory, var_value_and_file_map,
                             module_data_retrieval)

    # Stage 4: Load modules
    _load_modules(out_definitions, out_evaluations_context, out_parsing_errors,
                  env_vars, directory, module_loader_registry, dir_filter, module_load_context)

    # Stage 5: Variable resolution round 2 - now with modules
    _process_vars_and_locals(out_definitions, out_evaluations_context, directory, var_value_and_file_map,
                             module_data_retrieval)


def _process_vars_and_locals(out_definitions: Dict,
                             evaluations_context: Dict[str, Dict[str, EvaluationContext]],
                             directory: str,
                             var_value_and_file_map: Dict[str, Tuple[Any, str]],
                             module_data_retrieval: Callable[[str], Dict[str, Any]]):
    locals_values = {}
    for file_data in out_definitions.values():
        file_locals = file_data.get("locals")
        if not file_locals:
            continue
        for k, v in file_locals[0].items():
            locals_values[k] = v[0]

    # Processing is done in a loop to deal with chained references and the like.
    # Loop while the data is being changed, stop when no more changes are happening.
    # To ensure there's not some kind of oscillation, a cap of 25 passes is in place.
    # More than a couple loops isn't normally expected.
    # NOTE: If this approach proves to be a performance liability, a DAG will be needed.
    loop_count = 0
    for i in range(0, 25):
        loop_count += 1

        made_change = False
        # Put out file layer here so the context works inside the loop
        for file, file_data in out_definitions.items():
            eval_context_dict = evaluations_context.get(file)
            if eval_context_dict is None:
                eval_context_dict = {}
                evaluations_context[file] = eval_context_dict
                # out_evaluations_context[os.path.join(directory, file)] = {
                #     var_name: EvaluationContext(os.path.relpath(file.path, directory))
                # }

            if _process_vars_and_locals_loop(file_data,
                                             eval_context_dict,
                                             os.path.relpath(file, directory),
                                             var_value_and_file_map, locals_values,
                                             file_data.get("resource"),
                                             file_data.get("module"),
                                             module_data_retrieval,
                                             directory):
                made_change = True

            if len(eval_context_dict) == 0:
                del evaluations_context[file]
        if not made_change:
            break

    LOGGER.debug("Processing variables took %d loop iterations", loop_count)


def _process_vars_and_locals_loop(out_definitions: Dict,
                                  eval_map_by_var_name: Dict[str, EvaluationContext], relative_file_path: str,
                                  var_value_and_file_map: Dict[str, Tuple[Any, str]],
                                  locals_values: Dict[str, Any],
                                  resource_list: Optional[List[Dict[str, Any]]],
                                  module_list: Optional[List[Dict[str, Any]]],
                                  module_data_retrieval: Callable[[str], Dict[str, Any]],
                                  root_directory: str,
                                  outer_context: str = "") -> bool:

    # Generic loop for handling a source of key/value tuples (e.g., enumerate() or <dict>.items())
    def process_items_helper(key_value_iterator, data_map, context, allow_str_bool_translation: bool):
        made_change = False
        for key, value in list(key_value_iterator()):       # Copy to list to allow deletion
            new_context = f"{context}/{key}" if len(context) != 0 else key

            if isinstance(value, str):
                altered_value = value

                had_pattern_match = False
                for match in _VAR_PATTERN.finditer(value):
                    var_base = match[1]

                    # Expressions such as (from variable definition):
                    #    type = string
                    # are turned into:
                    #    "type = ${string}"
                    if var_base in _SIMPLE_TYPES and match[0] == value:
                        altered_value = var_base
                        had_pattern_match = True
                    else:
                        replaced = _handle_single_var_pattern(var_base, var_value_and_file_map, locals_values,
                                                              resource_list,
                                                              module_list, module_data_retrieval,
                                                              eval_map_by_var_name,
                                                              new_context, value, root_directory)
                        if replaced != var_base:
                            if match[0] == value:
                                altered_value = replaced
                            else:
                                altered_value = altered_value.replace(match[0], str(replaced))
                            had_pattern_match = True

                if not had_pattern_match:
                    # tomap is annoying because the curly braces in the string break the regex. Rather than
                    # coming up with something that's significantly more complex, we'll special case this
                    # check. Only do this when there wasn't a pattern match to make sure there are no
                    # variables lingering in the map value.
                    # https://www.terraform.io/docs/configuration/functions/tomap.html
                    if value.startswith("${tomap(") and value.endswith(")}"):
                        trimmed = value[8:-2]
                        trimmed = trimmed.replace(":", "=")     # converted to colons by parser #shrug
                        altered_value = _eval_string(trimmed)

                        if not isinstance(altered_value, dict):
                            continue

                        # If there is a string and anything else, convert to string
                        had_string = False
                        had_something_else = False
                        for k, v in altered_value.items():
                            if v == "${True}":
                                altered_value[k] = True
                                v = True
                            elif v == "${False}":
                                altered_value[k] = False
                                v = False

                            if isinstance(v, str):
                                had_string = True
                                if had_something_else:
                                    break
                            else:
                                had_something_else = True
                                if had_string:
                                    break
                        if had_string and had_something_else:
                            altered_value = {k: _tostring(v) for k, v in altered_value.items()}
                    # Same as above, regex can blow this up
                    # (see parser scenario: tostring_function, INNER_CURLY
                    elif value.startswith("${tostring(\"") and value.endswith("\")}"):
                        altered_value = value[12:-3]

                    # Support HCL 0.11 optional boolean syntax - evaluate "true" to true and "false" to false
                    #
                    # `allow_str_bool_translation` exists because we want to prevent conversion in a dict
                    # which is a direct value. See the "MIXED_BOOL" variable in the "tomap_function" parser
                    # scenario for a situation which worked incorrectly without this.
                    # NOTE: This is probably not a big deal to be removed if this causes problems in other
                    #       places. The MIXED_BOOL test case is technically correct with the TF spec, but
                    #       isn't essential operation for Checkov.
                    elif allow_str_bool_translation and value == "true":
                        altered_value = True
                    elif allow_str_bool_translation and value == "false":
                        altered_value = False

                if value != altered_value:
                    LOGGER.debug(f"Resolve: %s --> %s", value, altered_value)
                    data_map[key] = altered_value
                    made_change = True
            elif isinstance(value, dict):
                if _process_vars_and_locals_loop(value, eval_map_by_var_name, relative_file_path,
                                                 var_value_and_file_map,
                                                 locals_values, resource_list,
                                                 module_list, module_data_retrieval, root_directory,
                                                 new_context):
                    made_change = True

            elif isinstance(value, list):
                if process_items_helper(lambda: enumerate(value), value, new_context, True):
                    made_change = True
                # Some special cases that should be pruned from datasets
                if value == [None] or value == [{}] or len(value) == 0:
                    del data_map[key]
        return made_change

    return process_items_helper(out_definitions.items, out_definitions, outer_context, False)


def _load_modules(out_definitions: Dict,
                  out_evaluations_context: Dict[str, Dict[str, EvaluationContext]],
                  out_parsing_errors: Dict[str, Exception],
                  env_vars: Mapping[str, str],
                  directory: str, module_loader_registry: ModuleLoaderRegistry,
                  dir_filter: Callable[[str], bool],
                  module_load_context: Optional[str]):

    all_module_definitions = {}
    all_module_evaluations_context = {}
    for file, file_data in out_definitions.items():
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

                source = module_call_data.get("source")
                if not source or not isinstance(source, list):
                    continue
                source = source[0]

                # Special handling for local sources to make sure we aren't double-parsing
                if source.startswith("./") or source.startswith("../"):
                    module_path = os.path.normpath(os.path.join(directory, source))
                    if not dir_filter(os.path.abspath(module_path)):
                        continue

                version = module_call_data.get("version")
                if version and isinstance(version, list):
                    version = version[0]

                try:
                    with module_loader_registry.load(os.path.dirname(file), source, version) as content:
                        if not content.loaded():
                            continue

                        # Variables being passed to module, "source" and "version" are reserved
                        specified_vars = {k: v[0] for k, v in module_call_data.items()
                                          if k != "source" and k != "version"}

                        module_definitions = {}
                        module_evaluations_context = {}
                        _internal_dir_load(content.path(), module_definitions,
                                           module_evaluations_context, out_parsing_errors, env_vars,
                                           specified_vars, module_loader_registry, dir_filter,
                                           module_load_context)

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

                        resolved_loc_list = module_call_data.get("__resolved__")
                        if resolved_loc_list is None:
                            resolved_loc_list = []
                            module_call_data["__resolved__"] = resolved_loc_list

                        # NOTE: Modules can load other modules, so only append referrer information where it
                        #       has not already been added.
                        keys = list(module_definitions.keys())
                        for key in keys:
                            if key.endswith("]"):
                                continue
                            new_key = f"{key}[{file}#{module_index}]"
                            module_definitions[new_key] = \
                                module_definitions[key]
                            del module_definitions[key]

                            resolved_loc_list.append(new_key)

                        deep_merge.merge(all_module_definitions, module_definitions)
                        # TODO: Not sure what to do with variable evaluations
                        deep_merge.merge(all_module_evaluations_context, module_evaluations_context)
                except Exception as e:
                    logging.warning("Unable to load module (source=\"%s\" version=\"%s\"): %s",
                                    source, version, e)
                    pass

    if all_module_definitions:
        deep_merge.merge(out_definitions, all_module_definitions)
        deep_merge.merge(out_evaluations_context, all_module_evaluations_context)


def _handle_single_var_pattern(orig_variable: str, var_value_and_file_map: Dict[str, Tuple[Any, str]],
                               locals_values: Dict[str, Any],
                               resource_list: Optional[List[Dict[str, Any]]],
                               module_list: Optional[List[Dict[str, Any]]],
                               module_data_retrieval: Callable[[str], Dict[str, Any]],
                               eval_map_by_var_name: Dict[str, EvaluationContext],
                               context, orig_variable_full, root_directory: str) -> Any:
    if "${" in orig_variable:
        return orig_variable

    elif orig_variable.startswith("module."):
        if not module_list:
            return orig_variable

        # Reference to module outputs, example: 'module.bucket.bucket_name'
        ref_tokens = orig_variable.split(".")
        if len(ref_tokens) != 3:
            return orig_variable        # fail safe, can the length ever be something other than 3?

        try:
            ref_list = jmespath.search(f"[].{ref_tokens[1]}.__resolved__[]", module_list)
            #                                ^^^^^^^^^^^^^ module name

            if not ref_list or not isinstance(ref_list, list):
                return orig_variable

            for ref in ref_list:
                module_data = module_data_retrieval(ref)
                if not module_data:
                    continue

                result = _handle_indexing(ref_tokens[2],
                                          lambda r: jmespath.search(f"output[].{ref_tokens[2]}.value[] | [0]",
                                                                    module_data))
                if result:
                    logging.debug("Resolved module ref:  %s --> %s", orig_variable, result)
                    return result
        except ValueError:
            pass
        return orig_variable

    elif orig_variable == "True":
        return True
    elif orig_variable == "False":
        return False

    elif orig_variable.startswith("var."):
        var_name = orig_variable[4:]
        var_value_and_file = _handle_indexing(var_name, lambda r: var_value_and_file_map.get(r))
        if var_value_and_file is not None:
            var_value, var_file = var_value_and_file
            eval_context = eval_map_by_var_name.get(var_name)
            if eval_context is None:
                eval_map_by_var_name[var_name] = EvaluationContext(os.path.relpath(var_file, root_directory),
                                                                   var_value,
                                                                   [VarReference(var_name,
                                                                                 orig_variable_full,
                                                                                 context)])
            else:
                eval_context.definitions.append(VarReference(var_name, orig_variable_full, context))
            return var_value
    elif orig_variable.startswith("local."):
        var_value = _handle_indexing(orig_variable[6:], lambda r: locals_values.get(r))
        if var_value is not None:
            return var_value
    elif orig_variable.startswith("to") and orig_variable.endswith(")"):
        # https://www.terraform.io/docs/configuration/functions/tobool.html
        if orig_variable.startswith("tobool("):
            bool_variable = orig_variable[7:-1].lower()
            if bool_variable == "true" or bool_variable == '"true"':
                return True
            elif bool_variable == "false" or bool_variable == '"false"':
                return False
            else:
                return orig_variable
        # https://www.terraform.io/docs/configuration/functions/tolist.html
        elif orig_variable.startswith("tolist("):
            altered_value = _eval_string(orig_variable[7:-1])
            return altered_value if isinstance(altered_value, list) else list(altered_value)
        # NOTE: tomap as handled outside this loop (see below)
        # https://www.terraform.io/docs/configuration/functions/tonumber.html
        elif orig_variable.startswith("tonumber("):
            num_variable = orig_variable[9:-1]
            if num_variable.startswith('"') and num_variable.endswith('"'):
                num_variable = num_variable[1:-1]
            try:
                if "." in num_variable:
                    return float(num_variable)
                else:
                    return int(num_variable)
            except ValueError:
                return orig_variable
        # https://www.terraform.io/docs/configuration/functions/toset.html
        elif orig_variable.startswith("toset("):
            return set(_eval_string(orig_variable[6:-1]))
        # https://www.terraform.io/docs/configuration/functions/tostring.html
        elif orig_variable.startswith("tostring("):
            altered_value = orig_variable[9:-1]
            # Indicates a safe string, all good
            if altered_value.startswith('"') and altered_value.endswith('"'):
                return altered_value[1:-1]
            # Otherwise, need to check for valid types (number or bool)
            elif altered_value == "true":
                return True
            elif altered_value == "false":
                return False
            else:
                try:
                    if "." in altered_value:
                        return str(float(altered_value))
                    else:
                        return str(int(altered_value))
                except ValueError:
                    return orig_variable     # no change
    # TODO - format() support, still in progress
    # elif orig_variable.startswith("format(") and orig_variable.endswith(")"):
    #     format_tokens = orig_variable[7:-1].split(",")
    #     return format_tokens[0].format([_to_native_value(t) for t in format_tokens[1:]])

    elif _RESOURCE_REF_PATTERN.match(orig_variable):
        # Reference to resources, example: 'aws_s3_bucket.example.bucket'
        # TODO: handle index into map/list
        try:
            result = jmespath.search(f"[].{orig_variable}[] | [0]", resource_list)
        except ValueError:
            pass
        else:
            if result is not None:
                return result

    return orig_variable        # fall back to no change


def _handle_indexing(reference: str, data_source: Callable[[str], Optional[Any]]) -> Optional[Any]:
    if reference.endswith("]") and "[" in reference:
        base_ref = reference[:reference.rindex("[")]
        value = data_source(base_ref)
        if isinstance(value, dict):
            return value.get(reference[reference.rindex("[")+1: -1])
        elif isinstance(value, list):
            return value[int(reference[reference.rindex("[")+1: -1])]
    else:
        return data_source(reference)


def _load_or_die_quietly(file: os.PathLike, parsing_errors: Dict) -> Optional[Mapping]:
    """
Load JSON or HCL, depending on filename.
    :return: None if the file can't be loaded
    """

    file_path = os.fspath(file)
    file_name = os.path.basename(file_path)

    try:
        with open(file, "r") as f:
            if file_name.endswith(".json"):
                return _clean_bad_definitions(json.load(f))
            else:
                return _clean_bad_definitions(hcl2.load(f))
    except Exception as e:
        LOGGER.debug(f'failed while parsing file {file}', exc_info=e)
        parsing_errors[file_path] = e
        return None


def _clean_bad_definitions(tf_definition_list):
    return {
        block_type: list(filter(lambda definition_list: block_type == 'locals' or len(definition_list.keys()) == 1, tf_definition_list[block_type]))
        for block_type in tf_definition_list.keys()
    }


def _eval_string(value: str) -> Any:
    value_string = value.replace("'", '"')
    parsed = hcl2.loads(f'eval = {value_string}\n')      # NOTE: newline is needed
    return parsed["eval"][0]


def _to_native_value(value: str) -> Any:
    if value.startswith('"') or value.startswith("'"):
        return value[1:-1]
    else:
        return _eval_string(value)


def _tostring(value: Any) -> str:
    if value is True:
        return "true"
    elif value is False:
        return "false"
    return str(value)
