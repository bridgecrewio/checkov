import json
import logging
import os
from typing import Mapping, Optional, Dict, Any, List

import hcl2

from checkov.common.variables.context import EvaluationContext
from checkov.terraform.module_loading.registry import ModuleLoaderRegistry
from checkov.terraform.module_loading.registry import module_loader_registry as default_ml_registry


LOGGER = logging.getLogger(__name__)


def parse_directory(directory: str, out_definitions: Dict, out_definitions_context: Dict,
                    out_evaluations_context: Dict[str, EvaluationContext],
                    out_parsing_errors: Dict[str, Exception] = None, env_vars: Mapping[str, str] = None,
                    module_loader_registry: ModuleLoaderRegistry = default_ml_registry):
    """
Load and resolve configuration files starting in the given directory, merging the
resulting data into `tf_definitions`. This loads data according to the Terraform Code Organization
specification (https://www.terraform.io/docs/configuration/index.html#code-organization), starting
in the given directory and possibly moving out from there.

    :param directory:                  Directory in which .tf and .tfvars files will be loaded.
    :param out_definitions:            Dict into which the "simple" TF data with variables resolved is put.
    :param out_definitions_context:    Dict into which context about resource definitions is placed. The dict
                                       is a tree structure where keys are strings of the entity path
                                       ('resource', 'aws_s3_bucket', etc.) and the values are either another
                                       dict with the same semantics (branches) or EntityContext objects.
    :param out_evaluations_context:    Dict into which context about resource definitions is placed.
    :param out_parsing_errors:         Dict into which parsing errors, keyed on file path, are placed.
    :param env_vars:                   Optional values to use for resolving environment variables in TF code.
                                       If nothing is specified, Checkov's local environment will be used.
    :param module_loader_registry:     Registry used for resolving modules. This allows customization of how
                                       much resolution is performed (and easier testing) by using a manually
                                       constructed registry rather than the default.
    """

    if not out_parsing_errors:
        out_parsing_errors = {}
    if not env_vars:
        env_vars = dict(os.environ)

    _internal_dir_load(directory, out_definitions, out_definitions_context, out_evaluations_context,
                       out_parsing_errors, env_vars, None)

    # TODO!
    pass


def _internal_dir_load(directory: str, out_definitions: Dict, out_definitions_context: Dict,
                       out_evaluations_context: Dict[str, EvaluationContext],
                       out_parsing_errors: Dict[str, Exception],
                       env_vars: Mapping[str, str],
                       specified_vars: Optional[Mapping[str, str]]):
    """
See `parse_directory` docs.
    :param specified_vars:     Specifically defined variable values, overriding values from any other source.
    """

    # Stage 1: Look for applicable files in the directory:
    #          https://www.terraform.io/docs/configuration/index.html#code-organization
    #          Load the raw data for non-variable files, but perform no processing other than loading variable
    #          default values.
    #          Variable files are also flagged for later processing.
    var_values = {}
    hcl_tfvars: Optional[os.DirEntry] = None
    json_tfvars: Optional[os.DirEntry] = None
    auto_vars_files: Optional[List[os.DirEntry]] = None      # lazy creation
    for file in os.scandir(directory):
        # Ignore directories and hidden files
        if not file.is_file() or file.name.startswith("."):
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
                auto_vars_files.append(file.path)
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
        var_block = data.get("variable")
        if var_block:
            for var_name, var_definition in var_block[0].items():
                default_value = var_definition.get("default")
                if default_value is not None:
                    var_values[var_name] = default_value[0]

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
        var_values[key[7:]] = value
    if hcl_tfvars:                                                      # terraform.tfvars
        data = _load_or_die_quietly(hcl_tfvars, out_parsing_errors)
        var_values.update(data)
    if json_tfvars:                                                     # terraform.tfvars.json
        data = _load_or_die_quietly(json_tfvars, out_parsing_errors)
        var_values.update(data)
    if auto_vars_files:                                                 # *.auto.tfvars / *.auto.tfvars.json
        for var_file in sorted(auto_vars_files, key=os.DirEntry.name):
            data = _load_or_die_quietly(var_file, out_parsing_errors)
            var_values.update(data)
    if specified_vars:                                                  # specified
        var_values.update(specified_vars)


def _load_or_die_quietly(file: os.DirEntry, parsing_errors: Dict) -> Optional[Mapping]:
    """
Load JSON or HCL, depending on filename.
    :return: None if the file can't be loaded
    """
    try:
        with open(file, "r") as f:
            if file.name.endswith(".json"):
                return json.load(f)
            else:
                return hcl2.load(f)
    except Exception as e:
        LOGGER.debug(f'failed while parsing file {file}', exc_info=e)
        parsing_errors[file.path] = e
        return None
