# flake8: noqa
from termcolor import colored

from checkov.version import version
from checkov.common.version_manager import check_for_update

tool = "Checkov"
banner = r"""
       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: {} """.format(version)

new_version = check_for_update("checkov", version)
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
