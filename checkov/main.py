#!/usr/bin/env python
import atexit
import logging
import os
from os import name as os_name

import argparse
import shutil
from pathlib import Path
from typing import Optional, Iterator

from checkov.arm.runner import Runner as arm_runner
from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.goget.github.get_git import GitGetter
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.banner import banner as checkov_banner
from checkov.common.util.docs_generator import print_checks
from checkov.config import CheckovConfig, OUTPUT_CHOICES, FRAMEWORK_CHOICES, MERGING_BEHAVIOR_CHOICES, PROGRAM_NAME, \
    CheckovConfigError
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.logging_init import init as logging_init
from checkov.runner_filter import RunnerFilter
from checkov.serverless.runner import Runner as sls_runner
from checkov.terraform.runner import Runner as tf_runner
from checkov.version import version

outer_registry = None

ORDERED_CONFIG_FILES = [
    'tox.ini',
    'setup.cfg',
    f'.{PROGRAM_NAME}.yml',
    f'.{PROGRAM_NAME}.yaml',
    f'.{PROGRAM_NAME}',
]
'''Ordered file names of local config starting with the lowest priority.'''

logging_init()

logger = logging.getLogger(__name__)


def run(banner=checkov_banner):
    parser = argparse.ArgumentParser(description='Infrastructure as code static analysis')
    add_parser_args(parser)
    args = parser.parse_args()
    config = CheckovConfig.from_args(args)
    config.extend(get_configuration_from_files())
    bc_integration = BcPlatformIntegration()
    runner_filter = RunnerFilter(framework=config.framework, checks=config.check, skip_checks=config.skip_check)
    if outer_registry:
        runner_registry = outer_registry
        runner_registry.runner_filter = runner_filter
    else:
        runner_registry = RunnerRegistry(banner, runner_filter, tf_runner(), cfn_runner(), k8_runner(), sls_runner(),
                                         arm_runner())
    if args.version:
        print(version)
        return
    if args.bc_api_key:
        if config.repo_id is None:
            parser.error("--repo-id argument is required when using --bc-api-key")
        if len(config.repo_id.split('/')) != 2:
            parser.error("--repo-id argument format should be 'organization/repository_name' E.g "
                         "bridgecrewio/checkov")
        bc_integration.setup_bridgecrew_credentials(bc_api_key=args.bc_api_key, repo_id=config.repo_id)

    guidelines = {}
    if not config.no_guide:
        guidelines = bc_integration.get_guidelines()
    if not config.is_check_selection_valid:
        parser.error("--check and --skip-check can not be applied together. please use only one of them")
        return
    if args.list:
        print_checks(framework=config.framework)
        return
    external_checks_dir = get_external_checks_dir(config)
    if config.directory:
        for root_folder in config.directory:
            file = config.file
            scan_reports = runner_registry.run(root_folder=root_folder, external_checks_dir=external_checks_dir,
                                               files=file, guidelines=guidelines)
            if bc_integration.is_integration_configured():
                bc_integration.persist_repository(root_folder)
                bc_integration.persist_scan_results(scan_reports)
                bc_integration.commit_repository(config.branch)
            runner_registry.print_reports(scan_reports, config)
        return
    elif config.file:
        scan_reports = runner_registry.run(external_checks_dir=external_checks_dir, files=config.file,
                                           guidelines=guidelines)
        if bc_integration.is_integration_configured():
            files = [os.path.abspath(file) for file in config.file]
            root_folder = os.path.split(os.path.commonprefix(files))[0]
            bc_integration.persist_repository(root_folder)
            bc_integration.persist_scan_results(scan_reports)
            bc_integration.commit_repository(config.branch)
        runner_registry.print_reports(scan_reports, config)
    else:
        print("No argument given. Try ` --help` for further information")


def get_configuration_from_files() -> CheckovConfig:
    # user level - may be used for referring to costume check locations
    config = get_configuration_from_global_files()
    for local_config in get_configuration_from_local_files():
        local_config.extend(config)
        config = local_config
    return config


def get_configuration_from_global_files() -> Optional[CheckovConfig]:
    if os_name == 'nt':
        user_config_file = os.path.expanduser(f'~/.{PROGRAM_NAME}/config')
    else:
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
        if xdg_config_home:
            # XDG_CONFIG_HOME defaults to $HOME/.config
            user_config_file = os.path.join(xdg_config_home, PROGRAM_NAME, 'config')
        else:
            # if it is not set, we search in the users home
            user_config_file = os.path.expanduser(f'~/.config/{PROGRAM_NAME}/config')
    try:
        user_config = CheckovConfig.from_file(user_config_file)
        return user_config
    except CheckovConfigError:
        logger.exception(f'Failed to parse the config file from {user_config_file}')
        return None
    except FileNotFoundError:
        logger.debug(f'Config file at {user_config_file} not found')
        return None
    except OSError:
        logger.exception(f'Failed to read config file from {user_config_file}')
        return None


