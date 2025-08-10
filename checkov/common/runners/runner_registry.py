from __future__ import annotations

import argparse
import itertools
import json
import logging
import os
import re
import platform
import sys
import time

from collections import defaultdict
from collections.abc import Iterable
from io import StringIO
from pathlib import Path
from typing import List, Dict, Any, Optional, cast, TYPE_CHECKING, Type, Literal
from checkov.common.bridgecrew.check_type import CheckType

from checkov.common.bridgecrew.code_categories import CodeCategoryMapping, CodeCategoryType
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import \
    integration as metadata_integration
from checkov.common.bridgecrew.integration_features.features.repo_config_integration import \
    integration as repo_config_integration
from checkov.common.bridgecrew.integration_features.features.licensing_integration import \
    integration as licensing_integration
from checkov.common.bridgecrew.integration_features.integration_feature_registry import integration_feature_registry
from checkov.common.bridgecrew.platform_errors import ModuleNotEnabledError
from checkov.common.bridgecrew.severities import Severities
from checkov.common.images.image_referencer import ImageReferencer
from checkov.common.logger_streams import logger_streams
from checkov.common.models.enums import ErrorStatus, ParallelizationType
from checkov.common.output.csv import CSVSBOM
from checkov.common.output.cyclonedx import CycloneDX
from checkov.common.output.gitlab_sast import GitLabSast
from checkov.common.output.report import Report, merge_reports
from checkov.common.output.sarif import Sarif
from checkov.common.output.spdx import SPDX
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.common.sast.consts import CDKLanguages
from checkov.common.typing import _ExitCodeThresholds, _BaseRunner, _ScaExitCodeThresholds, LibraryGraph
from checkov.common.util import data_structures_utils
from checkov.common.util.banner import default_tool as tool_name
from checkov.common.util.consts import S3_UPLOAD_DETAILS_MESSAGE
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.common.util.json_utils import CustomJSONEncoder
from checkov.common.util.secrets_omitter import SecretsOmitter
from checkov.common.util.type_forcers import convert_csv_string_arg_to_list, force_list
from checkov.logging_init import log_stream, erase_log_stream
from checkov.sca_image.runner import Runner as image_runner
from checkov.common.secrets.consts import SECRET_VALIDATION_STATUSES
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.tf_parser import TFParser

if TYPE_CHECKING:
    from checkov.common.output.baseline import Baseline
    from checkov.common.runners.base_runner import BaseRunner  # noqa
    from checkov.runner_filter import RunnerFilter

CONSOLE_OUTPUT = "console"
CHECK_BLOCK_TYPES = frozenset(["resource", "data", "provider", "module"])
CYCLONEDX_OUTPUTS = ("cyclonedx", "cyclonedx_json")
OUTPUT_CHOICES = [
    "cli",
    "csv",
    "cyclonedx",
    "cyclonedx_json",
    "json",
    "junitxml",
    "github_failed_only",
    "gitlab_sast",
    "sarif",
    "spdx",
]
SUMMARY_POSITIONS = frozenset(['top', 'bottom'])
OUTPUT_DELIMITER = "\n--- OUTPUT DELIMITER ---\n"


