#!/usr/bin/env python
import atexit
import configargparse
import logging
import os
import shutil
import sys
from pathlib import Path

from checkov.arm.runner import Runner as arm_runner
from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.image_scanning.image_scanner import image_scanner
from checkov.common.util.ext_argument_parser import ExtArgumentParser
from checkov.common.util.config_utils import get_default_config_paths
from checkov.common.goget.github.get_git import GitGetter
from checkov.common.runners.runner_registry import RunnerRegistry, OUTPUT_CHOICES
from checkov.common.util.banner import banner as checkov_banner
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.common.util.docs_generator import print_checks
from checkov.common.util.runner_dependency_handler import RunnerDependencyHandler
from checkov.common.util.type_forcers import convert_str_to_bool
from checkov.terraform.runner import Runner as tf_graph_runner
from checkov.helm.runner import Runner as helm_runner
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.logging_init import init as logging_init
from checkov.runner_filter import RunnerFilter
from checkov.serverless.runner import Runner as sls_runner
from checkov.terraform.plan_runner import Runner as tf_plan_runner
from checkov.dockerfile.runner import Runner as dockerfile_runner
from checkov.version import version

outer_registry = None

logging_init()
logger = logging.getLogger(__name__)
checkov_runner_module_names = ['cfn', 'tf', 'k8', 'sls', 'arm', 'tf_plan', 'helm']
checkov_runners = ['cloudformation', 'terraform', 'kubernetes', 'serverless', 'arm', 'terraform_plan', 'helm',
                   'dockerfile']

# Check runners for necessary system dependencies.
runnerDependencyHandler = RunnerDependencyHandler(checkov_runner_module_names, globals())
runnerDependencyHandler.validate_runner_deps()


