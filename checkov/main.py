#!/usr/bin/env python
from __future__ import annotations

import atexit
import json
import logging
import os
import shutil
import signal
import sys
from pathlib import Path
from typing import Any, List, Optional, TYPE_CHECKING

import argcomplete  # type:ignore[import]
import configargparse
from urllib3.exceptions import MaxRetryError

import checkov.logging_init  # noqa  # should be imported before the others to ensure correct logging setup

from checkov.argo_workflows.runner import Runner as argo_workflows_runner
from checkov.arm.runner import Runner as arm_runner
from checkov.azure_pipelines.runner import Runner as azure_pipelines_runner
from checkov.bitbucket.runner import Runner as bitbucket_configuration_runner
from checkov.bitbucket_pipelines.runner import Runner as bitbucket_pipelines_runner
from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.bridgecrew.bc_source import SourceTypes, BCSourceType, get_source_type
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import \
    integration as policy_metadata_integration
from checkov.common.bridgecrew.integration_features.features.repo_config_integration import \
    integration as repo_config_integration
from checkov.common.bridgecrew.integration_features.features.suppressions_integration import \
    integration as suppressions_integration
from checkov.common.bridgecrew.integration_features.integration_feature_registry import integration_feature_registry
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.integration_features.features.licensing_integration import integration as licensing_integration
from checkov.common.goget.github.get_git import GitGetter
from checkov.common.output.baseline import Baseline
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.runners.runner_registry import RunnerRegistry, OUTPUT_CHOICES, SUMMARY_POSITIONS
from checkov.common.util import prompt
from checkov.common.util.banner import banner as checkov_banner
from checkov.common.util.config_utils import get_default_config_paths
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR, CHECKOV_RUN_SCA_PACKAGE_SCAN_V2
from checkov.common.util.docs_generator import print_checks
from checkov.common.util.ext_argument_parser import ExtArgumentParser
from checkov.common.util.runner_dependency_handler import RunnerDependencyHandler
from checkov.common.util.type_forcers import convert_str_to_bool
from checkov.contributor_metrics import report_contributor_metrics
from checkov.dockerfile.runner import Runner as dockerfile_runner
from checkov.github.runner import Runner as github_configuration_runner
from checkov.github_actions.runner import Runner as github_actions_runner
from checkov.gitlab.runner import Runner as gitlab_configuration_runner
from checkov.gitlab_ci.runner import Runner as gitlab_ci_runner
from checkov.helm.runner import Runner as helm_runner
from checkov.json_doc.runner import Runner as json_runner
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.kustomize.runner import Runner as kustomize_runner
from checkov.runner_filter import RunnerFilter
from checkov.sca_image.runner import Runner as sca_image_runner
from checkov.sca_package.runner import Runner as sca_package_runner
from checkov.sca_package_2.runner import Runner as sca_package_runner_2
from checkov.secrets.runner import Runner as secrets_runner
from checkov.serverless.runner import Runner as sls_runner
from checkov.terraform.plan_runner import Runner as tf_plan_runner
from checkov.terraform.runner import Runner as tf_graph_runner
from checkov.version import version
from checkov.yaml_doc.runner import Runner as yaml_runner
from checkov.bicep.runner import Runner as bicep_runner
from checkov.openapi.runner import Runner as openapi_runner
from checkov.circleci_pipelines.runner import Runner as circleci_pipelines_runner

if TYPE_CHECKING:
    from configargparse import ArgumentParser, Namespace

signal.signal(signal.SIGINT, lambda x, y: sys.exit(''))

outer_registry = None

logger = logging.getLogger(__name__)
checkov_runners = [value for attr, value in CheckType.__dict__.items() if not attr.startswith("__")]


DEFAULT_RUNNERS = (
    tf_graph_runner(),
    cfn_runner(),
    k8_runner(),
    sls_runner(),
    arm_runner(),
    tf_plan_runner(),
    helm_runner(),
    dockerfile_runner(),
    secrets_runner(),
    json_runner(),
    yaml_runner(),
    github_configuration_runner(),
    gitlab_configuration_runner(),
    gitlab_ci_runner(),
    bitbucket_configuration_runner(),
    bitbucket_pipelines_runner(),
    kustomize_runner(),
    github_actions_runner(),
    bicep_runner(),
    openapi_runner(),
    sca_image_runner(),
    argo_workflows_runner(),
    circleci_pipelines_runner(),
    azure_pipelines_runner(),
    sca_package_runner_2() if CHECKOV_RUN_SCA_PACKAGE_SCAN_V2 else sca_package_runner()
)