class RunnerRegistry:
    def __init__(
        self,
        banner: str,
        runner_filter: RunnerFilter,
        *runners: _BaseRunner,
        tool: str = tool_name,
        secrets_omitter_class: Type[SecretsOmitter] = SecretsOmitter,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        add_resource_code_filter_to_logger(self.logger)
        self.runner_filter = runner_filter
        self.runners = list(runners)
        self.banner = banner
        self.sca_supported_ir_report: Optional[Report] = None
        self.scan_reports: list[Report] = []
        self.image_referencing_runners = self._get_image_referencing_runners()
        self.filter_runner_framework()
        self.tool = tool
        self._check_type_to_report_map: dict[str, Report] = {}  # used for finding reports with the same check type
        self.licensing_integration = licensing_integration  # can be manipulated by unit tests
        self.secrets_omitter_class = secrets_omitter_class
        self.check_type_to_graph: dict[str, list[tuple[LibraryGraph, Optional[str]]]] = {}
        self.check_type_to_resource_subgraph_map: dict[str, dict[str, str]] = {}
        for runner in runners:
            if isinstance(runner, image_runner):
                runner.image_referencers = self.image_referencing_runners

    def run(
            self,
            root_folder: Optional[str] = None,
            external_checks_dir: Optional[List[str]] = None,
            files: Optional[List[str]] = None,
            collect_skip_comments: bool = True,
            repo_root_for_plan_enrichment: list[str | Path] | None = None,
    ) -> list[Report]:
        if not self.runners:
            logging.error('There are no runners to run. This can happen if you specify a file type and a framework that are not compatible '
                          '(e.g., `--file xyz.yaml --framework terraform`), or if you specify a framework with missing dependencies (e.g., '
                          'helm or kustomize, which require those tools to be on your system). Running with LOG_LEVEL=DEBUG may provide more information.')
            return []
        elif len(self.runners) == 1:
            runner_check_type = self.runners[0].check_type
            if self.licensing_integration.is_runner_valid(runner_check_type):
                reports: Iterable[Report | list[Report]] = [
                    self.runners[0].run(root_folder, external_checks_dir=external_checks_dir, files=files,
                                        runner_filter=self.runner_filter,
                                        collect_skip_comments=collect_skip_comments)]
            else:
                # This is the only runner, so raise a clear indication of failure
                raise ModuleNotEnabledError(f'The framework "{runner_check_type}" is part of the "{self.licensing_integration.get_subscription_for_runner(runner_check_type).name}" module, which is not enabled in the platform',
                                            unsupported_frameworks=[runner_check_type])
        else:
            valid_runners = []
            invalid_runners = []
            platform_integration_data = None

            if parallel_runner.type == ParallelizationType.SPAWN:
                platform_integration_data = bc_integration.generate_instance_data()

            for runner in self.runners:
                if self.licensing_integration.is_runner_valid(runner.check_type):
                    valid_runners.append(
                        (runner, root_folder, external_checks_dir, files, self.runner_filter, collect_skip_comments, platform_integration_data)
                    )
                else:
                    invalid_runners.append(runner)

            # if all runners are disabled (most likely to occur if the user specified --framework for only disabled runners)
            # then raise a clear error
            # if some frameworks are disabled and the user used --framework, log a warning so they see it
            # if some frameworks are disabled and the user did not use --framework, then log at a lower level so that we have it for troubleshooting
            if not valid_runners:
                check_types = [runner.check_type for runner in self.runners]
                runners_categories = os.linesep.join([f'{runner.check_type}: {self.licensing_integration.get_subscription_for_runner(runner.check_type).name}' for runner in invalid_runners])
                error_message = f'All the frameworks are disabled because they are not enabled in the platform. ' \
                                f'You must subscribe to one or more of the categories below to get results for these frameworks.{os.linesep}{runners_categories}'
                raise ModuleNotEnabledError(error_message, unsupported_frameworks=check_types)
            elif invalid_runners:
                for runner in invalid_runners:
                    level = logging.INFO
                    if runner.check_type in self.runner_filter.framework_flag_values:
                        level = logging.WARNING
                    logging.log(level, f'The framework "{runner.check_type}" is part of the "{self.licensing_integration.get_subscription_for_runner(runner.check_type).name}" module, which is not enabled in the platform')

            valid_runners = self._merge_runners(valid_runners)

            parallel_runner_results = parallel_runner.run_function(
                func=_parallel_run,
                items=valid_runners,
                group_size=1,
            )

            reports = []
            full_check_type_to_graph = {}
            full_check_type_to_resource_subgraph_map = {}
            for result in parallel_runner_results:
                if result is not None:
                    report, check_type, graphs, resource_subgraph_map, subprocess_log_stream = result
                    reports.append(report)
                    if subprocess_log_stream is not None:
                        # only sub processes need to add their logs streams,
                        # the logs of all others methods already exists in the main stream
                        if parallel_runner.running_as_process():
                            logger_streams.add_stream(f'{check_type or time.time()}', subprocess_log_stream)
                    if check_type is not None:
                        if graphs is not None:
                            full_check_type_to_graph[check_type] = graphs
                        if resource_subgraph_map is not None:
                            full_check_type_to_resource_subgraph_map[check_type] = resource_subgraph_map
            self.check_type_to_graph = full_check_type_to_graph
            self.check_type_to_resource_subgraph_map = full_check_type_to_resource_subgraph_map

        merged_reports = self._merge_reports(reports)
        if bc_integration.bc_api_key:
            self.secrets_omitter_class(merged_reports).omit()

        post_scan_reports = integration_feature_registry.run_post_scan(merged_reports)
        if post_scan_reports:
            merged_reports.extend(post_scan_reports)

        for scan_report in merged_reports:
            self._handle_report(scan_report, repo_root_for_plan_enrichment)

        if not self.check_type_to_graph:
            self.check_type_to_graph = {runner.check_type: self.extract_graphs_from_runner(runner) for runner
                                        in self.runners if runner.graph_manager}
        if not self.check_type_to_resource_subgraph_map:
            self.check_type_to_resource_subgraph_map = {runner.check_type: runner.resource_subgraph_map for runner in
                                                        self.runners if runner.resource_subgraph_map is not None}
        return self.scan_reports

    def _merge_runners(self, runners: Any) -> list[_BaseRunner]:
        sast_runner = None
        cdk_runner = None
        merged_runners = []
        for runner in runners:
            if runner[0].check_type == CheckType.CDK:
                cdk_runner = runner
                continue
            if runner[0].check_type == CheckType.SAST:
                merged_runners.append(runner)
                sast_runner = runner
                continue
            merged_runners.append(runner)

        if cdk_runner:
            if sast_runner:
                for lang in CDKLanguages.set():
                    sast_runner[0].cdk_langs.append(lang)
            else:
                merged_runners.append(cdk_runner)
        return merged_runners

    def _merge_reports(self, reports: Iterable[Report | list[Report]]) -> list[Report]:
        """Merges reports with the same check_type"""

        merged_reports = []

        for report in reports:
            if report is None:
                # this only happens, when an uncaught exception occurs
                continue

            sub_reports: list[Report] = force_list(report)
            for sub_report in sub_reports:
                if sub_report.check_type in self._check_type_to_report_map:
                    merge_reports(self._check_type_to_report_map[sub_report.check_type], sub_report)
                else:
                    self._check_type_to_report_map[sub_report.check_type] = sub_report
                    merged_reports.append(sub_report)

                if self.should_add_sca_results_to_sca_supported_ir_report(sub_report, sub_reports):
                    if self.sca_supported_ir_report:
                        merge_reports(self.sca_supported_ir_report, sub_report)
                    else:
                        self.sca_supported_ir_report = pickle_deepcopy(sub_report)

        return merged_reports

    @staticmethod
    def should_add_sca_results_to_sca_supported_ir_report(sub_report: Report, sub_reports: list[Report]) -> bool:
        if sub_report.check_type == 'sca_image' and bc_integration.customer_run_config_response:
            # The regular sca report
            if len(sub_reports) == 1:
                return True
            # Dup report: first - regular iac, second - IR. we are checking that report fw is in the IR supported list.
            if len(sub_reports) == 2 and sub_reports[0].check_type in bc_integration.customer_run_config_response.get('supportedIrFw', []):
                return True
        return False

    def _handle_report(self, scan_report: Report, repo_root_for_plan_enrichment: list[str | Path] | None) -> None:
        if metadata_integration.check_metadata:
            RunnerRegistry.enrich_report_with_guidelines(scan_report)
        if repo_root_for_plan_enrichment and not self.runner_filter.deep_analysis:
            enriched_resources = RunnerRegistry.get_enriched_resources(
                repo_roots=repo_root_for_plan_enrichment,
                download_external_modules=self.runner_filter.download_external_modules,
            )
            scan_report = Report("terraform_plan").enrich_plan_report(scan_report, enriched_resources)
            scan_report = Report("terraform_plan").handle_skipped_checks(scan_report, enriched_resources)
        integration_feature_registry.run_post_runner(scan_report)
        self.scan_reports.append(scan_report)

    def save_output_to_file(self, file_name: str, data: str, data_format: str) -> None:
        try:
            file_path = Path(file_name)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(data)
            logging.info(f"\nWrote output in {data_format} format to the file '{file_name}')")
        except EnvironmentError:
            logging.error(f"\nAn error occurred while writing {data_format} results to file: {file_name}",
                          exc_info=True)

    @staticmethod
    def is_error_in_reports(reports: List[Report]) -> bool:
        return any(scan_report.error_status != ErrorStatus.SUCCESS for scan_report in reports)

    @staticmethod
    def get_fail_thresholds(config: argparse.Namespace, report_type: str) -> _ExitCodeThresholds | _ScaExitCodeThresholds:

        soft_fail = config.soft_fail

        soft_fail_on_checks = []
        soft_fail_threshold = None

        # these specifically check the --hard-fail-on and --soft-fail-on args, NOT enforcement rules, so
        # we don't care about SCA as a special case

        # soft fail on the highest severity threshold in the list
        for val in convert_csv_string_arg_to_list(config.soft_fail_on):
            if val.upper() in Severities:
                val = val.upper()
                if not soft_fail_threshold or Severities[val].level > soft_fail_threshold.level:
                    soft_fail_threshold = Severities[val]
            elif val.capitalize() in SECRET_VALIDATION_STATUSES:
                soft_fail_on_checks.append(val.capitalize())
            else:
                soft_fail_on_checks.append(val)

        logging.debug(f'Soft fail severity threshold: {soft_fail_threshold.level if soft_fail_threshold else None}')
        logging.debug(f'Soft fail checks: {soft_fail_on_checks}')

        hard_fail_on_checks = []
        hard_fail_threshold = None
        # hard fail on the lowest threshold in the list
        for val in convert_csv_string_arg_to_list(config.hard_fail_on):
            if val.upper() in Severities:
                val = val.upper()
                if not hard_fail_threshold or Severities[val].level < hard_fail_threshold.level:
                    hard_fail_threshold = Severities[val]
            elif val.capitalize() in SECRET_VALIDATION_STATUSES:
                hard_fail_on_checks.append(val.capitalize())
            else:
                hard_fail_on_checks.append(val)

        logging.debug(f'Hard fail severity threshold: {hard_fail_threshold.level if hard_fail_threshold else None}')
        logging.debug(f'Hard fail checks: {hard_fail_on_checks}')

        if not config.use_enforcement_rules:
            logging.debug('Use enforcement rules is FALSE')

        # if there is a severity in either the soft-fail-on list or hard-fail-on list, then we will ignore enforcement rules and skip this
        # it means that SCA will not be treated as having two different thresholds in that case
        # if the lists only contain check IDs, then we will merge them with the enforcement rule value
        elif not soft_fail and not soft_fail_threshold and not hard_fail_threshold:
            if 'sca_' in report_type:
                code_category_types = cast(List[CodeCategoryType], CodeCategoryMapping[report_type])
                category_rules = {
                    category: repo_config_integration.code_category_configs[category] for category in code_category_types
                }
                return cast(_ScaExitCodeThresholds, {
                    category: {
                        'soft_fail': category_rules[category].is_global_soft_fail(),
                        'soft_fail_checks': soft_fail_on_checks,
                        'soft_fail_threshold': soft_fail_threshold,
                        'hard_fail_checks': hard_fail_on_checks,
                        'hard_fail_threshold': category_rules[category].hard_fail_threshold
                    } for category in code_category_types
                })
            else:
                code_category_type = cast(CodeCategoryType, CodeCategoryMapping[report_type])  # not a list
                enf_rule = repo_config_integration.code_category_configs[code_category_type]

                if enf_rule:
                    logging.debug('Use enforcement rules is TRUE')
                    hard_fail_threshold = enf_rule.hard_fail_threshold
                    soft_fail = enf_rule.is_global_soft_fail()
                    logging.debug(f'Using enforcement rule hard fail threshold for this report: {hard_fail_threshold.name}')
                else:
                    logging.debug(f'Use enforcement rules is TRUE, but did not find an enforcement rule for report type {report_type}, so falling back to CLI args')
        else:
            logging.debug('Soft fail was true or a severity was used in soft fail on / hard fail on; ignoring enforcement rules')

        return {
            'soft_fail': soft_fail,
            'soft_fail_checks': soft_fail_on_checks,
            'soft_fail_threshold': soft_fail_threshold,
            'hard_fail_checks': hard_fail_on_checks,
            'hard_fail_threshold': hard_fail_threshold
        }

    def print_reports(
            self,
            scan_reports: List[Report],
            config: argparse.Namespace,
            url: Optional[str] = None,
            created_baseline_path: Optional[str] = None,
            baseline: Optional[Baseline] = None,
    ) -> Literal[0, 1]:
        output_formats: "dict[str, str]" = {}

        if config.output_file_path and "," in config.output_file_path:
            output_paths = config.output_file_path.split(",")
            for idx, output_format in enumerate(config.output):
                output_formats[output_format] = output_paths[idx]
        else:
            output_formats = {output_format: CONSOLE_OUTPUT for output_format in config.output}

        exit_codes = []
        cli_reports = []
        report_jsons = []
        sarif_reports = []
        junit_reports = []
        github_reports = []
        cyclonedx_reports = []
        gitlab_reports = []
        spdx_reports = []
        csv_sbom_report = CSVSBOM()

        try:
            if config.skip_resources_without_violations:
                for report in scan_reports:
                    report.extra_resources = set()
        except AttributeError:
            # config attribute wasn't set, defaults to False and print extra resources to report
            pass

        data_outputs: dict[str, str] = defaultdict(str)
        for report in scan_reports:
            if not report.is_empty():
                if "json" in config.output:
                    report_jsons.append(report.get_dict(is_quiet=config.quiet, url=url, s3_setup_failed=bc_integration.s3_setup_failed, support_path=bc_integration.support_repo_path))
                if "junitxml" in config.output:
                    junit_reports.append(report)
                if "github_failed_only" in config.output:
                    github_reports.append(report.print_failed_github_md(use_bc_ids=config.output_bc_ids))
                if "sarif" in config.output:
                    sarif_reports.append(report)
                if "cli" in config.output:
                    cli_reports.append(report)
                if "gitlab_sast" in config.output:
                    gitlab_reports.append(report)
            if not report.is_empty() or len(report.extra_resources):
                if any(cyclonedx in config.output for cyclonedx in CYCLONEDX_OUTPUTS):
                    cyclonedx_reports.append(report)
                if "spdx" in config.output:
                    spdx_reports.append(report)
                if "csv" in config.output:
                    git_org = ""
                    git_repository = ""
                    if 'repo_id' in config and config.repo_id is not None:
                        git_org, git_repository = config.repo_id.split('/')
                    csv_sbom_report.add_report(report=report, git_org=git_org, git_repository=git_repository)
            logging.debug(f'Getting exit code for report {report.check_type}')
            exit_code_thresholds = self.get_fail_thresholds(config, report.check_type)
            exit_codes.append(report.get_exit_code(exit_code_thresholds))

        if "github_failed_only" in config.output:
            github_output = "".join(github_reports)

            self._print_to_console(
                output_formats=output_formats,
                output_format="github_failed_only",
                output=github_output,
            )

            data_outputs["github_failed_only"] = github_output
        if "cli" in config.output:
            if not config.quiet:
                print(f"{self.banner}\n")

            cli_output = ''

            if (bc_integration.runtime_run_config_response and bc_integration.runtime_run_config_response.get('isRepoInRuntime', False)):
                cli_output += f"The '{bc_integration.repo_id}' repository was discovered In a running environment\n\n"

            if len(cli_reports) > 0:
                cli_output += cli_reports[0].add_errors_to_output()

            for report in cli_reports:
                cli_output += report.print_console(
                    is_quiet=config.quiet,
                    is_compact=config.compact,
                    created_baseline_path=created_baseline_path,
                    baseline=baseline,
                    use_bc_ids=config.output_bc_ids,
                    summary_position=config.summary_position,
                )

            self._print_to_console(
                output_formats=output_formats,
                output_format="cli",
                output=cli_output,
                url=url,
                support_path=bc_integration.support_repo_path
            )

            # Remove colors from the cli output
            ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-9:;<=>?]*[ -/]*[@-~]')
            data_outputs['cli'] = ansi_escape.sub('', cli_output)
        if "sarif" in config.output:
            sarif = Sarif(reports=sarif_reports, tool=self.tool)

            output_format = output_formats["sarif"]
            if "cli" not in config.output and output_format == CONSOLE_OUTPUT:
                print(self.banner)

            for report in sarif_reports:
                if "cli" not in config.output and output_format == CONSOLE_OUTPUT:
                    print(report.print_console(
                        is_quiet=config.quiet,
                        is_compact=config.compact,
                        created_baseline_path=created_baseline_path,
                        baseline=baseline,
                        use_bc_ids=config.output_bc_ids,
                        summary_position=config.summary_position
                    ))

            if output_format == CONSOLE_OUTPUT:
                if not config.output_file_path or "," in config.output_file_path:
                    # don't write to file, if an explicit file path was set
                    sarif.write_sarif_output()

                del output_formats["sarif"]

                if "cli" not in config.output:
                    if url:
                        print(f"More details: {url}")
                    elif bc_integration.s3_setup_failed:
                        print(S3_UPLOAD_DETAILS_MESSAGE)
                    if bc_integration.support_repo_path:
                        print(f"\nPath for uploaded logs (give this to support if raising an issue): {bc_integration.support_repo_path}")
                if CONSOLE_OUTPUT in output_formats.values():
                    print(OUTPUT_DELIMITER)

            data_outputs["sarif"] = json.dumps(sarif.json, cls=CustomJSONEncoder)
        if "json" in config.output:
            if config.compact and report_jsons:
                self.strip_code_blocks_from_json(report_jsons)

            report_json_output: "list[dict[str, Any]] | dict[str, Any]" = report_jsons
            if not report_jsons:
                report_json_output = Report("").get_summary()
            elif len(report_jsons) == 1:
                report_json_output = report_jsons[0]

            json_output = json.dumps(report_json_output, indent=4, cls=CustomJSONEncoder)

            self._print_to_console(
                output_formats=output_formats,
                output_format="json",
                output=json_output,
            )

            data_outputs["json"] = json.dumps(report_json_output, cls=CustomJSONEncoder)
        if "junitxml" in config.output:
            properties = Report.create_test_suite_properties_block(config)

            if junit_reports:
                test_suites = [
                    report.get_test_suite(properties=properties, use_bc_ids=config.output_bc_ids)
                    for report in junit_reports
                ]
            else:
                test_suites = [Report("").get_test_suite(properties=properties)]

            junit_output = Report.get_junit_xml_string(test_suites)

            self._print_to_console(
                output_formats=output_formats,
                output_format="junitxml",
                output=junit_output,
            )

            data_outputs['junitxml'] = junit_output
        if any(cyclonedx in config.output for cyclonedx in CYCLONEDX_OUTPUTS):
            cyclonedx = CycloneDX(repo_id=metadata_integration.bc_integration.repo_id, reports=cyclonedx_reports)

            for cyclonedx_format in CYCLONEDX_OUTPUTS:
                if cyclonedx_format not in config.output:
                    # only the XML or JSON format was chosen
                    continue

                if cyclonedx_format == "cyclonedx":
                    cyclonedx_output = cyclonedx.get_xml_output()
                elif cyclonedx_format == "cyclonedx_json":
                    cyclonedx_output = cyclonedx.get_json_output()
                else:
                    # this shouldn't happen
                    logging.error(f"CycloneDX output format '{cyclonedx_format}' not supported")
                    continue

                self._print_to_console(
                    output_formats=output_formats,
                    output_format=cyclonedx_format,
                    output=cyclonedx_output,
                )

                data_outputs[cyclonedx_format] = cyclonedx_output
        if "gitlab_sast" in config.output:
            gl_sast = GitLabSast(reports=gitlab_reports)

            self._print_to_console(
                output_formats=output_formats,
                output_format="gitlab_sast",
                output=json.dumps(gl_sast.sast_json, indent=4),
            )

            data_outputs["gitlab_sast"] = json.dumps(gl_sast.sast_json)
        if "spdx" in config.output:
            spdx = SPDX(repo_id=metadata_integration.bc_integration.repo_id, reports=spdx_reports)
            spdx_output = spdx.get_tag_value_output()

            self._print_to_console(
                output_formats=output_formats,
                output_format="spdx",
                output=spdx_output,
            )

            data_outputs["spdx"] = spdx_output
        if "csv" in config.output:
            is_api_key = False
            if 'bc_api_key' in config and config.bc_api_key is not None:
                is_api_key = True
            csv_sbom_report.persist_report(is_api_key=is_api_key, output_path=config.output_file_path)

        # Save output to file
        file_names = {
            'cli': 'results_cli.txt',
            'github_failed_only': 'results_github_failed_only.md',
            'sarif': 'results_sarif.sarif',
            'json': 'results_json.json',
            'junitxml': 'results_junitxml.xml',
            'cyclonedx': 'results_cyclonedx.xml',
            'cyclonedx_json': 'results_cyclonedx.json',
            'gitlab_sast': 'results_gitlab_sast.json',
            'spdx': 'results_spdx.spdx',
        }

        if config.output_file_path:
            if output_formats:
                for output_format, output_path in output_formats.items():
                    self.save_output_to_file(
                        file_name=output_path,
                        data=data_outputs[output_format],
                        data_format=output_format,
                    )
            else:
                for output in config.output:
                    if output in file_names:
                        self.save_output_to_file(
                            file_name=f'{config.output_file_path}/{file_names[output]}',
                            data=data_outputs[output],
                            data_format=output,
                        )
        exit_code = 1 if 1 in exit_codes else 0
        return cast(Literal[0, 1], exit_code)

    def _print_to_console(self, output_formats: dict[str, str], output_format: str, output: str, url: str | None = None, support_path: str | None = None) -> None:
        """Prints the output to console, if needed"""
        output_dest = output_formats[output_format]
        if output_dest == CONSOLE_OUTPUT:
            del output_formats[output_format]

            if platform.system() == 'Windows':
                sys.stdout.buffer.write(output.encode("utf-8"))
            else:
                print(output)
            if url:
                print(f"More details: {url}")
            elif bc_integration.s3_setup_failed:
                print(S3_UPLOAD_DETAILS_MESSAGE)

            if support_path:
                print(f"\nPath for uploaded logs (give this to support if raising an issue): {support_path}")

            if CONSOLE_OUTPUT in output_formats.values():
                print(OUTPUT_DELIMITER)

    def print_iac_bom_reports(self, output_path: str,
                              scan_reports: list[Report],
                              output_types: list[str],
                              account_id: str) -> dict[str, str]:

        output_files = {
            'cyclonedx': 'results_cyclonedx.xml',
            'csv': 'results_iac.csv'
        }

        # create cyclonedx report
        if 'cyclonedx' in output_types:
            cyclonedx_output_path = output_files['cyclonedx']
            cyclonedx = CycloneDX(reports=scan_reports,
                                  repo_id=metadata_integration.bc_integration.repo_id,
                                  export_iac_only=True)
            cyclonedx_output = cyclonedx.get_xml_output()
            self.save_output_to_file(file_name=os.path.join(output_path, cyclonedx_output_path),
                                     data=cyclonedx_output,
                                     data_format="cyclonedx")

        # create csv report
        if 'csv' in output_types:
            csv_sbom_report = CSVSBOM()
            for report in scan_reports:
                if not report.is_empty():
                    git_org, git_repository = self.extract_git_info_from_account_id(account_id)
                    csv_sbom_report.add_report(report=report, git_org=git_org, git_repository=git_repository)
            csv_sbom_report.persist_report_iac(file_name=output_files['csv'], output_path=output_path)

        return {key: os.path.join(output_path, value) for key, value in output_files.items()}

    def filter_runner_framework(self) -> None:
        if not self.runner_filter:
            return
        if not self.runner_filter.framework:
            return
        if "all" in self.runner_filter.framework:
            return
        self.runners = [runner for runner in self.runners if runner.check_type in self.runner_filter.framework]

    def filter_runners_for_files(self, files: List[str]) -> None:
        if not files:
            return

        self.runners = [runner for runner in self.runners if any(runner.should_scan_file(file) for file in files)]
        logging.debug(f'Filtered runners based on file type(s). Result: {[r.check_type for r in self.runners]}')

    def remove_runner(self, runner: _BaseRunner) -> None:
        if runner in self.runners:
            self.runners.remove(runner)  # type:ignore[arg-type] # existence is checked one line above

    @staticmethod
    def enrich_report_with_guidelines(scan_report: Report) -> None:
        for record in itertools.chain(scan_report.failed_checks, scan_report.passed_checks, scan_report.skipped_checks):
            guideline = metadata_integration.get_guideline(record.check_id)
            if guideline:
                record.set_guideline(guideline)

    @staticmethod
    def get_enriched_resources(
        repo_roots: list[str | Path],
        download_external_modules: Optional[bool]
    ) -> dict[str, dict[str, Any]]:
        from checkov.terraform.modules.module_objects import TFDefinitionKey

        repo_definitions = {}
        for repo_root in repo_roots:
            parsing_errors: dict[str, Exception] = {}
            repo_root = os.path.abspath(repo_root)
            tf_definitions: dict[TFDefinitionKey, dict[str, list[dict[str, Any]]]] = TFParser().parse_directory(
                directory=repo_root,  # assume plan file is in the repo-root
                out_parsing_errors=parsing_errors,
                download_external_modules=download_external_modules,
            )
            repo_definitions[repo_root] = {'tf_definitions': tf_definitions, 'parsing_errors': parsing_errors}

        enriched_resources = {}
        for repo_root, parse_results in repo_definitions.items():
            definitions = cast("dict[TFDefinitionKey, dict[str, list[dict[str, Any]]]]", parse_results['tf_definitions'])
            for full_file_path, definition in definitions.items():
                definitions_context = parser_registry.enrich_definitions_context((full_file_path, definition))
                abs_scanned_file = full_file_path.file_path
                scanned_file = os.path.relpath(abs_scanned_file, repo_root)
                for block_type, block_value in definition.items():
                    if block_type in CHECK_BLOCK_TYPES:
                        for entity in block_value:
                            context_parser = parser_registry.context_parsers[block_type]
                            definition_path = context_parser.get_entity_context_path(entity)
                            entity_id = ".".join(definition_path)
                            entity_context_path = [block_type] + definition_path
                            entity_context = data_structures_utils.get_inner_dict(
                                definitions_context[full_file_path], entity_context_path
                            )
                            entity_lines_range = [
                                entity_context.get("start_line"),
                                entity_context.get("end_line"),
                            ]
                            entity_code_lines = entity_context.get("code_lines")
                            skipped_checks = entity_context.get("skipped_checks")
                            enriched_resources[entity_id] = {
                                "entity_code_lines": entity_code_lines,
                                "entity_lines_range": entity_lines_range,
                                "scanned_file": scanned_file,
                                "skipped_checks": skipped_checks,
                            }
        return enriched_resources

    def _get_image_referencing_runners(self) -> set[ImageReferencer]:
        image_referencing_runners: set[ImageReferencer] = set()
        for runner in self.runners:
            if issubclass(runner.__class__, ImageReferencer):
                image_referencing_runners.add(cast(ImageReferencer, runner))

        return image_referencing_runners

    @staticmethod
    def strip_code_blocks_from_json(report_jsons: List[Dict[str, Any]]) -> None:
        for report in report_jsons:
            results = report.get('results', {})
            for result in results.values():
                for result_dict in result:
                    if isinstance(result_dict, dict):
                        result_dict["code_block"] = None
                        result_dict["connected_node"] = None

    @staticmethod
    def extract_git_info_from_account_id(account_id: str) -> tuple[str, str]:
        if '/' in account_id:
            account_id_list = account_id.split('/')
            git_org = '/'.join(account_id_list[0:-1])
            git_repository = account_id_list[-1]
        else:
            git_org, git_repository = "", ""

        return git_org, git_repository

    @staticmethod
    def extract_graphs_from_runner(runner: _BaseRunner) -> list[tuple[LibraryGraph, Optional[str]]]:
        # exist only for terraform
        all_graphs = getattr(runner, 'all_graphs', None)
        if all_graphs:
            return all_graphs   # type:ignore[no-any-return]
        elif runner.graph_manager:
            return [(runner.graph_manager.get_reader_endpoint(), None)]
        return []