def run(banner=checkov_banner, argv=sys.argv[1:]):
    default_config_paths = get_default_config_paths(sys.argv[1:])
    parser = ExtArgumentParser(description='Infrastructure as code static analysis',
                               default_config_files=default_config_paths,
                               config_file_parser_class=configargparse.YAMLConfigFileParser,
                               add_env_var_help=True)
    add_parser_args(parser)
    config = parser.parse_args(argv)
    # bridgecrew uses both the urllib3 and requests libraries, while checkov uses the requests library.
    # Allow the user to specify a CA bundle to be used by both libraries.
    bc_integration.setup_http_manager(config.ca_certificate)
    
    # if a repo is passed in it'll save it.  Otherwise a default will be created based on the file or dir
    config.repo_id=bc_integration.persist_repo_id(config)
    # if a bc_api_key is passed it'll save it.  Otherwise it will check ~/.bridgecrew/credentials
    config.bc_api_key=bc_integration.persist_bc_api_key(config)

    # Disable runners with missing system dependencies
    config.skip_framework = runnerDependencyHandler.disable_incompatible_runners(config.skip_framework)

    runner_filter = RunnerFilter(framework=config.framework, skip_framework=config.skip_framework, checks=config.check,
                                 skip_checks=config.skip_check,
                                 download_external_modules=convert_str_to_bool(config.download_external_modules),
                                 external_modules_download_path=config.external_modules_download_path,
                                 evaluate_variables=convert_str_to_bool(config.evaluate_variables),
                                 runners=checkov_runners)
    if outer_registry:
        runner_registry = outer_registry
        runner_registry.runner_filter = runner_filter
    else:
        runner_registry = RunnerRegistry(banner, runner_filter, tf_graph_runner(), cfn_runner(), k8_runner(),
                                         sls_runner(),
                                         arm_runner(), tf_plan_runner(), helm_runner(), dockerfile_runner())

    if config.show_config:
        print(parser.format_values())
        return

    if config.bc_api_key == '':
        parser.error(
            'The --bc-api-key flag was specified but the value was blank. If this value was passed as a secret, '
            'you may need to double check the mapping.')
    elif config.bc_api_key:
        logger.debug(f'Using API key ending with {config.bc_api_key[-8:]}')

        if config.repo_id is None:
            parser.error("--repo-id argument is required when using --bc-api-key")
        if len(config.repo_id.split('/')) != 2:
            parser.error("--repo-id argument format should be 'organization/repository_name' E.g "
                         "bridgecrewio/checkov")

        source = os.getenv('BC_SOURCE', 'cli')
        source_version = os.getenv('BC_SOURCE_VERSION', version)
        logger.debug(f'BC_SOURCE = {source}, version = {source_version}')
        try:
            bc_integration.setup_bridgecrew_credentials(bc_api_key=config.bc_api_key, repo_id=config.repo_id,
                                                        skip_fixes=config.skip_fixes,
                                                        skip_suppressions=config.skip_suppressions,
                                                        source=source, source_version=source_version, repo_branch=config.branch)
            excluded_paths = bc_integration.get_excluded_paths()
            runner_filter.excluded_paths = excluded_paths
        except Exception as e:
            logger.error('An error occurred setting up the Bridgecrew platform integration. Please check your API token'
                         ' and try again.', exc_info=True)
            return
    else:
        logger.debug('No API key found. Scanning locally only.')

    guidelines = {}
    if not config.no_guide:
        guidelines = bc_integration.get_guidelines()

    if config.check and config.skip_check:
        if any(item in runner_filter.checks for item in runner_filter.skip_checks):
            parser.error("The check ids specified for '--check' and '--skip-check' must be mutually exclusive.")
            return

    if config.list:
        print_checks(framework=config.framework)
        return

    external_checks_dir = get_external_checks_dir(config)
    url = None

    if config.directory:
        exit_codes = []
        for root_folder in config.directory:
            file = config.file
            scan_reports = runner_registry.run(root_folder=root_folder, external_checks_dir=external_checks_dir,
                                               files=file, guidelines=guidelines)
            if bc_integration.is_integration_configured():
                bc_integration.persist_repository(root_folder)
                bc_integration.persist_scan_results(scan_reports)
                url = bc_integration.commit_repository(config.branch)

            exit_codes.append(runner_registry.print_reports(scan_reports, config, url))

        exit_code = 1 if 1 in exit_codes else 0
        return exit_code
    elif config.file:
        scan_reports = runner_registry.run(external_checks_dir=external_checks_dir, files=config.file,
                                           guidelines=guidelines,
                                           repo_root_for_plan_enrichment=config.repo_root_for_plan_enrichment)
        if bc_integration.is_integration_configured():
            files = [os.path.abspath(file) for file in config.file]
            root_folder = os.path.split(os.path.commonprefix(files))[0]
            bc_integration.persist_repository(root_folder, files)
            bc_integration.persist_scan_results(scan_reports)
            url = bc_integration.commit_repository(config.branch)
        return runner_registry.print_reports(scan_reports, config, url)
    elif config.docker_image:
        if config.bc_api_key is None:
            parser.error("--bc-api-key argument is required when using --docker-image")
            return
        if config.dockerfile_path is None:
            parser.error("--dockerfile-path argument is required when using --docker-image")
            return
        if config.branch is None:
            parser.error("--branch argument is required when using --docker-image")
            return
        image_scanner.scan(config.docker_image, config.dockerfile_path)
    else:
        print(f"{banner}")

        bc_integration.onboarding()