def exit_run(no_fail_on_crash: bool) -> None:
    exit(0) if no_fail_on_crash else exit(2)


def commit_repository(config: Namespace) -> Optional[str]:
    try:
        return bc_integration.commit_repository(config.branch)
    except Exception:
        logging.debug("commit_repository failed, exiting", exc_info=True)
        exit_run(config.no_fail_on_crash)
        return ""


def run(banner: str = checkov_banner, argv: List[str] = sys.argv[1:]) -> Optional[int]:
    default_config_paths = get_default_config_paths(sys.argv[1:])
    parser = ExtArgumentParser(description='Infrastructure as code static analysis',
                               default_config_files=default_config_paths,
                               config_file_parser_class=configargparse.YAMLConfigFileParser,
                               add_env_var_help=True)
    add_parser_args(parser)
    argcomplete.autocomplete(parser)
    config = parser.parse_args(argv)

    normalize_config(config, parser)

    run_metadata: dict[str, str | list[str]] = {
        "checkov_version": version,
        "python_executable": sys.executable,
        "python_version": sys.version,
        "checkov_executable": sys.argv[0],
        "args": parser.format_values(sanitize=True).split('\n')
    }

    logger.debug(f'Run metadata: {json.dumps(run_metadata, indent=2)}')

    if config.add_check:
        resp = prompt.Prompt()
        check = prompt.Check(resp.responses)
        check.action()
        return None

    # Check if --output value is None. If so, replace with ['cli'] for default cli output.
    if config.output is None:
        config.output = ['cli']

    if config.bc_api_key and not config.include_all_checkov_policies:
        if config.skip_download and not config.external_checks_dir:
            print('You are using an API key along with --skip-download but not --include-all-checkov-policies or --external-checks-dir. '
                  'With these arguments, Checkov cannot fetch metadata to determine what is a local Checkov-only '
                  'policy and what is a platform policy, so no policies will be evaluated. Please re-run Checkov '
                  'and either remove the --skip-download option, or use the --include-all-checkov-policies and / or '
                  '--external-checks-dir options.',
                  file=sys.stderr)
            exit_run(config.no_fail_on_crash)
        elif config.skip_download:
            print('You are using an API key along with --skip-download but not --include-all-checkov-policies. '
                  'With these arguments, Checkov cannot fetch metadata to determine what is a local Checkov-only '
                  'policy and what is a platform policy, so only local custom policies loaded with --external-checks-dir '
                  'will be evaluated.',
                  file=sys.stderr)
        else:
            logger.debug('Using API key and not --include-all-checkov-policies - only running platform policies '
                         '(this is the default behavior, and this message is just for debugging purposes)')

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
                                 skip_checks=config.skip_check, include_all_checkov_policies=config.include_all_checkov_policies,
                                 download_external_modules=bool(convert_str_to_bool(config.download_external_modules)),
                                 external_modules_download_path=config.external_modules_download_path,
                                 evaluate_variables=bool(convert_str_to_bool(config.evaluate_variables)),
                                 runners=checkov_runners, excluded_paths=excluded_paths,
                                 all_external=config.run_all_external_checks, var_files=config.var_file,
                                 skip_cve_package=config.skip_cve_package, show_progress_bar=not config.quiet,
                                 use_enforcement_rules=config.use_enforcement_rules,
                                 enable_secret_scan_all_files=bool(convert_str_to_bool(config.enable_secret_scan_all_files)),
                                 block_list_secret_scan=config.block_list_secret_scan,
                                 deep_analysis=config.deep_analysis,
                                 repo_root_for_plan_enrichment=config.repo_root_for_plan_enrichment)

    if outer_registry:
        runner_registry = outer_registry
        runner_registry.runner_filter = runner_filter
        runner_registry.filter_runner_framework()
    else:
        runner_registry = RunnerRegistry(banner, runner_filter, *DEFAULT_RUNNERS)

    runnerDependencyHandler = RunnerDependencyHandler(runner_registry)
    runnerDependencyHandler.validate_runner_deps()

    if config.show_config:
        print(parser.format_values(sanitize=True))
        return None

    if config.bc_api_key == '':
        parser.error('The --bc-api-key flag was specified but the value was blank. If this value was passed as a '
                     'secret, you may need to double check the mapping.')
    elif config.bc_api_key:
        logger.debug(f'Using API key ending with {config.bc_api_key[-8:]}')

        if not bc_integration.is_token_valid(config.bc_api_key):
            raise Exception('The provided API key does not appear to be a valid Bridgecrew API key or Prisma Cloud '
                            'access key and secret key. For Prisma, the value must be in the form '
                            'ACCESS_KEY::SECRET_KEY. For Bridgecrew, make sure to copy the token value from when you '
                            'created it, not the token ID visible later on. If you are using environment variables, '
                            'make sure they are properly set and exported.')

        if config.repo_id is None and not config.list:
            # if you are only listing policies, then the API key will be used to fetch policies, but that's it,
            # so the repo is not required
            parser.error("--repo-id argument is required when using --bc-api-key")
        elif config.repo_id:
            repo_id_sections = config.repo_id.split('/')
            if len(repo_id_sections) < 2 or any(len(section) == 0 for section in repo_id_sections):
                parser.error("--repo-id argument format should be 'organization/repository_name' E.g "
                             "bridgecrewio/checkov")

        source_env_val = os.getenv('BC_SOURCE', 'cli')
        source = get_source_type(source_env_val)
        if source == SourceTypes[BCSourceType.DISABLED]:
            logger.warning(
                f'Received unexpected value for BC_SOURCE: {source_env_val}; Should be one of {{{",".join(SourceTypes.keys())}}} setting source to DISABLED')
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
                                                        skip_download=config.skip_download,
                                                        source=source,
                                                        source_version=source_version,
                                                        repo_branch=config.branch,
                                                        prisma_api_url=config.prisma_api_url)

            should_run_contributor_metrics = source.report_contributor_metrics and config.repo_id and config.prisma_api_url
            logger.debug(f"Should run contributor metrics report: {should_run_contributor_metrics}")
            if should_run_contributor_metrics:
                try:        # collect contributor info and upload
                    report_contributor_metrics(config.repo_id, source.name, bc_integration)
                except Exception as e:
                    logger.warning(f"Unable to report contributor metrics due to: {e}")

        except MaxRetryError:
            exit_run(config.no_fail_on_crash)
        except Exception:
            if bc_integration.prisma_api_url:
                message = 'An error occurred setting up the Prisma Cloud platform integration. ' \
                          'Please check your Prisma Cloud API token and URL and try again.'
            else:
                message = 'An error occurred setting up the Bridgecrew platform integration. ' \
                          'Please check your API token and try again.'
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(message, exc_info=True)
            else:
                logger.error(message)
                logger.error('Please try setting the environment variable LOG_LEVEL=DEBUG and re-running the command, and provide the output to support', exc_info=True)
            exit_run(config.no_fail_on_crash)
    else:
        logger.debug('No API key found. Scanning locally only.')
        config.include_all_checkov_policies = True

    if config.check and config.skip_check:
        if any(item in runner_filter.checks for item in runner_filter.skip_checks):
            parser.error("The check ids specified for '--check' and '--skip-check' must be mutually exclusive.")
            return None

    BC_SKIP_MAPPING = os.getenv("BC_SKIP_MAPPING", "FALSE")
    if config.skip_download or BC_SKIP_MAPPING.upper() == "TRUE":
        bc_integration.skip_download = True

    try:
        bc_integration.get_platform_run_config()
    except Exception:
        if not config.include_all_checkov_policies:
            # stack trace gets printed in the exception handlers above
            # include_all_checkov_policies will always be set when there is no API key, so we don't need to worry about it here
            print('An error occurred getting data from the platform, including policy metadata. Because --include-all-checkov-policies '
                  'was not used, Checkov cannot differentiate Checkov-only policies from platform policies, and no '
                  'policies will get evaluated. Please resolve the error above or re-run with the --include-all-checkov-policies argument '
                  '(but note that this will not include any custom platform configurations or policy metadata).',
                  file=sys.stderr)
            exit_run(config.no_fail_on_crash)

    bc_integration.get_prisma_build_policies(config.policy_metadata_filter)

    integration_feature_registry.run_pre_scan()

    runner_filter.run_image_referencer = licensing_integration.should_run_image_referencer()

    runner_filter.filtered_policy_ids = policy_metadata_integration.filtered_policy_ids
    logger.debug(f"Filtered list of policies: {runner_filter.filtered_policy_ids}")

    runner_filter.excluded_paths = runner_filter.excluded_paths + list(repo_config_integration.skip_paths)

    runner_filter.set_suppressed_policies(suppressions_integration.get_policy_level_suppressions())

    if config.use_enforcement_rules:
        runner_filter.apply_enforcement_rules(repo_config_integration.code_category_configs)

    if config.list:
        print_checks(frameworks=config.framework, use_bc_ids=config.output_bc_ids,
                     include_all_checkov_policies=config.include_all_checkov_policies, filtered_policy_ids=runner_filter.filtered_policy_ids)
        return None

    baseline = None
    if config.baseline:
        baseline = Baseline(config.output_baseline_as_skipped)
        baseline.from_json(config.baseline)

    external_checks_dir = get_external_checks_dir(config)
    url = None
    created_baseline_path = None

    default_github_dir_path = os.getcwd() + '/' + os.getenv('CKV_GITLAB_CONF_DIR_NAME', 'github_conf')
    git_configuration_folders = [os.getenv("CKV_GITHUB_CONF_DIR_PATH", default_github_dir_path),
                                 os.getcwd() + '/' + os.getenv('CKV_GITLAB_CONF_DIR_NAME', 'gitlab_conf')]

    if config.directory:
        exit_codes = []
        for root_folder in config.directory:
            if not os.path.exists(root_folder):
                logger.error(f'Directory {root_folder} does not exist; skipping it')
                continue
            file = config.file
            scan_reports = runner_registry.run(root_folder=root_folder, external_checks_dir=external_checks_dir,
                                               files=file)
            if runner_registry.is_error_in_reports(scan_reports):
                exit_run(config.no_fail_on_crash)
            if baseline:
                baseline.compare_and_reduce_reports(scan_reports)
            if bc_integration.is_integration_configured():
                bc_integration.persist_repository(root_folder, excluded_paths=runner_filter.excluded_paths, included_paths=[config.external_modules_download_path])
                bc_integration.persist_git_configuration(os.getcwd(), git_configuration_folders)
                bc_integration.persist_scan_results(scan_reports)
                bc_integration.persist_run_metadata(run_metadata)
                url = commit_repository(config)

            if config.create_baseline:
                overall_baseline = Baseline()
                for report in scan_reports:
                    overall_baseline.add_findings_from_report(report)
                created_baseline_path = os.path.join(os.path.abspath(root_folder), '.checkov.baseline')
                with open(created_baseline_path, 'w') as f:
                    json.dump(overall_baseline.to_dict(), f, indent=4)
            exit_codes.append(runner_registry.print_reports(scan_reports, config, url=url,
                                                            created_baseline_path=created_baseline_path,
                                                            baseline=baseline))
        exit_code = 1 if 1 in exit_codes else 0
        return exit_code
    elif config.docker_image:
        if config.bc_api_key is None:
            parser.error("--bc-api-key argument is required when using --docker-image")
            return None
        if config.dockerfile_path is None:
            parser.error("--dockerfile-path argument is required when using --docker-image")
            return None
        if config.branch is None:
            parser.error("--branch argument is required when using --docker-image")
            return None
        files = [os.path.abspath(config.dockerfile_path)]
        runner = sca_image_runner()
        result = runner.run(
            root_folder='',
            image_id=config.docker_image,
            dockerfile_path=config.dockerfile_path,
            runner_filter=runner_filter,
        )
        results = result if isinstance(result, list) else [result]
        if runner_registry.is_error_in_reports(results):
            exit_run(config.no_fail_on_crash)
        if len(results) > 1:
            # this shouldn't happen, but if it happens, then it is intended or something is broke
            logger.error(f"SCA image runner returned {len(results)} reports; expected 1")

        integration_feature_registry.run_post_runner(results[0])
        bc_integration.persist_repository(os.path.dirname(config.dockerfile_path), files=files)
        bc_integration.persist_scan_results(results)
        bc_integration.persist_image_scan_results(runner.raw_report, config.dockerfile_path, config.docker_image,
                                                  config.branch)
        bc_integration.persist_run_metadata(run_metadata)
        url = commit_repository(config)
        exit_code = runner_registry.print_reports(results, config, url=url)
        return exit_code
    elif config.file:
        runner_registry.filter_runners_for_files(config.file)
        scan_reports = runner_registry.run(external_checks_dir=external_checks_dir, files=config.file,
                                           repo_root_for_plan_enrichment=config.repo_root_for_plan_enrichment)
        if runner_registry.is_error_in_reports(scan_reports):
            exit_run(config.no_fail_on_crash)
        if baseline:
            baseline.compare_and_reduce_reports(scan_reports)
        if config.create_baseline:
            overall_baseline = Baseline()
            for report in scan_reports:
                overall_baseline.add_findings_from_report(report)
            created_baseline_path = os.path.join(os.path.abspath(os.path.commonprefix(config.file)),
                                                 '.checkov.baseline')
            with open(created_baseline_path, 'w') as f:
                json.dump(overall_baseline.to_dict(), f, indent=4)

        if bc_integration.is_integration_configured():
            files = [os.path.abspath(file) for file in config.file]
            root_folder = os.path.split(os.path.commonprefix(files))[0]
            bc_integration.persist_repository(root_folder, files, excluded_paths=runner_filter.excluded_paths)
            bc_integration.persist_git_configuration(os.getcwd(), git_configuration_folders)
            bc_integration.persist_scan_results(scan_reports)
            bc_integration.persist_run_metadata(run_metadata)
            url = commit_repository(config)
        exit_code = runner_registry.print_reports(scan_reports, config, url=url, created_baseline_path=created_baseline_path, baseline=baseline)
        return exit_code
    elif not config.quiet:
        print(f"{banner}")

        bc_integration.onboarding()
    return None


