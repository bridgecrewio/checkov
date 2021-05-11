import os
import logging
import yaml

from pathlib import Path


class ConfigParser:

    def __init__(self, args):
        self.args = args
        self.logger = logging.getLogger(__name__)

    def compute_args(self, config_file):
        # TODO:
        #   bc_api_key --> Needs to be ignored.
        #   branch='master' --> Defaults to 'master'
        #   ca_certificate
        #   check
        #   compact
        #   directory --> Done.
        #   docker_image
        #   dockerfile_path
        #   download_external_modules
        #   evaluate_variables=True --> Defaults to True.
        #   external_checks_dir
        #   external_checks_git
        #   external_modules_download_path='.external_modules' --> Defaults to .external_modules
        #   file
        #   framework='all' --> Defaults to all.
        #   list
        #   no_guide
        #   output='cli' --> Defaults to cli.
        #   quiet
        #   repo_id
        #   skip_check
        #   skip_fixes
        #   skip_framework
        #   skip_suppressions
        #   soft_fail --> Done.
        #   version --> Needs to be ignored.
        config = self._read_config(config_file)
        for arg in vars(self.args):
            # If the arg is None or False, check config file and set it in the args Namespace.
            if not getattr(self.args, arg):
                if arg in config:
                    setattr(self.args, arg, config.get(arg))

    def find_config_file(self):
        if self.args.directory:
            for root_folder in self.args.directory:
                config_file = self._config_file_path(root_folder)
            if os.path.exists(config_file):
                return config_file
        else:
            current_dir_config_path = self._config_file_path(os.getcwd())
            home_dir_config_path = self._config_file_path(Path.home())

            if os.path.exists(current_dir_config_path):
                return self._config_file_path(os.getcwd())
            elif os.path.exists(home_dir_config_path):
                self.logger.debug("Config file found at {}".format())
                return self._config_file_path(Path.home())
            else:
                self.logger.debug("No checkov config file found.")
                return None

    @staticmethod
    def _read_config(config_file_path):
        with open(config_file_path, "r") as f:
            config = yaml.safe_load(f)
        return config

    @staticmethod
    def _config_file_path(dir_path):
        checkov_dir = "{}/.checkov".format(dir_path)
        return "{}/config.yaml".format(checkov_dir)


