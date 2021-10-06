#!/usr/bin/env python
import atexit
import json
import logging
import os
import shutil
import sys
import signal
from pathlib import Path

import configargparse

signal.signal(signal.SIGINT, lambda x, y: sys.exit(''))

from checkov.arm.runner import Runner as arm_runner
from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.bridgecrew.bc_source import SourceTypes, BCSourceType, get_source_type
from checkov.common.bridgecrew.image_scanning.image_scanner import image_scanner
from checkov.common.bridgecrew.integration_features.integration_feature_registry import integration_feature_registry
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.goget.github.get_git import GitGetter
from checkov.common.output.baseline import Baseline
from checkov.common.runners.runner_registry import RunnerRegistry, OUTPUT_CHOICES
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.util.banner import banner as checkov_banner
from checkov.common.util.config_utils import get_default_config_paths
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.common.util.docs_generator import print_checks
from checkov.common.util.ext_argument_parser import ExtArgumentParser
from checkov.common.util.runner_dependency_handler import RunnerDependencyHandler
from checkov.common.util.type_forcers import convert_str_to_bool
from checkov.dockerfile.runner import Runner as dockerfile_runner
from checkov.helm.runner import Runner as helm_runner
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.logging_init import init as logging_init
from checkov.runner_filter import RunnerFilter
from checkov.secrets.runner import Runner as secrets_runner
from checkov.serverless.runner import Runner as sls_runner
from checkov.terraform.plan_runner import Runner as tf_plan_runner
from checkov.terraform.runner import Runner as tf_graph_runner
from checkov.json_doc.runner import Runner as json_runner
from checkov.version import version

outer_registry = None

logging_init()
logger = logging.getLogger(__name__)
checkov_runners = ['cloudformation', 'terraform', 'kubernetes', 'serverless', 'arm', 'terraform_plan', 'helm',
                   'dockerfile', 'secrets', 'json']

DEFAULT_RUNNERS = (tf_graph_runner(), cfn_runner(), k8_runner(),
                   sls_runner(), arm_runner(), tf_plan_runner(), helm_runner(),
                   dockerfile_runner(), secrets_runner(), json_runner())