def add_parser_args(parser: ArgumentParser) -> None:
    parser.add('-v', '--version',
               help='version', action='version', version=version)
    parser.add('-d', '--directory', action='append',
               help='IaC root directory (can not be used together with --file).')
    parser.add('--add-check', action='store_true', help="Generate a new check via CLI prompt")
    parser.add('-f', '--file', action='append',
               help='File to scan (can not be used together with --directory). With this option, Checkov will attempt '
                    'to filter the runners based on the file type. For example, if you specify a ".tf" file, only the '
                    'terraform and secrets frameworks will be included. You can further limit this (e.g., skip secrets) '
                    'by using the --skip-framework argument.')
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
               help='Report output format. Add multiple outputs by using the flag multiple times (-o sarif -o cli)')
    parser.add('--output-file-path', default=None,
               help='Name of the output folder to save the chosen output formats. '
                    'Advanced usage: '
                    'By using -o cli -o junitxml --output-file-path console,results.xml the CLI output will be printed '
                    'to the console and the JunitXML output to the file results.xml.'
               )
    parser.add('--output-bc-ids', action='store_true',
               help='Print Bridgecrew platform IDs (BC...) instead of Checkov IDs (CKV...), if the check exists in the platform')
    parser.add('--include-all-checkov-policies', action='store_true',
               help='When running with an API key, Checkov will omit any policies that do not exist '
                    'in the Bridgecrew or Prisma Cloud platform, except for local custom policies loaded with the '
                    '--external-check flags. Use this key to include policies that only exist in Checkov in the scan. '
                    'Note that this will make the local CLI results different from the results you see in the '
                    'platform. Has no effect if you are not using an API key. Use the --check option to explicitly '
                    'include checks by ID even if they are not in the platform, without using this flag.')
    parser.add('--quiet', action='store_true',
               default=False,
               help='in case of CLI output, display only failed checks. Also disables progress bars')
    parser.add('--compact', action='store_true',
               default=False,
               help='in case of CLI output, do not display code blocks')
    parser.add('--framework',
               help='Filter scan to run only on specific infrastructure code frameworks',
               choices=checkov_runners + ["all"],
               default=["all"],
               env_var='CKV_FRAMEWORK',
               nargs="+")
    parser.add('--skip-framework',
               help='Filter scan to skip specific infrastructure as code frameworks.'
                    'This will be included automatically for some frameworks if system dependencies '
                    'are missing. Add multiple frameworks using spaces. For example, '
                    '--skip-framework terraform sca_package.',
               choices=checkov_runners,
               default=None,
               nargs="+")
    parser.add('-c', '--check',
               help='Checks to run; any other checks will be skipped. Enter one or more items separated by commas. '
                    'Each item may be either a Checkov check ID (CKV_AWS_123), a BC check ID (BC_AWS_GENERAL_123), or '
                    'a severity (LOW, MEDIUM, HIGH, CRITICAL). If you use a severity, then all checks equal to or '
                    'above the lowest severity in the list will be included. This option can be combined with '
                    '--skip-check. If it is, then the logic is to first take all checks that match this list, and then '
                    'remove all checks that match the skip list. For example, if you use --check CKV_123 and '
                    '--skip-check LOW, then CKV_123 will not run if it is a LOW severity. Similarly, if you use '
                    '--check CKV_789 --skip-check MEDIUM, then CKV_789 will run if it is a HIGH severity. If you use a '
                    'check ID here along with an API key, and the check is not part of the BC / PC platform, then the '
                    'check will still be run (see --include-all-checkov-policies for more info).',
               action='append', default=None,
               env_var='CKV_CHECK')
    parser.add('--skip-check',
               help='Checks to skip; any other checks will not be run. Enter one or more items separated by commas. '
                    'Each item may be either a Checkov check ID (CKV_AWS_123), a BC check ID (BC_AWS_GENERAL_123), or '
                    'a severity (LOW, MEDIUM, HIGH, CRITICAL). If you use a severity, then all checks equal to or '
                    'below the highest severity in the list will be skipped. This option can be combined with --check. '
                    'If it is, priority is given to checks explicitly listed by ID or wildcard over checks listed by '
                    'severity. For example, if you use --skip-check CKV_123 and --check HIGH, then CKV_123 will be '
                    'skipped even if it is a HIGH severity. In the case of a tie (e.g., --check MEDIUM and '
                    '--skip-check HIGH for a medium severity check), then the check will be skipped.',
               action='append', default=None,
               env_var='CKV_SKIP_CHECK')
    parser.add('--run-all-external-checks', action='store_true',
               help='Run all external checks (loaded via --external-checks options) even if the checks are not present '
                    'in the --check list. This allows you to always ensure that new checks present in the external '
                    'source are used. If an external check is included in --skip-check, it will still be skipped.')
    parser.add('-s', '--soft-fail',
               help='Runs checks but always returns a 0 exit code. Using either --soft-fail-on and / or --hard-fail-on '
                    'overrides this option, except for the case when a result does not match either of the soft fail '
                    'or hard fail criteria, in which case this flag determines the result.', action='store_true')
    parser.add('--soft-fail-on',
               help='Exits with a 0 exit code if only the specified items fail. Enter one or more items '
                    'separated by commas. Each item may be either a Checkov check ID (CKV_AWS_123), a BC '
                    'check ID (BC_AWS_GENERAL_123), or a severity (LOW, MEDIUM, HIGH, CRITICAL). If you use '
                    'a severity, then any severity equal to or less than the highest severity in the list '
                    'will result in a soft fail. This option may be used with --hard-fail-on, using the same '
                    'priority logic described in --check and --skip-check options above, with --hard-fail-on '
                    'taking precedence in a tie. If a given result does not meet the --soft-fail-on nor '
                    'the --hard-fail-on criteria, then the default is to hard fail',
               action='append',
               default=None)
    parser.add('--hard-fail-on',
               help='Exits with a non-zero exit code for specified checks. Enter one or more items '
                    'separated by commas. Each item may be either a Checkov check ID (CKV_AWS_123), a BC '
                    'check ID (BC_AWS_GENERAL_123), or a severity (LOW, MEDIUM, HIGH, CRITICAL). If you use a '
                    'severity, then any severity equal to or greater than the lowest severity in the list will '
                    'result in a hard fail. This option can be used with --soft-fail-on, using the same '
                    'priority logic described in --check and --skip-check options above, with --hard-fail-on '
                    'taking precedence in a tie.',
               action='append',
               default=None)
    parser.add('--bc-api-key', env_var='BC_API_KEY', sanitize=True,
               help='Bridgecrew API key or Prisma Cloud Access Key (see --prisma-api-url)')
    parser.add('--prisma-api-url', env_var='PRISMA_API_URL', default=None,
               help='The Prisma Cloud API URL (see: https://prisma.pan.dev/api/cloud/api-urls). '
                    'Requires --bc-api-key to be a Prisma Cloud Access Key in the following format: <access_key_id>::<secret_key>')
    parser.add('--docker-image', help='Scan docker images by name or ID. Only works with --bc-api-key flag')
    parser.add('--dockerfile-path', help='Path to the Dockerfile of the scanned docker image')
    parser.add('--repo-id',
               help='Identity string of the repository, with form <repo_owner>/<repo_name>')
    parser.add('-b', '--branch',
               help="Selected branch of the persisted repository. Only has effect when using the --bc-api-key flag",
               default='master')
    parser.add('--skip-download',
               help='Do not download any data from Bridgecrew. This will omit doc links, severities, etc., as well as '
                    'custom policies and suppressions if using an API token. Note: it will prevent BC platform IDs from '
                    'being available in Checkov.',
               action='store_true')
    parser.add('--use-enforcement-rules', action='store_true',
               help='Use the Enforcement rules configured in the platform for hard / soft fail logic. With this option, '
                    'the enforcement rule matching this repo, or the default rule if there is no match, will determine '
                    'this behavior: any check with a severity below the selected rule\'s soft-fail threshold will be '
                    'skipped; any check with a severity equal to or greater than the rule\'s hard-fail threshold will '
                    'be part of the hard-fail list, and any check in between will be part of the soft-fail list. For '
                    'example, if the given enforcement rule has a hard-fail value of HIGH and a soft-fail value of MEDIUM,'
                    'this is the equivalent of using the flags `--skip-check LOW --hard-fail-on HIGH`. You can use --check, '
                    '--skip-check, --soft-fail, --soft-fail-on, or --hard-fail-on to override portions of an enforcement rule. '
                    'Note, however, that the logic of applying the --check list and then the --skip-check list (as described '
                    'above under --check) still applies here. Requires a BC or PC platform API key.')
    parser.add('--no-guide', action='store_true',
               default=False,
               help='Deprecated - use --skip-download')
    parser.add('--skip-suppressions',
               help='Deprecated - use --skip-download',
               action='store_true')
    parser.add('--skip-policy-download',
               help='Deprecated - use --skip-download',
               action='store_true')
    parser.add('--skip-fixes',
               help='Do not download fixed resource templates from Bridgecrew. Only has effect when using the API key.',
               action='store_true')
    parser.add('--download-external-modules',
               help="download external terraform modules from public git repositories and terraform registry",
               default=os.environ.get('DOWNLOAD_EXTERNAL_MODULES', False), env_var='DOWNLOAD_EXTERNAL_MODULES')
    parser.add('--var-file', action='append',
               help='Variable files to load in addition to the default files (see '
                    'https://www.terraform.io/docs/language/values/variables.html#variable-definitions-tfvars-files).'
                    'Currently only supported for source Terraform (.tf file), and Helm chart scans.'
                    'Requires using --directory, not --file.')
    parser.add('--external-modules-download-path',
               help="set the path for the download external terraform modules",
               default=DEFAULT_EXTERNAL_MODULES_DIR, env_var='EXTERNAL_MODULES_DIR')
    parser.add('--evaluate-variables',
               help="evaluate the values of variables and locals",
               env_var="CKV_EVAL_VARS",
               default=True)
    parser.add('-ca', '--ca-certificate',
               help='Custom CA certificate (bundle) file', default=None, env_var='BC_CA_BUNDLE')
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
    parser.add(
        '--baseline',
        help=(
            "Use a .checkov.baseline file to compare current results with a known baseline. "
            "Report will include only failed checks that are new with respect to the provided baseline"
        ),
        default=None,
    )
    parser.add(
        '--output-baseline-as-skipped',
        help="output checks that are skipped due to baseline file presence",
        action='store_true',
        default=False,
    )
    parser.add('--skip-cve-package',
               help='filter scan to run on all packages but a specific package identifier (denylist), You can '
                    'specify this argument multiple times to skip multiple packages', action='append', default=None)
    parser.add('--policy-metadata-filter',
               help='comma separated key:value string to filter policies based on Prisma Cloud policy metadata. '
                    'See https://prisma.pan.dev/api/cloud/cspm/policy#operation/get-policy-filters-and-options for '
                    'information on allowed filters. Format: policy.label=test,cloud.type=aws ', default=None)
    parser.add('--secrets-scan-file-type',
               default=[],
               env_var='CKV_SECRETS_SCAN_FILE_TYPE',
               action='append',
               help='not in use')
    parser.add('--enable-secret-scan-all-files',
               default=False,
               env_var='CKV_SECRETS_SCAN_ENABLE_ALL',
               action='store_true',
               help='enable secret scan for all files')
    parser.add('--block-list-secret-scan',
               default=[],
               env_var='CKV_SECRETS_SCAN_BLOCK_LIST',
               action='append',
               help='List of files to filter out from the secret scanner')
    parser.add('--summary-position', default='top', choices=SUMMARY_POSITIONS,
               help='Chose whether the summary will be appended on top (before the checks results) or on bottom '
                    '(after check results), default is on top.')
    parser.add('--skip-resources-without-violations',
               help="exclude extra resources (resources without violations) from report output",
               action='store_true',
               env_var='CKV_SKIP_RESOURCES_WITHOUT_VIOLATIONS')
    parser.add('--deep-analysis',
               default=False,
               action='store_true',
               help='Enable combine tf graph and rf plan graph')
    parser.add('--no-fail-on-crash',
               default=False,
               env_var='CKV_NO_FAIL_ON_CRASH',
               action='store_true',
               help='Return exit code 0 instead of 2')


