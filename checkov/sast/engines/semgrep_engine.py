from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from io import StringIO
from typing import List, TYPE_CHECKING, Set, Collection, Dict, Any

from checkov.common.bridgecrew.check_type import CheckType
from checkov.sast.checks_infra.base_registry import Registry
from checkov.sast.common import get_code_block
from checkov.common.output.report import Report
from checkov.common.bridgecrew.severities import get_severity
from checkov.sast.consts import SEMGREP_SEVERITY_TO_CHECKOV_SEVERITY, SastLanguages, FILE_EXT_TO_SAST_LANG
from checkov.common.typing import _CheckResult
from checkov.common.models.enums import CheckResult
from checkov.sast.engines.base_engine import SastEngine

if not sys.platform.startswith('win'):
    # TODO: Enable SAST for windows runners
    from semgrep.output import OutputSettings, OutputHandler
    from semgrep.constants import OutputFormat, EngineType, DEFAULT_TIMEOUT, RuleSeverity
    from semgrep.core_runner import StreamingSemgrepCore, SemgrepCore, CoreRunner
    from semgrep.semgrep_main import main as run_semgrep

if TYPE_CHECKING:
    from semgrep.rule_match import RuleMatchMap, RuleMatch
    from semgrep.target_manager import FileTargetingLog
    from semgrep.profile_manager import ProfileManager
    from semgrep.output_extra import OutputExtra
    from semgrep.error import SemgrepError
    from semgrep.rule import Rule

from pathlib import Path
from checkov.sast.record import SastRecord

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


class SemgrepEngine(SastEngine):

    def __init__(self) -> None:
        self.check_type = CheckType.SAST

    def get_reports(self, targets: List[str], registry: Registry, languages: Set[SastLanguages]) -> List[Report]:

        # load checks
        loaded_checks = registry.load_semgrep_checks(languages)
        if not loaded_checks:
            logger.warning('No valid rules were found for SAST')
            return [Report(self.check_type)]

        registry.create_temp_rules_file()
        config = [registry.temp_semgrep_rules_path]
        if not config:
            logger.warning('no valid checks')
            return [Report(self.check_type)]

        StringIO()
        output_settings = OutputSettings(output_format=OutputFormat.JSON)
        output_handler = OutputHandler(output_settings)

        semgrep_output = self.get_semgrep_output(targets=targets, config=config, output_handler=output_handler)
        semgrep_results_by_language: Dict[str, List[RuleMatch]] = {}
        for matches in semgrep_output.matches.values():
            for rule_match in matches:
                match_lang = FILE_EXT_TO_SAST_LANG.get(rule_match.path.suffix.lstrip('.'), '')
                if not match_lang or not isinstance(match_lang, SastLanguages):  # 2nd condition for typing
                    raise TypeError(f'file type {rule_match.path.suffix} is not supported by sast framework')
                semgrep_results_by_language.setdefault(match_lang.value, []).append(rule_match)

        # add empty reports for checked languages without findings
        for target in targets:
            suffix = target.rsplit(".", maxsplit=1)
            if len(suffix) == 2:
                match_lang_extra = FILE_EXT_TO_SAST_LANG.get(suffix[1])
                if match_lang_extra and match_lang_extra.value not in semgrep_results_by_language:
                    semgrep_results_by_language[match_lang_extra.value] = []

        registry.delete_temp_rules_file()

        reports = []
        for language, results in semgrep_results_by_language.items():
            if isinstance(results, list):
                reports.append(self.create_report(self.check_type, language, results))
        return reports

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

    def get_semgrep_output(self, targets: List[str], config: List[str], output_handler: OutputHandler) -> SemgrepOutput:
        semgrep_result = run_semgrep(output_handler=output_handler, target=targets,
                                     pattern="", lang="", configs=config, **{})

        (filtered_matches_by_rule,
         semgrep_errors,
         renamed_targets,
         target_manager_ignore_log,
         filtered_rules,
         profiler,
         output_extra,
         shown_severities,
         target_manager_lockfile_scan_info) = semgrep_result

        semgrep_output = SemgrepOutput(filtered_matches_by_rule, semgrep_errors, renamed_targets,
                                       target_manager_ignore_log, filtered_rules, profiler,
                                       output_extra, shown_severities, target_manager_lockfile_scan_info)
        return semgrep_output

    def create_report(self, check_type: str, lang: str, semgrep_matches: List[RuleMatch]) -> Report:
        report = Report(f'{check_type}_{lang}')
        for match in semgrep_matches:
            check_id = match.rule_id.split('.')[-1]
            check_id = check_id.rsplit("_", maxsplit=1)[0]  # remove the added language suffix, ex. CKV_AWS_21_python
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
                                file_abs_path=file_abs_path, severity=severity, cwe=check_cwe, owasp=check_owasp,
                                show_severity=True)

            report.add_record(record)

        return report