def run(banner=checkov_banner, argv=sys.argv[1:]):
    default_config_paths = get_default_config_paths(sys.argv[1:])
    parser = ExtArgumentParser(description='Infrastructure as code static analysis',
                               default_config_files=default_config_paths,
                               config_file_parser_class=configargparse.YAMLConfigFileParser,
                               add_env_var_help=True)
    add_parser_args(parser)
    config = parser.parse_args(argv)

    # Check if --output value is None. If so, replace with ['cli'] for default cli output.
    if config.output == None:
        config.output = ['cli']

    # bridgecrew uses both the urllib3 and requests libraries, while checkov uses the requests library.
    # Allow the user to specify a CA bundle to be used by both libraries.
    bc_integration.setup_http_manager(config.ca_certificate)

    # if a repo is passed in it'll save it.  Otherwise a default will be created based on the file or dir
    config.repo_id = bc_integration.persist_repo_id(config)
    # if a bc_api_key is passed it'll save it.  Otherwise it will check ~/.bridgecrew/credentials
    config.bc_api_key = bc_integration.persist_bc_api_key(config)

    excluded_paths = config.skip_path or []

    if config.var_file:
        config.var_file = [os.path.abspath(f) for f in config.var_file]

    runner_filter = RunnerFilter(framework=config.framework, skip_framework=config.skip_framework, checks=config.check,
                                 skip_checks=config.skip_check,
                                 download_external_modules=convert_str_to_bool(config.download_external_modules),
                                 external_modules_download_path=config.external_modules_download_path,
                                 evaluate_variables=convert_str_to_bool(config.evaluate_variables),
                                 runners=checkov_runners, excluded_paths=excluded_paths,
                                 all_external=config.run_all_external_checks, var_files=config.var_file)
    if outer_registry:
        runner_registry = outer_registry
        runner_registry.runner_filter = runner_filter
    else:
        runner_registry = RunnerRegistry(banner, runner_filter, *DEFAULT_RUNNERS)

    runnerDependencyHandler = RunnerDependencyHandler(runner_registry)
    runnerDependencyHandler.validate_runner_deps()

    if config.show_config:
        print(parser.format_values())
        return

    if config.bc_api_key == '':
        parser.error('The --bc-api-key flag was specified but the value was blank. If this value was passed as a '
                     'secret, you may need to double check the mapping.')
    elif config.bc_api_key:
        logger.debug(f'Using API key ending with {config.bc_api_key[-8:]}')

        if config.repo_id is None and not config.list:
            # if you are only listing policies, then the API key will be used to fetch policies, but that's it,
            # so the repo is not required
            parser.error("--repo-id argument is required when using --bc-api-key")
        elif config.repo_id and len(config.repo_id.split('/')) != 2:
            parser.error("--repo-id argument format should be 'organization/repository_name' E.g "
                         "bridgecrewio/checkov")

        source_env_val = os.getenv('BC_SOURCE', 'cli')
        source = get_source_type(source_env_val)
        if source == SourceTypes[BCSourceType.DISABLED]:
            logger.warning(f'Received unexpected value for BC_SOURCE: {source_env_val}; Should be one of {{{",".join(SourceTypes.keys())}}} setting source to DISABLED')
        source_version = os.getenv('BC_SOURCE_VERSION', version)
        logger.debug(f'BC_SOURCE = {source.name}, version = {source_version}')

        if config.list:
            # This speeds up execution by not setting up upload credentials (since we won't upload anything anyways)
            logger.debug('Using --list; setting source to DISABLED')
            source = SourceTypes[BCSourceType.DISABLED]

        try:
            bc_integration.bc_api_key = config.bc_api_key
            bc_integration.setup_bridgecrew_credentials(repo_id=config.repo_id,
                                                        skip_fixes=config.skip_fixes,
                                                        skip_suppressions=config.skip_suppressions,
                                                        skip_policy_download=config.skip_policy_download,
                                                        source=source, source_version=source_version, repo_branch=config.branch)
            platform_excluded_paths = bc_integration.get_excluded_paths() or []
            runner_filter.excluded_paths = runner_filter.excluded_paths + platform_excluded_paths
        except Exception as e:
            logger.error('An error occurred setting up the Bridgecrew platform integration. Please check your API token'
                         ' and try again.', exc_info=True)
            return
    else:
        logger.debug('No API key found. Scanning locally only.')

    if config.check and config.skip_check:
        if any(item in runner_filter.checks for item in runner_filter.skip_checks):
            parser.error("The check ids specified for '--check' and '--skip-check' must be mutually exclusive.")
            return

    integration_feature_registry.run_pre_scan()

    guidelines = {}
    if not config.no_guide:
        guidelines = bc_integration.get_guidelines()

        ckv_to_bc_mapping = bc_integration.get_ckv_to_bc_id_mapping()
        if ckv_to_bc_mapping:
            all_checks = BaseCheckRegistry.get_all_registered_checks()
            for check in all_checks:
                check.bc_id = ckv_to_bc_mapping.get(check.id)

    if config.list:
        print_checks(framework=config.framework, use_bc_ids=config.output_bc_ids)
        return

    baseline = None
    if config.baseline:
        baseline = Baseline()
        baseline.from_json(config.baseline)

    external_checks_dir = get_external_checks_dir(config)
    url = None
    created_baseline_path = None

    if config.directory:
        exit_codes = []
        for root_folder in config.directory:
            file = config.file
            scan_reports = runner_registry.run(root_folder=root_folder, external_checks_dir=external_checks_dir,
                                               files=file, guidelines=guidelines)
            if baseline:
                baseline.compare_and_reduce_reports(scan_reports)
            if bc_integration.is_integration_configured():
                bc_integration.persist_repository(root_folder, excluded_paths=runner_filter.excluded_paths)
                bc_integration.persist_scan_results(scan_reports)
                url = bc_integration.commit_repository(config.branch)

            if config.create_baseline:
                overall_baseline = Baseline()
                for report in scan_reports:
                    overall_baseline.add_findings_from_report(report)
                created_baseline_path = os.path.join(os.path.abspath(root_folder), '.checkov.baseline')
                with open(created_baseline_path, 'w') as f:
                    json.dump(overall_baseline.to_dict(), f, indent=4)
            exit_codes.append(runner_registry.print_reports(scan_reports, config, url=url, created_baseline_path=created_baseline_path, baseline=baseline))
        exit_code = 1 if 1 in exit_codes else 0
        return exit_code
    elif config.file:
        scan_reports = runner_registry.run(external_checks_dir=external_checks_dir, files=config.file,
                                           guidelines=guidelines,
                                           repo_root_for_plan_enrichment=config.repo_root_for_plan_enrichment)
        if baseline:
            baseline.compare_and_reduce_reports(scan_reports)
        if config.create_baseline:
            overall_baseline = Baseline()
            for report in scan_reports:
                overall_baseline.add_findings_from_report(report)
            created_baseline_path = os.path.join(os.path.abspath(os.path.commonprefix(config.file)), '.checkov.baseline')
            with open(created_baseline_path, 'w') as f:
                json.dump(overall_baseline.to_dict(), f, indent=4)

        if bc_integration.is_integration_configured():
            files = [os.path.abspath(file) for file in config.file]
            root_folder = os.path.split(os.path.commonprefix(files))[0]
            bc_integration.persist_repository(root_folder, files, excluded_paths=runner_filter.excluded_paths)
            bc_integration.persist_scan_results(scan_reports)
            url = bc_integration.commit_repository(config.branch)
        return runner_registry.print_reports(scan_reports, config, url=url, created_baseline_path=created_baseline_path,
                                             baseline=baseline)
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
        bc_integration.commit_repository(config.branch)
        image_scanner.scan(config.docker_image, config.dockerfile_path)
    elif not config.quiet:
        print(f"{banner}")

        bc_integration.onboarding()


