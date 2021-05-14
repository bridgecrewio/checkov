import os
from checkov.common.config.checkov_config import CheckovConfig

from pathlib import Path


def compute_config(args):
    """
    Read config from the args and config file. Merge the objects based on precedence rules. Args override config file.
    If the arg is not defined, config file is used.
    """
    args_config = CheckovConfig.from_args(args)
    config_path = find_config_file(args)
    if config_path is not None:
        file_config = CheckovConfig.from_yaml(config_path)
        return combine_config(args_config, file_config)
    else:
        print(args_config)
        return args_config


def combine_config(primary, secondary):
    for attr, val in primary.__dict__.items():
        # If the primary values are default (None), check secondary.
        if val is None:
            if secondary.__getattribute__(attr) is not None:
                primary.__setattr__(attr, secondary.__getattribute__(attr))
                print('Modified {} from {} to {}'.format(attr, val, primary.__getattribute__(attr)))
        elif isinstance(val, bool):
            if is_bool_default(attr, val):
                # If primary has default values for boolean attributes, check secondary.
                if secondary.__getattribute__(attr) is not None:
                    primary.__setattr__(attr, secondary.__getattribute__(attr))
                    print('Modified {} from {} to {}'.format(attr, val, primary.__getattribute__(attr)))
        elif isinstance(val, (str, list)):
            if is_str_list_default(attr, val):
                # If primary has default values for string / list attributes, check secondary.
                if secondary.__getattribute__(attr) is not None:
                    primary.__setattr__(attr, secondary.__getattribute__(attr))
                    print('Modified {} from {} to {}'.format(attr, val, primary.__getattribute__(attr)))
    return primary


def is_bool_default(attr, val):
    # Return 'True' if the attribute has default value.
    if attr == 'evaluate_variables' and val:
        return True
    elif attr != 'evaluate_variables' and not val:
        return True
    return False


def is_str_list_default(attr, val):
    # Return 'True' if the attribute has default value.
    if attr == 'branch' and val == 'master':
        return True
    if attr == 'framework' and val == 'all':
        return True
    if attr == 'external_modules_download_path' and val == '.external_modules':
        return True
    return False


def find_config_file(args):
    """
    If the directory argument is not None, look for the .checkov/config.yaml file there.
    If the directory is not specified check if the config file is present in the current working directory.
    If the cwd does not have the config file, check if the config file is present in the home directory.
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

# merge config based on args and file.
