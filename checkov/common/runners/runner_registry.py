from __future__ import annotations

import argparse
import itertools
import json
import logging
import os
import re

from collections import defaultdict
from collections.abc import Iterable
from json import dumps
from pathlib import Path
from typing import List, Dict, Any, Optional, cast, TYPE_CHECKING, TypeVar

from typing_extensions import Literal

from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import \
    integration as metadata_integration
from checkov.common.bridgecrew.integration_features.integration_feature_registry import integration_feature_registry
from checkov.common.images.image_referencer import ImageReferencer
from checkov.common.output.csv import CSVSBOM
from checkov.common.output.cyclonedx import CycloneDX
from checkov.common.output.report import Report
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.util import data_structures_utils
from checkov.common.util.banner import tool as tool_name
from checkov.common.util.json_utils import CustomJSONEncoder
from checkov.sca_image.runner import Runner as image_runner
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.parser import Parser
from checkov.terraform.runner import Runner as tf_runner

if TYPE_CHECKING:
    from checkov.common.output.baseline import Baseline
    from checkov.common.runners.base_runner import BaseRunner  # noqa
    from checkov.runner_filter import RunnerFilter

_BaseRunner = TypeVar("_BaseRunner", bound="BaseRunner[Any]")

CHECK_BLOCK_TYPES = frozenset(["resource", "data", "provider", "module"])
OUTPUT_CHOICES = ["cli", "cyclonedx", "json", "junitxml", "github_failed_only", "sarif", "csv"]
OUTPUT_DELIMITER = "\n--- OUTPUT DELIMITER ---\n"