def add_parser_args(parser):
    parser.add('-v', '--version',
               help='version', action='version', version=version)
    parser.add('-d', '--directory', action='append',
               help='IaC root directory (can not be used together with --file).')
    parser.add('-f', '--file', action='append',
               help='IaC file(can not be used together with --directory)')
    parser.add('--skip-path', action='append',
               help='Path (file or directory) to skip, using regular expression logic, relative to current '
                    'working directory. Word boundaries are not implicit; i.e., specifying "dir1" will skip any '
                    'directory or subdirectory named "dir1". Ignored with -f. Can be specified multiple times.')
    parser.add('--external-checks-dir', action='append',
               help='Directory for custom checks to be loaded. Can be repeated')
    parser.add('--external-checks-git', action='append',
               help='Github url of external checks to be added. \n you can specify a subdirectory after a '
                    'double-slash //. \n cannot be used together with --external-checks-dir')
    parser.add('-l', '--list', help='List checks', action='store_true')
    parser.add('-o', '--output', action='append', choices=OUTPUT_CHOICES,
               default=None,
               help='Report output format. Can be repeated')
    parser.add('--output-bc-ids', action='store_true',
               help='Print Bridgecrew platform IDs (BC...) instead of Checkov IDs (CKV...), if the check exists in the platform')
    parser.add('--no-guide', action='store_true',
               default=False,
               help='Do not fetch Bridgecrew platform IDs and guidelines for the checkov output report. Note: this '
                    'prevents Bridgecrew platform check IDs from being used anywhere in the CLI.')
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
    parser.add('--run-all-external-checks', action='store_true',
               help='Run all external checks (loaded via --external-checks options) even if the checks are not present '
                    'in the --check list. This allows you to always ensure that new checks present in the external '
                    'source are used. If an external check is included in --skip-check, it will still be skipped.')
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
    parser.add('--skip-policy-download',
               help='Do not download custom policies configured in the Bridgecrew platform. '
                    'Only has effect when using the --bc-api-key flag',
               action='store_true')
    parser.add('--download-external-modules',
               help="download external terraform modules from public git repositories and terraform registry",
               default=os.environ.get('DOWNLOAD_EXTERNAL_MODULES', False), env_var='DOWNLOAD_EXTERNAL_MODULES')
    parser.add('--var-file', action='append',
               help='Variable files to load in addition to the default files (see '
                    'https://www.terraform.io/docs/language/values/variables.html#variable-definitions-tfvars-files).'
                    'Currently only supported for source Terraform (.tf file) scans. Requires using --directory, not --file.')
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
               dest="repo_root_for_plan_enrichment", action='append')
    parser.add('--config-file', help='path to the Checkov configuration YAML file', is_config_file=True, default=None)
    parser.add('--create-config', help='takes the current command line args and writes them out to a config file at '
                                       'the given path', is_write_out_config_file_arg=True, default=None)
    parser.add('--show-config', help='prints all args and config settings and where they came from '
                                     '(eg. commandline, config file, environment variable or default)',
               action='store_true', default=None)
    parser.add('--create-baseline', help='Alongside outputting the findings, save all results to .checkov.baseline file'
                                         ' so future runs will not re-flag the same noise. Works only with `--directory` flag',
               action='store_true', default=False)
    parser.add('--baseline', help='Use a .checkov.baseline file to compare current results with a known baseline. Report will include only failed checks that are new'
                                  'with respect to the provided baseline', default=None)
    # Add mutually exclusive groups of arguments
    exit_code_group = parser.add_mutually_exclusive_group()
    exit_code_group.add('-s', '--soft-fail', help='Runs checks but suppresses error code', action='store_true')
    exit_code_group.add('--soft-fail-on', help='Exits with a 0 exit code for specified checks. You can specify '
                                               'multiple checks separated by comma delimiter', action='append',
                        default=None)
    exit_code_group.add('--hard-fail-on', help='Exits with a non-zero exit code for specified checks. You can specify '
                                               'multiple checks separated by comma delimiter', action='append',
                        default=None)


def get_external_checks_dir(config):
    external_checks_dir = config.external_checks_dir
    if config.external_checks_git:
        git_getter = GitGetter(config.external_checks_git[0])
        external_checks_dir = [git_getter.get()]
        atexit.register(shutil.rmtree, str(Path(external_checks_dir[0]).parent))
    return external_checks_dir


if __name__ == '__main__':
    exit(run())
