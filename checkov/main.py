#!/usr/bin/env python
from __future__ import annotations

import atexit
import itertools
import json
import logging
import os
import platform
import shutil
import signal
import sys
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, List, Set

import argcomplete
import configargparse
from urllib3.exceptions import MaxRetryError

import checkov.logging_init  # noqa  # should be imported before the others to ensure correct logging setup
from checkov.ansible.runner import Runner as ansible_runner
from checkov.argo_workflows.runner import Runner as argo_workflows_runner
from checkov.arm.runner import Runner as arm_runner
from checkov.azure_pipelines.runner import Runner as azure_pipelines_runner
from checkov.bicep.runner import Runner as bicep_runner
from checkov.bitbucket.runner import Runner as bitbucket_configuration_runner
from checkov.bitbucket_pipelines.runner import Runner as bitbucket_pipelines_runner
from checkov.cdk.runner import CdkRunner
from checkov.circleci_pipelines.runner import Runner as circleci_pipelines_runner
from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.bridgecrew.bc_source import SourceTypes, BCSourceType, get_source_type, SourceType
from checkov.common.bridgecrew.check_type import checkov_runners, CheckType
from checkov.common.bridgecrew.platform_errors import ModuleNotEnabledError, PlatformConnectionError
from checkov.common.bridgecrew.integration_features.features.custom_policies_integration import \
    integration as custom_policies_integration
from checkov.common.bridgecrew.integration_features.features.licensing_integration import \
    integration as licensing_integration
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import \
    integration as policy_metadata_integration
from checkov.common.bridgecrew.integration_features.features.repo_config_integration import \
    integration as repo_config_integration
from checkov.common.bridgecrew.integration_features.features.suppressions_integration import \
    integration as suppressions_integration
from checkov.common.bridgecrew.integration_features.integration_feature_registry import integration_feature_registry
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.severities import BcSeverities
from checkov.common.goget.github.get_git import GitGetter
from checkov.common.logger_streams import logger_streams
from checkov.common.output.baseline import Baseline
from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.sast.consts import SastLanguages
from checkov.common.typing import LibraryGraph
from checkov.common.util import prompt
from checkov.common.util.banner import banner as checkov_banner, default_tool as default_tool
from checkov.common.util.config_utils import get_default_config_paths
from checkov.common.util.ext_argument_parser import ExtArgumentParser, flatten_csv
from checkov.common.util.runner_dependency_handler import RunnerDependencyHandler
from checkov.common.util.type_forcers import convert_str_to_bool
from checkov.common.util.env_vars_config import env_vars_config
from checkov.contributor_metrics import report_contributor_metrics
from checkov.dockerfile.runner import Runner as dockerfile_runner
from checkov.docs_generator import print_checks
from checkov.github.runner import Runner as github_configuration_runner
from checkov.github_actions.runner import Runner as github_actions_runner
from checkov.gitlab.runner import Runner as gitlab_configuration_runner
from checkov.gitlab_ci.runner import Runner as gitlab_ci_runner
from checkov.helm.runner import Runner as helm_runner
from checkov.json_doc.runner import Runner as json_runner
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.kustomize.runner import Runner as kustomize_runner
from checkov.logging_init import log_stream as logs_stream
from checkov.openapi.runner import Runner as openapi_runner
from checkov.runner_filter import RunnerFilter
from checkov.common.sast.report_types import serialize_reachability_report
from checkov.sast.report import SastData, SastReport
from checkov.sast.runner import Runner as sast_runner
from checkov.sca_image.runner import Runner as sca_image_runner
from checkov.sca_package_2.runner import Runner as sca_package_runner_2
from checkov.secrets.runner import Runner as secrets_runner
from checkov.serverless.runner import Runner as sls_runner
from checkov.terraform.plan_runner import Runner as tf_plan_runner
from checkov.terraform.runner import Runner as tf_graph_runner
from checkov.terraform_json.runner import TerraformJsonRunner
from checkov.version import version
from checkov.yaml_doc.runner import Runner as yaml_runner

if TYPE_CHECKING:
    from checkov.common.output.report import Report
    from checkov.common.runners.base_runner import BaseRunner
    from configargparse import Namespace

signal.signal(signal.SIGINT, lambda x, y: sys.exit(''))

outer_registry = None

logger = logging.getLogger(__name__)
add_resource_code_filter_to_logger(logger)

# sca package runner added during the run method
DEFAULT_RUNNERS: "list[BaseRunner[Any, Any, Any]]" = [
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
    sca_package_runner_2(),
    argo_workflows_runner(),
    circleci_pipelines_runner(),
    azure_pipelines_runner(),
    ansible_runner(),
    TerraformJsonRunner(),
    sast_runner(),
    CdkRunner(),
]


