import argparse
import itertools
import json
import logging
import os
from abc import abstractmethod
from typing import List, Union, Dict, Any, Tuple, Optional

from typing_extensions import Literal

from checkov.common.bridgecrew.integration_features.integration_feature_registry import integration_feature_registry
from checkov.common.output.baseline import Baseline
from checkov.common.output.report import Report
from checkov.common.runners.base_runner import BaseRunner
from checkov.common.util import data_structures_utils
from checkov.runner_filter import RunnerFilter
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.runner import Runner as tf_runner
from checkov.terraform.parser import Parser


CHECK_BLOCK_TYPES = frozenset(["resource", "data", "provider", "module"])
OUTPUT_CHOICES = ["cli", "json", "junitxml", "github_failed_only", "sarif"]
OUTPUT_DELIMITER = "\n--- OUTPUT DELIMITER ---\n"


class RunnerRegistry:
    runners: List[BaseRunner] = []
    scan_reports: List[Report] = []
    banner = ""

    def __init__(self, banner: str, runner_filter: RunnerFilter, *runners: BaseRunner) -> None:
        self.logger = logging.getLogger(__name__)
        self.runner_filter = runner_filter
        self.runners = list(runners)
        self.banner = banner
        self.scan_reports = []
        self.filter_runner_framework()

    @abstractmethod
    def extract_entity_details(self, entity: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        raise NotImplementedError()

    def run(
        self,
        root_folder: Optional[str] = None,
        external_checks_dir: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        guidelines: Optional[Dict[str, str]] = None,
        collect_skip_comments: bool = True,
        repo_root_for_plan_enrichment: Optional[List[Union[str, os.PathLike]]] = None,
    ) -> List[Report]:
        for runner in self.runners:
            integration_feature_registry.run_pre_runner()
            scan_report = runner.run(
                root_folder,
                external_checks_dir=external_checks_dir,
                files=files,
                runner_filter=self.runner_filter,
                collect_skip_comments=collect_skip_comments,
            )
            integration_feature_registry.run_post_runner(scan_report)
            if guidelines:
                RunnerRegistry.enrich_report_with_guidelines(scan_report, guidelines)
            if repo_root_for_plan_enrichment:
                enriched_resources = RunnerRegistry.get_enriched_resources(repo_root_for_plan_enrichment)
                scan_report = Report("terraform_plan").enrich_plan_report(scan_report, enriched_resources)
                scan_report = Report("terraform_plan").handle_skipped_checks(scan_report, enriched_resources)
            self.scan_reports.append(scan_report)
        return self.scan_reports

    def print_reports(
        self,
        scan_reports: List[Report],
        config: argparse.Namespace,
        url: Optional[str] = None,
        created_baseline_path: Optional[str] = None,
        baseline: Optional[Baseline] = None,
    ) -> Literal[0, 1]:
        output_formats = set(config.output)

        if "cli" in config.output and not config.quiet:
            print(f"{self.banner}\n")
        exit_codes = []
        report_jsons = []
        sarif_reports = []
        junit_reports = []
        for report in scan_reports:
            if not report.is_empty():
                if "json" in config.output:
                    report_jsons.append(report.get_dict(is_quiet=config.quiet))
                if "junitxml" in config.output:
                    junit_reports.append(report)
                    # report.print_junit_xml()
                if "github_failed_only" in config.output:
                    report.print_failed_github_md(use_bc_ids=config.output_bc_ids)
                if "sarif" in config.output:
                    sarif_reports.append(report)
                if "cli" in config.output:
                    report.print_console(
                        is_quiet=config.quiet,
                        is_compact=config.compact,
                        created_baseline_path=created_baseline_path,
                        baseline=baseline,
                        use_bc_ids=config.output_bc_ids,
                    )
                    if url:
                        print("More details: {}".format(url))
                    output_formats.discard("cli")
                    if output_formats:
                        print(OUTPUT_DELIMITER)
            exit_codes.append(report.get_exit_code(config.soft_fail, config.soft_fail_on, config.hard_fail_on))
        if "sarif" in config.output:
            master_report = Report(None)
            for report in sarif_reports:
                master_report.failed_checks += report.failed_checks
            master_report.print_sarif_report()
            output_formats.remove("sarif")
            if output_formats:
                print(OUTPUT_DELIMITER)
        if "json" in config.output:
            if len(report_jsons) == 1:
                print(json.dumps(report_jsons[0], indent=4))
            else:
                print(json.dumps(report_jsons, indent=4))
            output_formats.remove("json")
            if output_formats:
                print(OUTPUT_DELIMITER)
        if "junitxml" in config.output:
            if len(junit_reports) == 1:
                junit_reports[0].print_junit_xml(use_bc_ids=config.output_bc_ids)
            else:
                master_report = Report(None)
                for report in junit_reports:
                    master_report.skipped_checks += report.skipped_checks
                    master_report.passed_checks += report.passed_checks
                    master_report.failed_checks += report.failed_checks
                master_report.print_junit_xml(use_bc_ids=config.output_bc_ids)
            output_formats.remove("junitxml")
            if output_formats:
                print(OUTPUT_DELIMITER)
        # if config.output == "cli":
        # bc_integration.get_report_to_platform(config,scan_reports)

        exit_code = 1 if 1 in exit_codes else 0
        return exit_code

    def filter_runner_framework(self) -> None:
        if not self.runner_filter:
            return
        if self.runner_filter.framework is None:
            return
        if self.runner_filter.framework == "all":
            return
        self.runners = [runner for runner in self.runners if runner.check_type in self.runner_filter.framework]

    def remove_runner(self, runner: BaseRunner) -> None:
        if runner in self.runners:
            self.runners.remove(runner)

    @staticmethod
    def enrich_report_with_guidelines(scan_report: Report, guidelines: Dict[str, str]) -> None:
        for record in itertools.chain(scan_report.failed_checks, scan_report.passed_checks, scan_report.skipped_checks):
            if record.check_id in guidelines:
                record.set_guideline(guidelines[record.check_id])

    @staticmethod
    def get_enriched_resources(repo_roots: List[Union[str, os.PathLike]]) -> Dict[str, Dict[str, Any]]:
        repo_definitions = {}
        for repo_root in repo_roots:
            tf_definitions = {}
            parsing_errors = {}
            Parser().parse_directory(
                directory=repo_root,  # assume plan file is in the repo-root
                out_definitions=tf_definitions,
                out_parsing_errors=parsing_errors,
            )
            repo_definitions[repo_root] = { 'tf_definitions': tf_definitions, 'parsing_errors': parsing_errors }

        enriched_resources = {}
        for repo_root, parse_results in repo_definitions.items():
            for full_file_path, definition in parse_results['tf_definitions'].items():
                definitions_context = parser_registry.enrich_definitions_context((full_file_path, definition))
                abs_scanned_file, _ = tf_runner._strip_module_referrer(full_file_path)
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
