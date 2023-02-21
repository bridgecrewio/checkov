from __future__ import annotations

import logging
from dataclasses import dataclass
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import get_severity
from checkov.common.models.enums import CheckResult
from checkov.common.output.report import Report
from checkov.common.typing import _CheckResult
from checkov.runner_filter import RunnerFilter
from checkov.sast.checks.registry import registry
from checkov.sast.consts import SastLanguages, SUPPORT_FILE_EXT, SEMGREP_SEVERITY_TO_CHECKOV_SEVERITY, \
    FILE_EXT_TO_SAST_LANG
from semgrep.semgrep_main import main as run_semgrep
from semgrep.output import OutputSettings, OutputHandler
from semgrep.constants import OutputFormat, RuleSeverity, EngineType, DEFAULT_TIMEOUT
from semgrep.core_runner import StreamingSemgrepCore, SemgrepCore, CoreRunner
from typing import Collection, List, Set, Dict, Tuple, Optional, Any, TYPE_CHECKING
from io import StringIO
from pathlib import Path

from checkov.sast.record import SastRecord

if TYPE_CHECKING:
    from semgrep.rule_match import RuleMatchMap, RuleMatch
    from semgrep.target_manager import FileTargetingLog
    from semgrep.profile_manager import ProfileManager
    from semgrep.output_extra import OutputExtra
    from semgrep.error import SemgrepError
    from semgrep.rule import Rule

logger = logging.getLogger(__name__)


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


class Runner():
    check_type = CheckType.SAST  # noqa: CCE003  # a static attribute

    def should_scan_file(self, file: str) -> bool:
        for extensions in SUPPORT_FILE_EXT.values():
            for extension in extensions:
                if file.endswith(extension):
                    return True
        return False

    def run(self, root_folder: Optional[str], external_checks_dir: Optional[List[str]] = None,
            files: Optional[List[str]] = None,
            runner_filter: Optional[RunnerFilter] = None, collect_skip_comments: bool = True) -> list[Report]:
        if not runner_filter:
            logger.warning('no runner filter')
            return [Report(self.check_type)]

        StringIO()
        output_settings = OutputSettings(output_format=OutputFormat.JSON)
        output_handler = OutputHandler(output_settings)

        registry.set_runner_filter(runner_filter)
        registry.load_rules(runner_filter.sast_languages)
        if external_checks_dir:
            for external_checks in external_checks_dir:
                registry.load_external_rules(external_checks, runner_filter.sast_languages)
        registry.create_temp_rules_file()
        config = [registry.temp_semgrep_rules_path]
        if not config:
            logger.warning('no valid checks')
            return [Report(self.check_type)]

        if root_folder:
            targets = [root_folder]
        if files:
            targets = files

        semgrep_output = Runner._get_semgrep_output(targets=targets, config=config, output_handler=output_handler)
        semgrep_results_by_language: Dict[str, List[RuleMatch]] = {}
        for matches in semgrep_output.matches.values():
            for rule_match in matches:
                match_lang = FILE_EXT_TO_SAST_LANG.get(rule_match.path.suffix.lstrip('.'), '')
                if not match_lang or not isinstance(match_lang, SastLanguages):  # 2nd condition for typing
                    raise TypeError(f'file type {rule_match.path.suffix} is not supported by sast framework')
                semgrep_results_by_language.setdefault(match_lang.value, []).append(rule_match)

        registry.delete_temp_rules_file()

        reports = []
        for language, results in semgrep_results_by_language.items():
            if results:
                reports.append(self._create_report(language, results))

        return reports

    @staticmethod
    def _get_semgrep_output(targets: List[str], config: List[str], output_handler: OutputHandler) -> SemgrepOutput:
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

    def _create_report(self, lang: str, semgrep_matches: List[RuleMatch]) -> Report:
        report = Report(f'{self.check_type}_{lang}')
        for match in semgrep_matches:
            check_id = match.rule_id.split('.')[-1]
            check_name = match.metadata.get('name', '')
            check_cwe = match.metadata.get('cwe')
            check_owasp = match.metadata.get('owasp')
            code_block = Runner._get_code_block(match.lines, match.start.line)
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

    @staticmethod
    def _get_code_block(lines: List[str], start: int) -> List[Tuple[int, str]]:
        code_block = [(index, line) for index, line in enumerate(lines, start=start)]
        return Runner._cut_code_block_ident(code_block)

    @staticmethod
    def _cut_code_block_ident(code_block: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
        min_ident = len(code_block[0][1]) - len(code_block[0][1].lstrip())
        for item in code_block[1:]:
            current_min_ident = len(item[1]) - len(item[1].lstrip())
            if current_min_ident < min_ident:
                min_ident = current_min_ident

        if min_ident == 0:
            return code_block

        code_block_cut_ident = []
        for item in code_block:
            code_block_cut_ident.append((item[0], item[1][min_ident:]))
        return code_block_cut_ident

    @staticmethod
    def _get_generic_ast(language: SastLanguages, target: str) -> Dict[str, Any]:
        try:
            core_runner = CoreRunner(jobs=None, engine=EngineType.OSS, timeout=DEFAULT_TIMEOUT, max_memory=0,
                                     interfile_timeout=0, timeout_threshold=0, optimizations="none", core_opts_str=None)
            cmd = [SemgrepCore.path(), '-json', '-full_token_info', '-dump_ast', target, '-lang', language.value]
            runner = StreamingSemgrepCore(cmd, 1)
            runner.vfs_map = {}
            returncode = runner.execute()
            output_json: Dict[str, Any] = core_runner._extract_core_output([], returncode, " ".join(cmd), runner.stdout,
                                                                           runner.stderr)
            return output_json
        except Exception:
            logger.error(f'Cant parse AST for this file: {target}, for {language.value}', exc_info=True)
        return {}