class Checkov:
    def __init__(self, argv: list[str] = sys.argv[1:]) -> None:
        self.config: "Namespace"  # set in 'parse_config()'
        self.parser: "ExtArgumentParser"  # set in 'parse_config()'
        self.runners = DEFAULT_RUNNERS.copy()
        self.scan_reports: "list[Report]" = []
        self.run_metadata: dict[str, str | list[str]] = {}
        self.graphs: dict[str, list[tuple[LibraryGraph, Optional[str]]]] = {}
        self.resource_subgraph_maps: dict[str, dict[str, str]] = {}
        self.url: str | None = None
        self.sast_data: SastData = SastData()

        self.parse_config(argv=argv)

    def _parse_mask_to_resource_attributes_to_omit(self) -> None:
        resource_attributes_to_omit = defaultdict(set)
        for entry in self.config.mask:
            splitted_entry = entry.split(':')
            # if we have 2 entries, this is resource & variable to mask
            splitted_entry_len = len(splitted_entry)
            if 2 == splitted_entry_len:
                resource = splitted_entry[0]
                variables_to_mask = splitted_entry[1].split(',')
                resource_attributes_to_omit[resource].update(variables_to_mask)
            # ToDo: Uncomment if we want to support universal masking
            # elif 1 == splitted_entry_len:
            #     variables_to_mask = splitted_entry[0].split(',')
            #     resource_attributes_to_omit[RESOURCE_ATTRIBUTES_TO_OMIT_UNIVERSAL_MASK].update(variables_to_mask)

        self.config.mask = resource_attributes_to_omit

    def parse_config(self, argv: list[str] = sys.argv[1:]) -> None:
        """Parses the user-defined config via CLI flags and handles missing config-file"""

        default_config_paths = get_default_config_paths(sys.argv[1:])
        self.parser = ExtArgumentParser(
            description='Infrastructure as code static analysis',
            default_config_files=default_config_paths,
            config_file_parser_class=configargparse.YAMLConfigFileParser,
            add_env_var_help=True,
        )
        self.parser.add_parser_args()
        argcomplete.autocomplete(self.parser)

        # Pre-validate the config-file argument
        if env_vars_config.ENABLE_CONFIG_FILE_VALIDATION:
            for i, arg in enumerate(argv):
                if arg == "--config-file" and i + 1 < len(argv):
                    config_path = Path(argv[i + 1])
                    if not config_path.is_file():
                        logger.debug(f"The config file at '{config_path}' does not exist. Running without a config file.")
                        argv[i + 1] = ""  # Clear the non-existent file from arguments

        self.config = self.parser.parse_args(argv)
        self.normalize_config()

    def normalize_config(self) -> None:
        if not self.config.bc_api_key and not self.config.include_all_checkov_policies:
            # makes it easier to pick out policies later if we can just always rely on this flag without other context
            logger.debug('No API key present; setting include_all_checkov_policies to True')
            self.config.include_all_checkov_policies = True

        if self.config.use_enforcement_rules and not self.config.bc_api_key:
            self.parser.error('Must specify an API key with --use-enforcement-rules')

        if self.config.bc_api_key and not self.config.repo_id and not self.config.list:
            self.parser.error('--repo-id is required when using a platform API key')

        if (self.config.policy_metadata_filter or self.config.policy_metadata_filter_exception) and not (self.config.bc_api_key and self.config.prisma_api_url):
            logger.warning(
                '--policy-metadata-filter or --policy-metadata-filter-exception flag was used without a Prisma Cloud API key. Policy filtering will be skipped.'
            )

        logging.debug('Normalizing --framework')
        self.config.framework = self.normalize_framework_arg(self.config.framework, handle_all=True)
        logging.debug(f'Normalized --framework value: {self.config.framework}')

        logging.debug('Normalizing --skip-framework')
        self.config.skip_framework = self.normalize_framework_arg(self.config.skip_framework)
        logging.debug(f'Normalized --skip-framework value: {self.config.skip_framework}')

        duplicate_frameworks = set(self.config.skip_framework).intersection(self.config.framework)
        if duplicate_frameworks:
            self.parser.error(f'Frameworks listed for both --framework and --skip-framework: {", ".join(duplicate_frameworks)}')

        # Parse mask into json with default dict. If self.config.mask is empty list, default dict will be assigned
        self._parse_mask_to_resource_attributes_to_omit()

        if self.config.file:
            # it is passed as a list of lists
            self.config.file = list(itertools.chain.from_iterable(self.config.file))

    def normalize_framework_arg(self, raw_framework_arg: List[List[str]], handle_all: bool = False) -> List[str]:
        # frameworks come as arrays of arrays, e.g. --framework terraform arm --framework bicep,cloudformation
        # becomes: [['terraform', 'arm'], ['bicep,cloudformation']]
        # we'll collapse it into a single array (which is how it was before checkov3)

        if raw_framework_arg:
            logging.debug(f'Raw framework value: {raw_framework_arg}')
            frameworks = flatten_csv(raw_framework_arg)
            logging.debug(f'Flattened frameworks: {frameworks}')
            if handle_all and 'all' in frameworks:
                return ['all']
            else:
                invalid = list(filter(lambda f: f not in checkov_runners, frameworks))
                if invalid:
                    self.parser.error(f'Invalid frameworks specified: {", ".join(invalid)}.{os.linesep}'
                                      f'Valid values are: {", ".join(checkov_runners + ["all"] if handle_all else [])}')
                return frameworks
        elif handle_all:
            logging.debug('No framework specified; setting to `all`')
            return ['all']
        else:
            logging.debug('No framework specified; setting to none')
            return []

    def run(self, banner: str = checkov_banner, tool: str = default_tool, source_type: SourceType | None = None) -> int | None:
        self.run_metadata = {
            "checkov_version": version,
            "python_executable": sys.executable,
            "python_version": sys.version,
            "checkov_executable": sys.argv[0],
            "args": self.parser.format_values(sanitize=True).split('\n'),
            "OS_system_info": platform.platform(),
            "CPU_architecture": platform.processor(),
            "Python_implementation": platform.python_implementation()
        }

        logger.debug(f'Run metadata: {json.dumps(self.run_metadata, indent=2)}')

        if self.config.custom_tool_name:  # if the user specifies a tool name, use that
            tool = self.config.custom_tool_name
        try:
            if self.config.add_check:
                resp = prompt.Prompt()
                check = prompt.Check(resp.responses)
                check.action()
                return None

            # Check if --output value is None. If so, replace with ['cli'] for default cli output.
            if self.config.output is None:
                self.config.output = ['cli']

            if self.config.support:
                bc_integration.support_flag_enabled = True

            if self.config.bc_api_key and not self.config.include_all_checkov_policies:
                if self.config.skip_download and not self.config.external_checks_dir:
                    print('You are using an API key along with --skip-download but not --include-all-checkov-policies or --external-checks-dir. '
                          'With these arguments, Checkov cannot fetch metadata to determine what is a local Checkov-only '
                          'policy and what is a platform policy, so no policies will be evaluated. Please re-run Checkov '
                          'and either remove the --skip-download option, or use the --include-all-checkov-policies and / or '
                          '--external-checks-dir options.',
                          file=sys.stderr)
                    self.exit_run()
                elif self.config.skip_download:
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
            bc_integration.setup_http_manager(self.config.ca_certificate, self.config.no_cert_verify)

            # if a repo is passed in it'll save it.  Otherwise a default will be created based on the file or dir
            self.config.repo_id = bc_integration.persist_repo_id(self.config)
            # if a bc_api_key is passed it'll save it.  Otherwise it will check ~/.bridgecrew/credentials
            self.config.bc_api_key = bc_integration.persist_bc_api_key(self.config)

            if not self.config.bc_api_key:
                # check, if someone tries to use a severity filter without an API key
                severities = {severity for severity in BcSeverities.__dict__.values() if isinstance(severity, str)}
                if (
                    (self.config.check and any(check in severities for check in self.config.check))
                    or (self.config.skip_check and any(check in severities for check in self.config.skip_check))
                ):
                    logging.warning("Filtering checks by severity is only possible with an API key")

            excluded_paths = self.config.skip_path or []

            if self.config.var_file:
                self.config.var_file = [os.path.abspath(f) for f in self.config.var_file]

            runner_filter = RunnerFilter(
                framework=self.config.framework,
                skip_framework=self.config.skip_framework,
                checks=self.config.check,
                skip_checks=self.config.skip_check,
                include_all_checkov_policies=self.config.include_all_checkov_policies,
                download_external_modules=bool(convert_str_to_bool(self.config.download_external_modules)),
                external_modules_download_path=self.config.external_modules_download_path,
                evaluate_variables=bool(convert_str_to_bool(self.config.evaluate_variables)),
                runners=checkov_runners,
                excluded_paths=excluded_paths,
                all_external=self.config.run_all_external_checks,
                var_files=self.config.var_file,
                skip_cve_package=self.config.skip_cve_package,
                show_progress_bar=not self.config.quiet,
                use_enforcement_rules=self.config.use_enforcement_rules,
                enable_secret_scan_all_files=bool(convert_str_to_bool(self.config.enable_secret_scan_all_files)),
                block_list_secret_scan=self.config.block_list_secret_scan,
                deep_analysis=self.config.deep_analysis,
                repo_root_for_plan_enrichment=self.config.repo_root_for_plan_enrichment,
                resource_attr_to_omit=self.config.mask,
                enable_git_history_secret_scan=self.config.scan_secrets_history,
                git_history_timeout=self.config.secrets_history_timeout,
                report_sast_imports=bool(convert_str_to_bool(os.getenv('CKV_ENABLE_UPLOAD_SAST_IMPORTS', False))),
                report_sast_reachability=bool(convert_str_to_bool(os.getenv('CKV_ENABLE_UPLOAD_SAST_REACHABILITY', False)))
            )

            source_env_val = os.getenv('BC_SOURCE', 'cli')
            source = source_type if source_type else get_source_type(source_env_val)
            if source == SourceTypes[BCSourceType.DISABLED]:
                logger.warning(
                    f'Received unexpected value for BC_SOURCE: {source_env_val}; Should be one of {{{",".join(SourceTypes.keys())}}} setting source to DISABLED')
            source_version = os.getenv('BC_SOURCE_VERSION', version)
            logger.debug(f'BC_SOURCE = {source.name}, version = {source_version}')

            if self.config.list:
                # This speeds up execution by not setting up upload credentials (since we won't upload anything anyways)
                logger.debug('Using --list; setting source to DISABLED')
                source = SourceTypes[BCSourceType.DISABLED]

            if outer_registry:
                runner_registry = outer_registry
                runner_registry.runner_filter = runner_filter
                runner_registry.filter_runner_framework()
            else:
                runner_registry = RunnerRegistry(banner, runner_filter, *self.runners, tool=tool)

            runnerDependencyHandler = RunnerDependencyHandler(runner_registry)
            runnerDependencyHandler.validate_runner_deps()

            if self.config.show_config:
                print(self.parser.format_values(sanitize=True))
                return None

            if self.config.bc_api_key == '':
                self.parser.error(
                    'The --bc-api-key flag was specified but the value was blank. If this value was passed as a '
                    'secret, you may need to double check the mapping.'
                )
            elif self.config.bc_api_key:
                logger.debug(f'Using API key ending with {self.config.bc_api_key[-8:]}')

                if not bc_integration.is_token_valid(self.config.bc_api_key):
                    raise Exception('The provided API key does not appear to be a valid Bridgecrew API key or Prisma Cloud '
                                    'access key and secret key. For Prisma, the value must be in the form '
                                    'ACCESS_KEY::SECRET_KEY. For Bridgecrew, make sure to copy the token value from when you '
                                    'created it, not the token ID visible later on. If you are using environment variables, '
                                    'make sure they are properly set and exported.')

                if not self.config.list:
                    # if you are only listing policies, then the API key will be used to fetch policies, but that's it,
                    # so the repo is not required and ignored
                    if self.config.repo_id is None:
                        self.parser.error("--repo-id argument is required when using --bc-api-key")
                    else:
                        repo_id_sections = self.config.repo_id.split('/')
                        if len(repo_id_sections) < 2 or any(len(section) == 0 for section in repo_id_sections):
                            self.parser.error(
                                "--repo-id argument format should be 'organization/repository_name' E.g "
                                "bridgecrewio/checkov"
                            )

                try:
                    bc_integration.bc_api_key = self.config.bc_api_key
                    bc_integration.api_url = 'https://www.bridgecrew.cloud'
                    bc_integration.setup_bridgecrew_credentials(repo_id=self.config.repo_id,
                                                                skip_fixes=False,  # will be set to True if this run is not eligible for fixes
                                                                skip_download=self.config.skip_download,
                                                                source=source,
                                                                source_version=source_version,
                                                                repo_branch=self.config.branch,
                                                                prisma_api_url=self.config.prisma_api_url)

                except MaxRetryError:
                    self.exit_run()
                except PlatformConnectionError:
                    self.exit_run()
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
                    self.exit_run()
            else:
                if bc_integration.support_flag_enabled:
                    logger.warning("--bc-api-key argument is required when using --support")
                logger.debug('No API key found. Scanning locally only.')
                self.config.include_all_checkov_policies = True

            if self.config.check and self.config.skip_check:
                if any(item in runner_filter.checks for item in runner_filter.skip_checks):
                    self.parser.error("The check ids specified for '--check' and '--skip-check' must be mutually exclusive.")
                    return None

            BC_SKIP_MAPPING = os.getenv("BC_SKIP_MAPPING", "FALSE")
            if self.config.skip_download or BC_SKIP_MAPPING.upper() == "TRUE":
                bc_integration.skip_download = True

            try:
                bc_integration.get_platform_run_config()
            except Exception:
                if not self.config.include_all_checkov_policies:
                    # stack trace gets printed in the exception handlers above
                    # include_all_checkov_policies will always be set when there is no API key, so we don't need to worry about it here
                    print('An error occurred getting data from the platform, including policy metadata. Because --include-all-checkov-policies '
                          'was not used, Checkov cannot differentiate Checkov-only policies from platform policies, and no '
                          'policies will get evaluated. Please resolve the error above or re-run with the --include-all-checkov-policies argument '
                          '(but note that this will not include any custom platform configurations or policy metadata).',
                          file=sys.stderr)
                    self.exit_run()

            # bc_integration.get_runtime_run_config()
            bc_integration.setup_on_prem()
            if bc_integration.on_prem:
                # disable --support for on-premises integrations
                if bc_integration.support_flag_enabled:
                    logger.warning("--support flag is not supported for on-premises integrations")
                    bc_integration.support_flag_enabled = False
                # disable sca_package, sca_image for on-premises integrations
                if not outer_registry:
                    removed_check_types = []
                    for runner in list(runner_registry.runners):
                        if runner.check_type in [CheckType.SCA_IMAGE, CheckType.SCA_PACKAGE]:
                            removed_check_types.append(runner.check_type)
                            runner_registry.runners.remove(runner)
                    if removed_check_types:
                        logger.warning(f"Following runners won't run as they are not supported for on-premises integrations: {removed_check_types}")

            bc_integration.get_prisma_build_policies(self.config.policy_metadata_filter, self.config.policy_metadata_filter_exception)

            # set config to make it usable inside the integration features
            integration_feature_registry.config = self.config
            integration_feature_registry.run_pre_scan()

            # assign policies suppression to runner_filter
            policy_level_suppression = suppressions_integration.get_policy_level_suppressions()
            runner_filter.bc_cloned_checks = custom_policies_integration.bc_cloned_checks
            custom_policies_integration.policy_level_suppression = list(policy_level_suppression.keys())
            runner_filter.set_suppressed_policies(list(policy_level_suppression.values()))

            if any(framework in runner_filter.framework for framework in ("all", CheckType.SCA_IMAGE)):
                # only run image referencer, when sca_image framework is enabled
                runner_filter.run_image_referencer = licensing_integration.should_run_image_referencer()

            runner_filter.filtered_policy_ids = policy_metadata_integration.filtered_policy_ids
            runner_filter.filtered_exception_policy_ids = policy_metadata_integration.filtered_exception_policy_ids
            logger.debug(f"Filtered list of policies: {runner_filter.filtered_policy_ids}")
            logger.debug(f"Filtered excluded list of policies: {runner_filter.filtered_exception_policy_ids}")

            runner_filter.excluded_paths = runner_filter.excluded_paths + list(repo_config_integration.skip_paths)

            if self.config.use_enforcement_rules:
                runner_filter.apply_enforcement_rules(repo_config_integration.code_category_configs)

            if self.config.list:
                print_checks(frameworks=self.config.framework, use_bc_ids=self.config.output_bc_ids,
                             include_all_checkov_policies=self.config.include_all_checkov_policies,
                             filtered_policy_ids=runner_filter.filtered_policy_ids,
                             filtered_exception_policy_ids=runner_filter.filtered_exception_policy_ids)
                return None

            baseline = None
            if self.config.baseline:
                baseline = Baseline(self.config.output_baseline_as_skipped)
                baseline.from_json(self.config.baseline)

            external_checks_dir = self.get_external_checks_dir()
            created_baseline_path = None

            default_github_dir_path = os.getcwd() + '/' + os.getenv('CKV_GITHUB_CONF_DIR_NAME', 'github_conf')
            git_configuration_folders = [os.getenv("CKV_GITHUB_CONF_DIR_PATH", default_github_dir_path),
                                         os.getcwd() + '/' + os.getenv('CKV_GITLAB_CONF_DIR_NAME', 'gitlab_conf')]

            if self.config.directory:
                exit_codes = []
                bc_integration.scan_dir = self.config.directory
                for root_folder in self.config.directory:
                    absolute_root_folder = os.path.abspath(root_folder)
                    if not os.path.exists(root_folder):
                        logger.error(f'Directory {root_folder} does not exist; skipping it')
                        continue
                    file = self.config.file
                    self.scan_reports = runner_registry.run(
                        root_folder=root_folder,
                        external_checks_dir=external_checks_dir,
                        files=file,
                    )
                    self.graphs = runner_registry.check_type_to_graph
                    self.resource_subgraph_maps = runner_registry.check_type_to_resource_subgraph_map
                    if runner_registry.is_error_in_reports(self.scan_reports):
                        self.exit_run()
                    if baseline:
                        baseline.compare_and_reduce_reports(self.scan_reports)

                    if bc_integration.is_integration_configured() \
                            and bc_integration.bc_source \
                            and bc_integration.bc_source.upload_results \
                            and not self.config.skip_results_upload \
                            and not bc_integration.s3_setup_failed:
                        included_paths = [self.config.external_modules_download_path]
                        for r in runner_registry.runners:
                            included_paths.extend(r.included_paths())
                        self.save_sast_assets_data(self.scan_reports)
                        self.save_sast_reachability_data(self.scan_reports)
                        self.upload_results(
                            root_folder=root_folder,
                            absolute_root_folder=absolute_root_folder,
                            excluded_paths=runner_filter.excluded_paths,
                            included_paths=included_paths,
                            git_configuration_folders=git_configuration_folders,
                            sca_supported_ir_report=runner_registry.sca_supported_ir_report,
                            sast_languages=runner_filter.sast_languages
                        )

                    if self.config.create_baseline:
                        overall_baseline = Baseline()
                        for report in self.scan_reports:
                            overall_baseline.add_findings_from_report(report)
                        created_baseline_path = os.path.join(os.path.abspath(root_folder), '.checkov.baseline')
                        with open(created_baseline_path, 'w') as f:
                            json.dump(overall_baseline.to_dict(), f, indent=4)
                    exit_codes.append(self.print_results(
                        runner_registry=runner_registry,
                        url=self.url,
                        created_baseline_path=created_baseline_path,
                        baseline=baseline,
                    ))

                # this needs to run after the upload (otherwise the repository does not exist)
                should_run_contributor_metrics = bc_integration.bc_api_key and self.config.repo_id and self.config.prisma_api_url
                logger.debug(f"Should run contributor metrics report: {should_run_contributor_metrics}")
                if should_run_contributor_metrics:
                    try:  # collect contributor info and upload
                        report_contributor_metrics(self.config.repo_id, source.name, bc_integration)
                    except Exception as e:
                        logger.warning(f"Unable to report contributor metrics due to: {e}")

                exit_code = 1 if 1 in exit_codes else 0
                return exit_code
            elif self.config.docker_image:
                if self.config.bc_api_key is None:
                    self.parser.error("--bc-api-key argument is required when using --docker-image")
                    return None
                if self.config.dockerfile_path is None:
                    self.parser.error("--dockerfile-path argument is required when using --docker-image")
                    return None
                if self.config.branch is None:
                    self.parser.error("--branch argument is required when using --docker-image")
                    return None
                files = [os.path.abspath(self.config.dockerfile_path)]
                sca_runner = sca_image_runner()
                result = sca_runner.run(
                    root_folder='',
                    image_id=self.config.docker_image,
                    dockerfile_path=self.config.dockerfile_path,
                    runner_filter=runner_filter,
                )
                self.scan_reports = result if isinstance(result, list) else [result]
                if runner_registry.is_error_in_reports(self.scan_reports):
                    self.exit_run()
                if len(self.scan_reports) > 1:
                    # this shouldn't happen, but if it happens, then it is intended or something is broke
                    logger.error(f"SCA image runner returned {len(self.scan_reports)} reports; expected 1")

                integration_feature_registry.run_post_runner(self.scan_reports[0])

                if not self.config.skip_results_upload and not bc_integration.s3_setup_failed:
                    try:
                        if not bc_integration.on_prem:
                            bc_integration.persist_repository(os.path.dirname(self.config.dockerfile_path), files=files, sast_languages=runner_filter.sast_languages)
                        bc_integration.persist_scan_results(self.scan_reports)
                        bc_integration.persist_sast_scan_results(self.scan_reports)
                        bc_integration.persist_cdk_scan_results(self.scan_reports)
                        bc_integration.persist_image_scan_results(sca_runner.raw_report, self.config.dockerfile_path,
                                                                  self.config.docker_image,
                                                                  self.config.branch)

                        bc_integration.persist_run_metadata(self.run_metadata)
                        # there is no graph to persist
                        self.url = self.commit_repository()
                    except Exception:
                        logging.error('An error occurred while uploading scan results to the platform', exc_info=True)
                        bc_integration.s3_setup_failed = True

                should_run_contributor_metrics = bc_integration.bc_api_key and self.config.repo_id and self.config.prisma_api_url
                logger.debug(f"Should run contributor metrics report: {should_run_contributor_metrics}")
                if should_run_contributor_metrics:
                    try:  # collect contributor info and upload
                        report_contributor_metrics(self.config.repo_id, source.name, bc_integration)
                    except Exception as e:
                        logger.warning(f"Unable to report contributor metrics due to: {e}")

                exit_code = self.print_results(runner_registry=runner_registry, url=self.url)
                return exit_code
            elif self.config.file:
                bc_integration.scan_file = self.config.file
                runner_registry.filter_runners_for_files(self.config.file)
                self.scan_reports = runner_registry.run(
                    external_checks_dir=external_checks_dir,
                    files=self.config.file,
                    repo_root_for_plan_enrichment=self.config.repo_root_for_plan_enrichment,
                )
                self.graphs = runner_registry.check_type_to_graph
                self.resource_subgraph_maps = runner_registry.check_type_to_resource_subgraph_map
                if runner_registry.is_error_in_reports(self.scan_reports):
                    self.exit_run()
                if baseline:
                    baseline.compare_and_reduce_reports(self.scan_reports)
                if self.config.create_baseline:
                    overall_baseline = Baseline()
                    for report in self.scan_reports:
                        overall_baseline.add_findings_from_report(report)
                    created_baseline_path = os.path.join(os.path.abspath(os.path.commonprefix(self.config.file)),
                                                         '.checkov.baseline')
                    with open(created_baseline_path, 'w') as f:
                        json.dump(overall_baseline.to_dict(), f, indent=4)

                if bc_integration.is_integration_configured() \
                        and bc_integration.bc_source \
                        and bc_integration.bc_source.upload_results \
                        and not self.config.skip_results_upload \
                        and not bc_integration.s3_setup_failed:
                    files = [os.path.abspath(file) for file in self.config.file]
                    root_folder = os.path.split(os.path.commonprefix(files))[0]
                    absolute_root_folder = os.path.abspath(root_folder)

                    self.save_sast_assets_data(self.scan_reports)
                    self.save_sast_reachability_data(self.scan_reports)
                    self.upload_results(
                        root_folder=root_folder,
                        absolute_root_folder=absolute_root_folder,
                        files=files,
                        excluded_paths=runner_filter.excluded_paths,
                        git_configuration_folders=git_configuration_folders,
                        sast_languages=runner_filter.sast_languages
                    )

                should_run_contributor_metrics = bc_integration.bc_api_key and self.config.repo_id and self.config.prisma_api_url
                logger.debug(f"Should run contributor metrics report: {should_run_contributor_metrics}")
                if should_run_contributor_metrics:
                    try:  # collect contributor info and upload
                        report_contributor_metrics(self.config.repo_id, source.name, bc_integration)
                    except Exception as e:
                        logger.warning(f"Unable to report contributor metrics due to: {e}")

                exit_code = self.print_results(
                    runner_registry=runner_registry,
                    url=self.url,
                    created_baseline_path=created_baseline_path,
                    baseline=baseline,
                )
                return exit_code
            elif not self.config.quiet:
                print(f"{banner}")
            return None
        except ModuleNotEnabledError as m:
            if all(framework in self.config.framework for framework in m.unsupported_frameworks):
                logging.warning(m)
            return None
        except PlatformConnectionError:
            # we don't want to print all of these stack traces in normal output, as these could be user error
            # and stack traces look like checkov bugs
            logging.debug("Exception traceback:", exc_info=True)
            self.exit_run()
            return None
        except SystemExit:
            # calling exit_run from an exception handler causes another exception that is caught here, so we just need to re-exit
            self.exit_run()
            return None
        except BaseException:  # noqa: B036 # we need to catch any failure and exit properly
            logging.error("Exception traceback:", exc_info=True)
            self.exit_run()
            return None

        finally:
            if bc_integration.support_flag_enabled:
                # append main process log stream to the list of all streams
                logger_streams.add_stream('main', logs_stream)

                if bc_integration.s3_setup_failed:
                    print_to_stderr = os.getenv('CKV_STDERR_DEBUG', 'FALSE').upper() == 'TRUE'
                    log_level = os.getenv('LOG_LEVEL', '')
                    if log_level == 'DEBUG':
                        print('Unable to upload support logs. However, LOG_LEVEL is already set to DEBUG, so debug logs are available locally.')
                    elif print_to_stderr:
                        print('Unable to upload support logs - CKV_STDERR_DEBUG is TRUE, printing to stderr.')
                        logger_streams.print_to_console()
                    else:
                        # default to writing to a file - if they are using the support flag they probably are not excited
                        # to get debug logs from stderr (but they also might not be able to access a local file if it
                        # is in CI/CD, so there is not a good approach here)
                        print('Unable to upload support logs - saving debug logs to ./checkov_debug.log. To print the debug '
                              'logs to stderr instead, set the CKV_STDERR_DEBUG environment variable to TRUE, and re-run. '
                              'Note that this will result in the scan results being printed, followed by all logs.')
                        logger_streams.print_to_files()
                else:
                    bc_integration.persist_all_logs_streams(logger_streams.get_streams())

    def exit_run(self) -> None:
        exit(0) if self.config.no_fail_on_crash else exit(2)

    def commit_repository(self) -> str | None:
        try:
            return bc_integration.commit_repository(self.config.branch)
        except Exception:
            logging.debug("commit_repository failed, exiting", exc_info=True)
            self.exit_run()
            return ""

    def get_external_checks_dir(self) -> list[str]:
        external_checks_dir: "list[str]" = self.config.external_checks_dir
        if self.config.external_checks_git:
            git_getter = GitGetter(url=self.config.external_checks_git[0])
            external_checks_dir = [git_getter.get()]
            atexit.register(shutil.rmtree, str(Path(external_checks_dir[0]).parent))
        if bc_integration.sast_custom_policies:
            if not external_checks_dir:
                external_checks_dir = []
            external_checks_dir.append(bc_integration.sast_custom_policies)
        return external_checks_dir

    def upload_results(
            self,
            root_folder: str,
            absolute_root_folder: str,
            files: list[str] | None = None,
            excluded_paths: list[str] | None = None,
            included_paths: list[str] | None = None,
            git_configuration_folders: list[str] | None = None,
            sca_supported_ir_report: Report | None = None,
            sast_languages: Set[SastLanguages] | None = None
    ) -> None:
        """Upload scan results and other relevant files"""

        try:
            scan_reports_to_upload = self.scan_reports
            if not bc_integration.on_prem:
                bc_integration.persist_repository(
                    root_dir=root_folder,
                    files=files,
                    excluded_paths=excluded_paths,
                    included_paths=included_paths,
                    sast_languages=sast_languages
                )
                if git_configuration_folders:
                    bc_integration.persist_git_configuration(os.getcwd(), git_configuration_folders)
                if sca_supported_ir_report:
                    scan_reports_to_upload = [report for report in self.scan_reports if report.check_type != 'sca_image']
                    scan_reports_to_upload.append(sca_supported_ir_report)
            bc_integration.persist_scan_results(scan_reports_to_upload)
            bc_integration.persist_sast_scan_results(scan_reports_to_upload)
            bc_integration.persist_cdk_scan_results(scan_reports_to_upload)
            bc_integration.persist_assets_scan_results(self.sast_data.imports_data)
            bc_integration.persist_reachability_scan_results(self.sast_data.reachability_report)
            bc_integration.persist_run_metadata(self.run_metadata)
            if bc_integration.enable_persist_graphs and not bc_integration.on_prem:
                bc_integration.persist_graphs(self.graphs, absolute_root_folder=absolute_root_folder)
                bc_integration.persist_resource_subgraph_maps(self.resource_subgraph_maps)
            self.url = self.commit_repository()
        except Exception:
            logging.error('An error occurred while uploading scan results to the platform', exc_info=True)
            bc_integration.s3_setup_failed = True

    def save_sast_assets_data(self, scan_reports: List[Report]) -> None:
        if not bool(convert_str_to_bool(os.getenv('CKV_ENABLE_UPLOAD_SAST_IMPORTS', False))):
            return
        sast_report = [scan_report for scan_report in scan_reports if isinstance(scan_report, SastReport)]
        sast_imports_report = self.sast_data.get_sast_import_report(sast_report)
        self.sast_data.set_imports_data(sast_imports_report)

    def save_sast_reachability_data(self, scan_reports: List[Report]) -> None:
        if not bool(convert_str_to_bool(os.getenv('CKV_ENABLE_UPLOAD_SAST_REACHABILITY', False))):
            return
        sast_report = [scan_report for scan_report in scan_reports if isinstance(scan_report, SastReport)]
        result: Dict[SastLanguages, Any] = {}
        for rep in sast_report:
            if rep.sast_reachability:
                result[rep.language] = {}
        for rep in sast_report:
            if rep.sast_reachability:
                result[rep.language] = {**result[rep.language], **serialize_reachability_report(rep.sast_reachability)}

        formated_report = SastReport.get_formated_reachability_report(result)
        self.sast_data.set_reachability_report(formated_report)

    def print_results(
            self,
            runner_registry: RunnerRegistry,
            url: str | None = None,
            created_baseline_path: str | None = None,
            baseline: Baseline | None = None,
    ) -> Literal[0, 1]:
        """Print scan results to stdout"""

        if convert_str_to_bool(os.getenv("CHECKOV_NO_OUTPUT", "False")):
            # this is mainly used for testing, where the report output is not needed
            return 0

        return runner_registry.print_reports(
            scan_reports=self.scan_reports,
            config=self.config,
            url=url,
            created_baseline_path=created_baseline_path,
            baseline=baseline,
        )


# the flag/arg parsing moved to checkov/common/util/ext_argument_parser.py


if __name__ == '__main__':
    ckv = Checkov()
    sys.exit(ckv.run())