class RunnerRegistry:
    def __init__(self, banner: str, runner_filter: RunnerFilter, *runners: _BaseRunner) -> None:
        self.logger = logging.getLogger(__name__)
        self.runner_filter = runner_filter
        self.runners = list(runners)
        self.banner = banner
        self.scan_reports: list[Report] = []
        self.image_referencing_runners = self._get_image_referencing_runners()
        self.filter_runner_framework()
        self.tool = tool_name
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
    ) -> List[Report]:
        integration_feature_registry.run_pre_runner()
        if len(self.runners) == 1:
            reports: Iterable[Report] = [
                self.runners[0].run(root_folder, external_checks_dir=external_checks_dir, files=files,
                                    runner_filter=self.runner_filter,
                                    collect_skip_comments=collect_skip_comments)]
        else:
            def _parallel_run(runner: _BaseRunner) -> Report:
                return runner.run(
                    root_folder=root_folder,
                    external_checks_dir=external_checks_dir,
                    files=files,
                    runner_filter=self.runner_filter,
                    collect_skip_comments=collect_skip_comments,
                )

            reports = parallel_runner.run_function(func=_parallel_run, items=self.runners, group_size=1)

        for scan_report in reports:
            self._handle_report(scan_report, repo_root_for_plan_enrichment)
        return self.scan_reports

    def _handle_report(self, scan_report: Report, repo_root_for_plan_enrichment: list[str | Path] | None) -> None:
        integration_feature_registry.run_post_runner(scan_report)
        if metadata_integration.check_metadata:
            RunnerRegistry.enrich_report_with_guidelines(scan_report)
        if repo_root_for_plan_enrichment:
            enriched_resources = RunnerRegistry.get_enriched_resources(repo_root_for_plan_enrichment)
            scan_report = Report("terraform_plan").enrich_plan_report(scan_report, enriched_resources)
            scan_report = Report("terraform_plan").handle_skipped_checks(scan_report, enriched_resources)
        self.scan_reports.append(scan_report)

    def save_output_to_file(self, file_name: str, data: str, data_format: str) -> None:
        try:
            with open(file_name, 'w') as f:
                f.write(data)
            logging.info(f"\nWrote output in {data_format} format to the file '{file_name}')")
        except EnvironmentError:
            logging.error(f"\nAn error occurred while writing {data_format} results to file: {file_name}",
                          exc_info=True)

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
        cli_reports = []
        report_jsons = []
        sarif_reports = []
        junit_reports = []
        cyclonedx_reports = []
        csv_sbom_report = CSVSBOM()

        data_outputs: dict[str, str] = defaultdict(str)
        for report in scan_reports:
            if not report.is_empty():
                if "json" in config.output:
                    report_jsons.append(report.get_dict(is_quiet=config.quiet, url=url))
                if "junitxml" in config.output:
                    junit_reports.append(report)
                if "github_failed_only" in config.output:
                    data_outputs["github_failed_only"] += report.print_failed_github_md(use_bc_ids=config.output_bc_ids)
                if "sarif" in config.output:
                    sarif_reports.append(report)
                if "cli" in config.output:
                    cli_reports.append(report)
                if "cyclonedx" in config.output:
                    cyclonedx_reports.append(report)
                if "csv" in config.output:
                    git_org = ""
                    git_repository = ""
                    if 'repo_id' in config and config.repo_id is not None:
                        git_org,git_repository = config.repo_id.split('/')
                    csv_sbom_report.add_report(report=report, git_org=git_org, git_repository=git_repository)
            logging.debug(f'Getting exit code for report {report.check_type}')
            exit_codes.append(report.get_exit_code(config.soft_fail, config.soft_fail_on, config.hard_fail_on))

        if "cli" in config.output:
            cli_output = ''
            for report in cli_reports:
                cli_output += report.print_console(
                    is_quiet=config.quiet,
                    is_compact=config.compact,
                    created_baseline_path=created_baseline_path,
                    baseline=baseline,
                    use_bc_ids=config.output_bc_ids,
                )
            print(cli_output)
            # Remove colors from the cli output
            ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
            data_outputs['cli'] = ansi_escape.sub('', cli_output)
            if url:
                print("More details: {}".format(url))
            output_formats.remove("cli")
            if output_formats:
                print(OUTPUT_DELIMITER)
        if "sarif" in config.output:
            master_report = Report("merged")
            print(self.banner)
            for report in sarif_reports:
                print(report.print_console(
                    is_quiet=config.quiet,
                    is_compact=config.compact,
                    created_baseline_path=created_baseline_path,
                    baseline=baseline,
                    use_bc_ids=config.output_bc_ids,
                ))
                master_report.failed_checks += report.failed_checks
                master_report.skipped_checks += report.skipped_checks
            if url:
                print("More details: {}".format(url))
            master_report.write_sarif_output(self.tool)
            data_outputs['sarif'] = json.dumps(master_report.get_sarif_json(self.tool), cls=CustomJSONEncoder)
            output_formats.remove("sarif")
            if output_formats:
                print(OUTPUT_DELIMITER)
        if "json" in config.output:
            if config.compact and report_jsons:
                self.strip_code_blocks_from_json(report_jsons)
            if not report_jsons:
                print(dumps(Report("").get_summary(), indent=4, cls=CustomJSONEncoder))
                data_outputs['json'] = json.dumps(Report("").get_summary(), cls=CustomJSONEncoder)
            elif len(report_jsons) == 1:
                print(dumps(report_jsons[0], indent=4, cls=CustomJSONEncoder))
                data_outputs['json'] = json.dumps(report_jsons[0], cls=CustomJSONEncoder)
            else:
                print(dumps(report_jsons, indent=4, cls=CustomJSONEncoder))
                data_outputs['json'] = json.dumps(report_jsons, cls=CustomJSONEncoder)
            output_formats.remove("json")
            if output_formats:
                print(OUTPUT_DELIMITER)
        if "junitxml" in config.output:
            properties = Report.create_test_suite_properties_block(config)

            if junit_reports:
                test_suites = [
                    report.get_test_suite(properties=properties, use_bc_ids=config.output_bc_ids)
                    for report in junit_reports
                ]
            else:
                test_suites = [Report("").get_test_suite(properties=properties)]

            data_outputs['junitxml'] = Report.get_junit_xml_string(test_suites)
            print(data_outputs['junitxml'])

            output_formats.remove("junitxml")
            if output_formats:
                print(OUTPUT_DELIMITER)
        if "cyclonedx" in config.output:
            cyclonedx = CycloneDX(repo_id=metadata_integration.bc_integration.repo_id, reports=cyclonedx_reports)
            cyclonedx_output = cyclonedx.get_xml_output()

            print(cyclonedx_output)
            data_outputs["cyclonedx"] = cyclonedx_output
            output_formats.remove("cyclonedx")
            if output_formats:
                print(OUTPUT_DELIMITER)
        if "csv" in config.output:
            is_api_key = False
            if 'bc_api_key' in config and config.bc_api_key is not None:
                is_api_key = True
            csv_sbom_report.persist_report(is_api_key)

        # Save output to file
        file_names = {'cli': 'results_cli.txt',
                      'github_failed_only': 'results_github_failed_only.txt',
                      'sarif': 'results_sarif.sarif',
                      'json': 'results_json.json',
                      'junitxml': 'results_junitxml.xml',
                      'cyclonedx': 'results_cyclonedx.xml'}
        if config.output_file_path:
            for output in config.output:
                if output in file_names:
                    self.save_output_to_file(file_name=f'{config.output_file_path}/{file_names[output]}',
                                             data=data_outputs[output],
                                             data_format=output)
        exit_code = 1 if 1 in exit_codes else 0
        return cast(Literal[0, 1], exit_code)

    def print_iac_bom_reports(self, output_path: str, scan_reports: list[Report], output_types: list[str]) -> None:
        # create cyclonedx report
        if 'cyclonedx' in output_types:
            cyclonedx_output_path = 'results_cyclonedx.xml'
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
                    csv_sbom_report.add_report(report=report, git_org="", git_repository="")
            csv_sbom_report.persist_report_iac(file_name='results_iac.csv', output_path=output_path)

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
            self.runners.remove(runner)

    @staticmethod
    def enrich_report_with_guidelines(scan_report: Report) -> None:
        for record in itertools.chain(scan_report.failed_checks, scan_report.passed_checks, scan_report.skipped_checks):
            guideline = metadata_integration.get_guideline(record.check_id)
            if guideline:
                record.set_guideline(guideline)

    @staticmethod
    def get_enriched_resources(repo_roots: list[str | Path]) -> dict[str, dict[str, Any]]:
        repo_definitions = {}
        for repo_root in repo_roots:
            tf_definitions: dict[str, Any] = {}
            parsing_errors: dict[str, Exception] = {}
            Parser().parse_directory(
                directory=repo_root,  # assume plan file is in the repo-root
                out_definitions=tf_definitions,
                out_parsing_errors=parsing_errors,
            )
            repo_definitions[repo_root] = {'tf_definitions': tf_definitions, 'parsing_errors': parsing_errors}

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
            for key, result in results.items():
                for result_dict in result:
                    result_dict.pop('code_block', None)
                    result_dict.pop('connected_node', None)
