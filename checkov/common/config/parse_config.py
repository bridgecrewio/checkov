import os
import yaml

from pathlib import Path

home = str(Path.home())
checkov_dir = "{}/.checkov".format(home)
checkov_file = "{}/config.yaml".format(checkov_dir)


def read_config():
    if os.path.exists(checkov_file):
        with open(checkov_file, "r") as f:
            return yaml.safe_load(f)
