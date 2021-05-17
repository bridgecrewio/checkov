import os
from checkov.common.config.checkov_config import CheckovConfig

from pathlib import Path


def compute_config(args, parser, argv):
    """
    If config file is not found, use the cli arguments to create CheckovConfig object.
    If config file is found, merge the config file with the CLi arguments based on precedence rules.

    :param args: Namespace object based on sys.argv[1:]
    :param parser: Instance of ArgumentParser.
    :param argv: List of user provided CLI args.
    :return: CheckovConfig object.
    """
    args_config = CheckovConfig.from_args(args)
    config_path = find_config_file(args)
    if config_path:
        file_config = CheckovConfig.from_yaml(config_path)
        return combine_config(args_config, file_config, argv, get_option_string_to_variable_mapping(parser))
    else:
        return args_config


def combine_config(args_config, file_config, argv, option_string_to_variable_mapping):
    """
    Precedence for this is as follows;
    - Values for CLI arguments (default or non-default), will take precedence over config file values.
    - If CLI argument is not passed in, the config file value will be used.

    :param args_config: CheckovConfig object from cli arguments.
    :param file_config: CheckovConfig object from configuration file.
    :param argv: List of CLI arguments passed in by user.
    :param option_string_to_variable_mapping: Mapping of the option strings to the argument variables.
    :return: Combined CheckovConfig object.
    """
    # It is necessary to determine which arguments were supplied in the cli since that value will override the config
    # file. Therefore we need to check sys.argv for what the user typed.
    if option_string_to_variable_mapping:
        for attr, val in option_string_to_variable_mapping.items():
            if attr in argv:
                file_config.__setattr__(val, args_config.__getattribute__(val))
    return file_config


def get_option_string_to_variable_mapping(parser):
    # The ArgumentParser library does not have a method to get option string names from the parser object.
    # However, this can be done by looking at the '_option_string_actions' field in the parser object.
    # Example: {'-d': 'directory', '--directory': 'directory', '-f': 'file', '--file': 'file'}
    option_string_to_variable_mapping = {}
    for key in vars(parser)['_option_string_actions'].keys():
        option_string_to_variable_mapping[key] = vars(parser)['_option_string_actions'][key].dest
    return option_string_to_variable_mapping


def find_config_file(args):
    """
    If the directory argument is not None, look for the .checkov/config.yaml file there.
    If the directory is not specified check if the config file is present in the current working directory.
    If the cwd does not have the config file, check if the config file is present in the home directory.
    Check for cwd always - have it lower priority than -d
    If there's a -d, but no config file there, then check cwd
    TODO: Take in config file path via cli arg.
    """
    if args.directory:
        for root_folder in args.directory:
            config_file = config_file_path(root_folder)
        if os.path.exists(config_file):
            return config_file
    else:
        current_dir_config_path = config_file_path(os.getcwd())
        home_dir_config_path = config_file_path(Path.home())
        if os.path.exists(current_dir_config_path):
            return current_dir_config_path
        elif os.path.exists(home_dir_config_path):
            return home_dir_config_path
        else:
            return None


def config_file_path(dir_path):
    checkov_dir = "{}/.checkov".format(dir_path)
    return "{}/config.yaml".format(checkov_dir)
