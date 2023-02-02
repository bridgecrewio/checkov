from __future__ import annotations
from dataclasses import dataclass

import logging
import semgrep.output_from_core as core
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.report import Report
from checkov.runner_filter import RunnerFilter
from checkov.common.output.record import Record
from semgrep.semgrep_main import main as run_semgrep
from semgrep.output import OutputSettings, OutputHandler
from semgrep.constants import OutputFormat, RuleSeverity
from semgrep.rule_match import RuleMatchMap
from semgrep.target_manager import FileTargetingLog
from semgrep.profile_manager import ProfileManager
from semgrep.profiling import ProfilingData
from semgrep.parsing_data import ParsingData
from semgrep.error import SemgrepError
from semgrep.rule import Rule

from typing import Collection, List, Set, Dict
from io import StringIO
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SemgrepOutput:
    matches: RuleMatchMap = None
    errors: List[SemgrepError] = []
    all_targets: Set[Path] = set()
    renamed_targets: Set[Path] = set()
    target_manager_ignore_log: FileTargetingLog = None
    filtered_rules: List[Rule] = []
    profiler: ProfileManager = None
    profiling_data: ProfilingData = None
    parsing_data: ParsingData = None
    explanations: List[core.MatchingExplanation] = []
    shown_severities: Collection[RuleSeverity] = None
    target_manager_lockfile_scan_info:  Dict[str, int] = {}



class Runner():
    check_type = CheckType.SAST  # noqa: CCE003  # a static attribute

    def run(self, root_folder: str | None, external_checks_dir: list[str] | None = None, files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None, collect_skip_comments: bool = True) -> Report:
        report = Report(self.check_type)

        output_settings = OutputSettings(output_format=OutputFormat.JSON)
        StringIO()
        output_handler = OutputHandler(output_settings)

        if root_folder:
            targets = [root_folder]
        if files:
            targets = files

        config = runner_filter.sast_config
        
        semgrep_output = Runner._get_semgrep_output(targets=targets, config=config, output_handler=output_handler)

        record = Record(check_id=None, bc_check_id=None, check_name=None, check_result=None, code_block=None,
                        file_path=None, file_line_range=None, resource=None, evaluations=None, check_class=None,
                        file_abs_path=None, entity_tags=None, severity=None)

        return report

    @staticmethod
    def _get_semgrep_output(targets, config, output_handler) -> SemgrepOutput:
        (filtered_matches_by_rule,
         semgrep_errors,
         all_targets,
         renamed_targets,
         target_manager_ignore_log,
         filtered_rules,
         profiler,
         profiling_data,
         parsing_data,
         explanations,
         shown_severities,
         target_manager_lockfile_scan_info) = run_semgrep(output_handler=output_handler, target=targets,
                                                          pattern="", lang="", configs=config, **{})
        semgrep_output = SemgrepOutput(filtered_matches_by_rule, semgrep_errors, all_targets, renamed_targets,
                                       target_manager_ignore_log, filtered_rules, profiler, profiling_data,
                                       parsing_data, explanations, shown_severities, target_manager_lockfile_scan_info)
        return semgrep_output