def get_external_checks_dir(config: Any) -> Any:
    external_checks_dir = config.external_checks_dir
    if config.external_checks_git:
        git_getter = GitGetter(config.external_checks_git[0])
        external_checks_dir = [git_getter.get()]
        atexit.register(shutil.rmtree, str(Path(external_checks_dir[0]).parent))
    return external_checks_dir


def normalize_config(config: Namespace, parser: ExtArgumentParser) -> None:
    if config.no_guide:
        logger.warning('--no-guide is deprecated and will be removed in a future release. Use --skip-download instead')
        config.skip_download = True
    if config.skip_suppressions:
        logger.warning('--skip-suppressions is deprecated and will be removed in a future release. Use --skip-download instead')
        config.skip_download = True
    if config.skip_policy_download:
        logger.warning('--skip-policy-download is deprecated and will be removed in a future release. Use --skip-download instead')
        config.skip_download = True

    elif not config.bc_api_key and not config.include_all_checkov_policies:
        # makes it easier to pick out policies later if we can just always rely on this flag without other context
        logger.debug('No API key present; setting include_all_checkov_policies to True')
        config.include_all_checkov_policies = True

    if config.use_enforcement_rules and not config.bc_api_key:
        parser.error('Must specify an API key with --use-enforcement-rules')

    if config.policy_metadata_filter and not (config.bc_api_key and config.prisma_api_url):
        logger.warning('--policy-metadata-filter flag was used without a Prisma Cloud API key. Policy filtering will be skipped.')


if __name__ == '__main__':
    sys.exit(run())