def add_parser_args(parser):
    parser.add('-v', '--version',
               help='version', action='version', version=version)
    parser.add('-d', '--directory', action='append',
               help='IaC root directory (can not be used together with --file).')
    parser.add('-f', '--file', action='append',
               help='IaC file(can not be used together with --directory)')
    parser.add('--external-checks-dir', action='append',
               help='Directory for custom checks to be loaded. Can be repeated')
    parser.add('--external-checks-git', action='append',
               help='Github url of external checks to be added. \n you can specify a subdirectory after a '
                    'double-slash //. \n cannot be used together with --external-checks-dir')
    parser.add('-l', '--list', help='List checks', action='store_true')
    parser.add('-o', '--output', nargs='?', choices=OUTPUT_CHOICES,
               default='cli',
               help='Report output format')
    parser.add('--no-guide', action='store_true',
               default=False,
               help='do not fetch bridgecrew guide in checkov output report')
    parser.add('--quiet', action='store_true',
               default=False,
               help='in case of CLI output, display only failed checks')
    parser.add('--compact', action='store_true',
               default=False,
               help='in case of CLI output, do not display code blocks')
    parser.add('--framework', help='filter scan to run only on a specific infrastructure code frameworks',
               choices=checkov_runners + ["all"],
               default='all')
    parser.add('--skip-framework', help='filter scan to skip specific infrastructure code frameworks. \n'
                                        'will be included automatically for some frameworks if system dependencies '
                                        'are missing.',
               choices=checkov_runners,
               default=None)
    parser.add('-c', '--check',
               help='filter scan to run only on a specific check identifier(allowlist), You can '
                    'specify multiple checks separated by comma delimiter', action='append', default=None)
    parser.add('--skip-check',
               help='filter scan to run on all check but a specific check identifier(denylist), You can '
                    'specify multiple checks separated by comma delimiter', action='append', default=None)
    parser.add('-s', '--soft-fail',
               help='Runs checks but suppresses error code', action='store_true')
    parser.add('--bc-api-key', help='Bridgecrew API key', env_var='BC_API_KEY')
    parser.add('--docker-image', help='Scan docker images by name or ID. Only works with --bc-api-key flag')
    parser.add('--dockerfile-path', help='Path to the Dockerfile of the scanned docker image')
    parser.add('--repo-id',
               help='Identity string of the repository, with form <repo_owner>/<repo_name>')
    parser.add('-b', '--branch',
               help="Selected branch of the persisted repository. Only has effect when using the --bc-api-key flag",
               default='master')
    parser.add('--skip-fixes',
               help='Do not download fixed resource templates from Bridgecrew. Only has effect when using the '
                    '--bc-api-key flag',
               action='store_true')
    parser.add('--skip-suppressions',
               help='Do not download preconfigured suppressions from the Bridgecrew platform. Code comment '
                    'suppressions will still be honored. '
                    'Only has effect when using the --bc-api-key flag',
               action='store_true')
    parser.add('--download-external-modules',
               help="download external terraform modules from public git repositories and terraform registry",
               default=os.environ.get('DOWNLOAD_EXTERNAL_MODULES', False), env_var='DOWNLOAD_EXTERNAL_MODULES')
    parser.add('--external-modules-download-path',
               help="set the path for the download external terraform modules",
               default=DEFAULT_EXTERNAL_MODULES_DIR, env_var='EXTERNAL_MODULES_DIR')
    parser.add('--evaluate-variables',
               help="evaluate the values of variables and locals",
               default=True)
    parser.add('-ca', '--ca-certificate',
               help='custom CA (bundle) file', default=None, env_var='CA_CERTIFICATE')
    parser.add('--repo-root-for-plan-enrichment',
               help='Directory containing the hcl code used to generate a given plan file. Use with -f.',
               dest="repo_root_for_plan_enrichment")
    parser.add('--config-file', help='path to the Checkov configuration YAML file', is_config_file=True, default=None)
    parser.add('--create-config', help='takes the current command line args and writes them out to a config file at '
                                       'the given path', is_write_out_config_file_arg=True, default=None)
    parser.add('--show-config', help='prints all args and config settings and where they came from '
                                     '(eg. commandline, config file, environment variable or default)',
               action='store_true', default=None)


def get_external_checks_dir(config):
    external_checks_dir = config.external_checks_dir
    if config.external_checks_git:
        git_getter = GitGetter(config.external_checks_git[0])
        external_checks_dir = [git_getter.get()]
        atexit.register(shutil.rmtree, str(Path(external_checks_dir[0]).parent))
    return external_checks_dir


if __name__ == '__main__':
    exit(run())
