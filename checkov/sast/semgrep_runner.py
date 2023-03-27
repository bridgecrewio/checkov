from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import List, TYPE_CHECKING, Set, Collection, Dict
from checkov.sast.common import get_code_block
from checkov.common.output.report import Report
from checkov.common.bridgecrew.severities import get_severity
from checkov.sast.consts import SEMGREP_SEVERITY_TO_CHECKOV_SEVERITY
from checkov.common.typing import _CheckResult
from checkov.common.models.enums import CheckResult


if not sys.platform.startswith('win'):
    # TODO: Enable SAST for windows runners
    from semgrep.semgrep_main import main as run_semgrep

if TYPE_CHECKING:
    from semgrep.rule_match import RuleMatchMap, RuleMatch
    from semgrep.target_manager import FileTargetingLog
    from semgrep.profile_manager import ProfileManager
    from semgrep.output_extra import OutputExtra
    from semgrep.error import SemgrepError
    from semgrep.rule import Rule
    if not sys.platform.startswith('win'):
        from semgrep.output import OutputHandler
        from semgrep.constants import RuleSeverity

from pathlib import Path
from checkov.sast.record import SastRecord


@dataclass
class SemgrepOutput:
    matches: RuleMatchMap
    errors: List[SemgrepError]
    renamed_targets: Set[Path]
    target_manager_ignore_log: FileTargetingLog
    filtered_rules: List[Rule]
    profiler: ProfileManager
    outputExtra: OutputExtra
    shown_severities: Collection[RuleSeverity]
    target_manager_lockfile_scan_info: Dict[str, int]


def get_semgrep_output(targets: List[str], config: List[str], output_handler: OutputHandler) -> SemgrepOutput:
    (filtered_matches_by_rule,
     semgrep_errors,
     renamed_targets,
     target_manager_ignore_log,
     filtered_rules,
     profiler,
     output_extra,
     shown_severities,
     target_manager_lockfile_scan_info) = run_semgrep(output_handler=output_handler, target=targets,
                                                      pattern="", lang="", configs=config, **{})
    semgrep_output = SemgrepOutput(filtered_matches_by_rule, semgrep_errors, renamed_targets,
                                   target_manager_ignore_log, filtered_rules, profiler,
                                   output_extra, shown_severities, target_manager_lockfile_scan_info)
    return semgrep_output


def create_report(check_type: str, lang: str, semgrep_matches: List[RuleMatch]) -> Report:
    report = Report(f'{check_type}_{lang}')
    for match in semgrep_matches:
        check_id = match.rule_id.split('.')[-1]
        check_name = match.metadata.get('name', '')
        check_cwe = match.metadata.get('cwe')
        check_owasp = match.metadata.get('owasp')
        code_block = get_code_block(match.lines, match.start.line)
        file_abs_path = match.match.location.path
        file_path = file_abs_path.split('/')[-1]
        severity = get_severity(SEMGREP_SEVERITY_TO_CHECKOV_SEVERITY.get(match.severity))
        file_line_range = [match.start.line, match.end.line]
        check_result = _CheckResult(result=CheckResult.FAILED)

        record = SastRecord(check_id=check_id, check_name=check_name, resource="", evaluations={},
                            check_class="", check_result=check_result, code_block=code_block,
                            file_path=file_path, file_line_range=file_line_range,
                            file_abs_path=file_abs_path, severity=severity, cwe=check_cwe, owasp=check_owasp)
        report.add_record(record)
    return report
