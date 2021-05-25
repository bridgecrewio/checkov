import os

from pathlib import Path


def config_file_paths(dir_path):
    return [os.path.join(dir_path, '.checkov.yaml'), os.path.join(dir_path, '.checkov.yml')]


def get_default_config_paths(argv):
    """
    Checkov looks for .checkov.yml or .checkov.yaml file in the directory (--directory) against which it is run.
    If that does not have the config file, the user's home directory is searched.
    :param argv: List of CLI args from sys.argv.
    :return: List of default config file paths.
    """
    home_paths = config_file_paths(Path.home())
    dir_paths = []
    for i, v in enumerate(argv):
        if v in ['-d', '--directory']:
            dir_paths += config_file_paths(argv[i + 1])
    return dir_paths + home_paths
