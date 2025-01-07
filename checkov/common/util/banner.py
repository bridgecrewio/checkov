# flake8: noqa
from termcolor import colored

from checkov.version import version
from checkov.common.version_manager import check_for_update
from checkov.common.util.env_vars_config import env_vars_config

default_tool = "Checkov"

banner = r"""
       _               _
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V /
  \___|_| |_|\___|\___|_|\_\___/ \_/

By Prisma Cloud | version: {} """.format(version)

new_version = check_for_update("checkov", version, env_vars_config.SKIP_PACKAGE_UPDATE_CHECK)
if new_version:
    banner = (
        "\n"
        + banner
        + "\nUpdate available "
        + colored(version, "grey")
        + " -> "
        + colored(new_version, "green")
        + "\nRun "
        + colored("pip3 install -U checkov", "magenta")
        + " to update \n"
    )
