import os

from pathlib import Path


def config_file_paths(dir_path):
    return [os.path.join(dir_path, '.checkov.yaml'), os.path.join(dir_path, '.checkov.yml')]


def get_default_config_paths(argv):
    """
    Checkov looks for .checkov.yml or .checkov.yaml file in the directory (--directory) against which it is run.
    If that does not have the config file, the current working directory is checked followed by checking the user's
    home directory is searched.
    :param argv: List of CLI args from sys.argv.
    :return: List of default config file paths.
    """
    home_paths = config_file_paths(Path.home())
    cwd_path = config_file_paths(Path.cwd())
    dir_paths = []
    for i, v in enumerate(argv):
        if v in ['-d', '--directory']:
            dir_paths += config_file_paths(argv[i + 1])
    return dir_paths + cwd_path + home_paths


def should_scan_hcl_files():
    from checkov.common.models.consts import SCAN_HCL_FLAG  # prevent circular import
    return os.getenv(SCAN_HCL_FLAG, default="false").lower() == "true"