def get_configuration_from_local_files() -> Iterator[CheckovConfig]:
    """
    Create an iterator over each config file present in the local directory. The items in the iterator are sorted by
    priority, starting with the lowest priority.

    :return:
    """
    for file in ORDERED_CONFIG_FILES:
        try:
            yield CheckovConfig.from_file(file)
        except CheckovConfigError:
            logger.exception(f'Failed to parse the config file from {file}')
            continue
        except FileNotFoundError:
            logger.debug(f'Config file at {file} not found')
            continue
        except OSError:
            logger.exception(f'Failed to read config file from {file}')
            continue


def add_parser_args(parser):
    parser.add_argument('-v', '--version',
                        help='version', action='store_true')
    parser.add_argument('-d', '--directory', action='append',
                        help='IaC root directory (can not be used together with --file). Can be repeated')
    parser.add_argument('-f', '--file', action='append',
                        help='IaC file(can not be used together with --directory)')
    parser.add_argument('--external-checks-dir', action='append',
                        help='Directory for custom checks to be loaded. Can be repeated')
    parser.add_argument('--external-checks-git', action='append',
                        help='Github url of external checks to be added. \n you can specify a subdirectory after a '
                             'double-slash //. \n cannot be used together with --external-checks-dir')
    parser.add_argument('-l', '--list', help='List checks', action='store_true')
    parser.add_argument('-o', '--output', nargs='?', choices=OUTPUT_CHOICES,
                        # Default value is implemented in config.CheckovConfig.output
                        help='Report output format')
    parser.add_argument('--no-guide', action='store_true', default=None,
                        # Default value is implemented in config.CheckovConfig.no_guide
                        help='do not fetch bridgecrew guide in checkov output report')
    parser.add_argument('--quiet', action='store_true', default=None,
                        # Default value is implemented in config.CheckovConfig.quiet
                        help='in case of CLI output, display only failed checks')
    parser.add_argument('--framework', help='filter scan to run only on a specific infrastructure code frameworks',
                        # Default value is implemented in config.CheckovConfig.framework
                        choices=FRAMEWORK_CHOICES)
    parser.add_argument('--merging-behavior',
                        help='Change the behavior how --check and --skip-check are merged with existing definitions '
                             'inside a configuration file. By default "override_if_present" is used, which will ignore '
                             'configuration files if you specify --check or --skip-check. "override" will completely '
                             'ignore configuration files for --check and --skip-check. This can be used to clear the '
                             'selection from existing configuration files. "union" will keep the checks from the '
                             'command line and the one defined in configuration files. "copy_parent" ignore the '
                             'current configuration and use the parent instead. This is not useful for command line '
                             'but for disabling a configuration permanently.',
                        # Default value is implemented in config.CheckovConfig.merging_behavior
                        choices=MERGING_BEHAVIOR_CHOICES)
    parser.add_argument('-c', '--check',
                        help='filter scan to run only on a specific check identifier(allowlist), You can '
                             'specify multiple checks separated by comma delimiter. E.g.: CKV_AWS_1,CKV_AWS_3 '
                             'You may want to specify a different --merging-behavior.', default=None)
    parser.add_argument('--skip-check',
                        help='filter scan to run on all check but a specific check identifier(denylist), You can '
                             'specify multiple checks separated by comma delimiter. E.g.: CKV_AWS_1,CKV_AWS_3 '
                             'You may want to specify a different --merging-behavior.', default=None)
    parser.add_argument('-s', '--soft-fail', default=None,
                        # Default value is implemented in config.CheckovConfig.soft_fail
                        help='Runs checks but suppresses error code', action='store_true')
    parser.add_argument('--bc-api-key', help='Bridgecrew API key')
    parser.add_argument('--repo-id',
                        help='Identity string of the repository, with form <repo_owner>/<repo_name>')
    parser.add_argument('-b', '--branch',
                        # Default value is implemented in config.CheckovConfig.branch
                        help='Selected branch of the persisted repository. Only has effect when using the --bc-api-key '
                             'flag. Defaults to "master"')


def get_external_checks_dir(config: CheckovConfig):
    external_checks_dir = config.external_checks_dir
    if config.external_checks_git:
        git_getter = GitGetter(config.external_checks_git[0])
        external_checks_dir = [git_getter.get()]
        atexit.register(shutil.rmtree, str(Path(external_checks_dir[0]).parent))
    return external_checks_dir


if __name__ == '__main__':
    run()
