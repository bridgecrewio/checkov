#!/usr/bin/env python
import argparse
import atexit
import logging
import os
import shutil
import sys
from pathlib import Path

from checkov.arm.runner import Runner as arm_runner
from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.image_scanning.image_scanner import image_scanner
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
checkov_runners = ['cloudformation', 'terraform', 'kubernetes', 'serverless', 'arm', 'terraform_plan', 'helm', 'dockerfile']

# Check runners for necessary system dependencies.
runnerDependencyHandler = RunnerDependencyHandler(checkov_runner_module_names, globals())
runnerDependencyHandler.validate_runner_deps()


def run(banner=checkov_banner, argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Infrastructure as code static analysis')
    add_parser_args(parser)
    args = parser.parse_args(argv)

    # bridgecrew uses both the urllib3 and requests libraries, while checkov uses the requests library.
    # Allow the user to specify a CA bundle to be used by both libraries.
    bc_integration.setup_http_manager(args.ca_certificate)

    # Disable runners with missing system dependencies
    args.skip_framework = runnerDependencyHandler.disable_incompatible_runners(args.skip_framework)

    runner_filter = RunnerFilter(framework=args.framework, skip_framework=args.skip_framework, checks=args.check, skip_checks=args.skip_check,
                                 download_external_modules=convert_str_to_bool(args.download_external_modules),
                                 external_modules_download_path=args.external_modules_download_path,
                                 evaluate_variables=convert_str_to_bool(args.evaluate_variables), runners=checkov_runners)
    if outer_registry:
        runner_registry = outer_registry
        runner_registry.runner_filter = runner_filter
    else:
        runner_registry = RunnerRegistry(banner, runner_filter, tf_graph_runner(), cfn_runner(), k8_runner(), sls_runner(),
                                         arm_runner(), tf_plan_runner(), helm_runner(),dockerfile_runner())
    if args.version:
        print(version)
        return

    if args.bc_api_key == '':
        parser.error('The --bc-api-key flag was specified but the value was blank. If this value was passed as a secret, you may need to double check the mapping.')
    elif args.bc_api_key:
        logger.debug(f'Using API key ending with {args.bc_api_key[-8:]}')

        if args.repo_id is None:
            parser.error("--repo-id argument is required when using --bc-api-key")
        if len(args.repo_id.split('/')) != 2:
            parser.error("--repo-id argument format should be 'organization/repository_name' E.g "
                         "bridgecrewio/checkov")

        source = os.getenv('BC_SOURCE', 'cli')
        source_version = os.getenv('BC_SOURCE_VERSION', version)
        logger.debug(f'BC_SOURCE = {source}, version = {source_version}')
        try:
            bc_integration.setup_bridgecrew_credentials(bc_api_key=args.bc_api_key, repo_id=args.repo_id, 
                                                        skip_fixes=args.skip_fixes,
                                                        skip_suppressions=args.skip_suppressions,
                                                        source=source, source_version=source_version, repo_branch=args.branch)
        except Exception as e:
            logger.error('An error occurred setting up the Bridgecrew platform integration. Please check your API token and try again.', exc_info=True)
            return
    else:
        logger.debug('No API key found. Scanning locally only.')

    guidelines = {}
    if not args.no_guide:
        guidelines = bc_integration.get_guidelines()
    if args.check and args.skip_check:
        parser.error("--check and --skip-check can not be applied together. please use only one of them")
        return
    if args.list:
        print_checks(framework=args.framework)
        return
    external_checks_dir = get_external_checks_dir(args)
    url = None

    if args.directory:
        exit_codes = []
        for root_folder in args.directory:
            file = args.file
            scan_reports = runner_registry.run(root_folder=root_folder, external_checks_dir=external_checks_dir,
                                               files=file, guidelines=guidelines, bc_integration=bc_integration)
            if bc_integration.is_integration_configured():
                bc_integration.persist_repository(root_folder)
                bc_integration.persist_scan_results(scan_reports)
                url = bc_integration.commit_repository(args.branch)

            exit_codes.append(runner_registry.print_reports(scan_reports, args, url))

        exit_code = 1 if 1 in exit_codes else 0
        return exit_code
    elif args.file:
        scan_reports = runner_registry.run(external_checks_dir=external_checks_dir, files=args.file,
                                           guidelines=guidelines, bc_integration=bc_integration)
        if bc_integration.is_integration_configured():
            files = [os.path.abspath(file) for file in args.file]
            root_folder = os.path.split(os.path.commonprefix(files))[0]
            bc_integration.persist_repository(root_folder)
            bc_integration.persist_scan_results(scan_reports)
            url = bc_integration.commit_repository(args.branch)
        return runner_registry.print_reports(scan_reports, args, url)
    elif args.docker_image:
        if args.bc_api_key is None:
            parser.error("--bc-api-key argument is required when using --docker-image")
            return
        if args.dockerfile_path is None:
            parser.error("--dockerfile-path argument is required when using --docker-image")
            return
        if args.branch is None:
            parser.error("--branch argument is required when using --docker-image")
            return
        image_scanner.scan(args.docker_image, args.dockerfile_path)
    else:
        print(f"{banner}")

        bc_integration.onboarding()


def add_parser_args(parser):
    parser.add_argument('-v', '--version',
                        help='version', action='store_true')
    parser.add_argument('-d', '--directory', action='append',
                        help='IaC root directory (can not be used together with --file).')
    parser.add_argument('-f', '--file', action='append',
                        help='IaC file(can not be used together with --directory)')
    parser.add_argument('--external-checks-dir', action='append',
                        help='Directory for custom checks to be loaded. Can be repeated')
    parser.add_argument('--external-checks-git', action='append',
                        help='Github url of external checks to be added. \n you can specify a subdirectory after a '
                             'double-slash //. \n cannot be used together with --external-checks-dir')
    parser.add_argument('-l', '--list', help='List checks', action='store_true')
    parser.add_argument('-o', '--output', nargs='?', choices=OUTPUT_CHOICES,
                        default='cli',
                        help='Report output format')
    parser.add_argument('--no-guide', action='store_true',
                        default=False,
                        help='do not fetch bridgecrew guide in checkov output report')
    parser.add_argument('--quiet', action='store_true',
                        default=False,
                        help='in case of CLI output, display only failed checks')
    parser.add_argument('--compact', action='store_true',
                        default=False,
                        help='in case of CLI output, do not display code blocks')
    parser.add_argument('--framework', help='filter scan to run only on a specific infrastructure code frameworks',
                        choices=checkov_runners + ["all"],
                        default='all')
    parser.add_argument('--skip-framework', help='filter scan to skip specific infrastructure code frameworks. \n'
                                                 'will be included automatically for some frameworks if system dependencies are missing.',
                        choices=checkov_runners,
                        default=None)
    parser.add_argument('-c', '--check',
                        help='filter scan to run only on a specific check identifier(allowlist), You can '
                             'specify multiple checks separated by comma delimiter', default=None)
    parser.add_argument('--skip-check',
                        help='filter scan to run on all check but a specific check identifier(denylist), You can '
                             'specify multiple checks separated by comma delimiter', default=None)
    parser.add_argument('-s', '--soft-fail',
                        help='Runs checks but suppresses error code', action='store_true')
    parser.add_argument('--bc-api-key', help='Bridgecrew API key')
    parser.add_argument('--docker-image', help='Scan docker images by name or ID. Only works with --bc-api-key flag')
    parser.add_argument('--dockerfile-path', help='Path to the Dockerfile of the scanned docker image')
    parser.add_argument('--repo-id',
                        help='Identity string of the repository, with form <repo_owner>/<repo_name>')
    parser.add_argument('-b', '--branch',
                        help="Selected branch of the persisted repository. Only has effect when using the --bc-api-key flag",
                        default='master')
    parser.add_argument('--skip-fixes',
                        help='Do not download fixed resource templates from Bridgecrew. Only has effect when using the --bc-api-key flag',
                        action='store_true')
    parser.add_argument('--skip-suppressions',
                        help='Do not download preconfigured suppressions from the Bridgecrew platform. Code comment suppressions will still be honored. '
                             'Only has effect when using the --bc-api-key flag',
                        action='store_true')
    parser.add_argument('--download-external-modules',
                        help="download external terraform modules from public git repositories and terraform registry",
                        default=os.environ.get('DOWNLOAD_EXTERNAL_MODULES', False))
    parser.add_argument('--external-modules-download-path',
                        help="set the path for the download external terraform modules",
                        default=DEFAULT_EXTERNAL_MODULES_DIR)
    parser.add_argument('--evaluate-variables',
                        help="evaluate the values of variables and locals",
                        default=True)
    parser.add_argument('-ca', '--ca-certificate',
                        help='custom CA (bundle) file', default=None)

def get_external_checks_dir(args):
    external_checks_dir = args.external_checks_dir
    if args.external_checks_git:
        git_getter = GitGetter(args.external_checks_git[0])
        external_checks_dir = [git_getter.get()]
        atexit.register(shutil.rmtree, str(Path(external_checks_dir[0]).parent))
    return external_checks_dir


if __name__ == '__main__':
    exit(run())