def _parallel_run(
    runner: _BaseRunner,
    root_folder: str | None = None,
    external_checks_dir: list[str] | None = None,
    files: list[str] | None = None,
    runner_filter: RunnerFilter | None = None,
    collect_skip_comments: bool = True,
    platform_integration_data: dict[str, Any] | None = None,
) -> tuple[Report | list[Report], str | None, list[tuple[LibraryGraph, str | None]] | None, dict[str, str] | None, StringIO | None]:
    # only sub processes need to erase their logs, to start clean
    if parallel_runner.running_as_process():
        erase_log_stream()

    if platform_integration_data:
        # only happens for 'ParallelizationType.SPAWN'
        bc_integration.init_instance(platform_integration_data=platform_integration_data)

    report = runner.run(
        root_folder=root_folder,
        external_checks_dir=external_checks_dir,
        files=files,
        runner_filter=runner_filter,
        collect_skip_comments=collect_skip_comments,
    )
    if report is None:
        # this only happens, when an uncaught exception inside the runner occurs
        logging.error(f"Failed to create report for {runner.check_type} framework")
        report = Report(check_type=runner.check_type)

    if runner.graph_manager:
        return report, runner.check_type, RunnerRegistry.extract_graphs_from_runner(runner), runner.resource_subgraph_map, log_stream
    return report, runner.check_type, None, None, log_stream
