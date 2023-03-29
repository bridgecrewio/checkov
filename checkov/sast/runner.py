from __future__ import annotations

import logging
import os
import pathlib
import sys

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.report import Report
from checkov.runner_filter import RunnerFilter
from checkov.sast.checks_infra.base_registry import Registry
from checkov.sast.consts import SastLanguages, SUPPORT_FILE_EXT, FILE_EXT_TO_SAST_LANG


if not sys.platform.startswith('win'):
    # TODO: Enable SAST for windows runners
    from semgrep.output import OutputSettings, OutputHandler
    from semgrep.constants import OutputFormat, EngineType, DEFAULT_TIMEOUT
    from semgrep.core_runner import StreamingSemgrepCore, SemgrepCore, CoreRunner
from typing import List, Dict, Optional, Any, TYPE_CHECKING
from io import StringIO

from .semgrep_runner import get_semgrep_output, create_report

if TYPE_CHECKING:
    from semgrep.rule_match import RuleMatch

logger = logging.getLogger(__name__)


CHECKS_DIR = (os.path.join(pathlib.Path(__file__).parent.resolve(), 'checks'))


CURRENT_ENGINE = 'semgrep'  # todo: cli flag ?


class Runner():
    check_type = CheckType.SAST  # noqa: CCE003  # a static attribute
    engine = CURRENT_ENGINE  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        self.registry = Registry(checks_dir=CHECKS_DIR)

    def should_scan_file(self, file: str) -> bool:
        for extensions in SUPPORT_FILE_EXT.values():
            for extension in extensions:
                if file.endswith(extension):
                    return True
        return False

    def run(self, root_folder: Optional[str], external_checks_dir: Optional[List[str]] = None,
            files: Optional[List[str]] = None,
            runner_filter: Optional[RunnerFilter] = None, collect_skip_comments: bool = True) -> list[Report]:

        if sys.platform.startswith('win'):
            # TODO: Enable SAST for windows runners
            return [Report(self.check_type)]

        if not runner_filter:
            logger.warning('no runner filter')
            return [Report(self.check_type)]

        StringIO()
        output_settings = OutputSettings(output_format=OutputFormat.JSON)
        output_handler = OutputHandler(output_settings)

        self.registry.set_runner_filter(runner_filter)
        rules_loaded = self.registry.load_rules(runner_filter.framework, runner_filter.sast_languages)

        if external_checks_dir:
            for external_checks in external_checks_dir:
                rules_loaded += self.registry.load_external_rules(external_checks, runner_filter.sast_languages)

        if not rules_loaded:
            logger.warning('No valid rules were found for SAST')
            return [Report(self.check_type)]

        self.registry.create_temp_rules_file()
        config = [self.registry.temp_semgrep_rules_path]
        if not config:
            logger.warning('no valid checks')
            return [Report(self.check_type)]

        targets = []
        if root_folder:
            targets = [root_folder]
        elif files:
            targets = files

        reports = []
        if self.engine == 'semgrep':
            reports = self.get_semgrep_reports(targets, config, output_handler)
        else:
            pass  # todo run go runner

        return reports

    def get_semgrep_reports(self, targets: List[str], config: List[str], output_handler: OutputHandler) -> list[Report]:
        semgrep_output = get_semgrep_output(targets=targets, config=config, output_handler=output_handler)
        semgrep_results_by_language: Dict[str, List[RuleMatch]] = {}
        for matches in semgrep_output.matches.values():
            for rule_match in matches:
                match_lang = FILE_EXT_TO_SAST_LANG.get(rule_match.path.suffix.lstrip('.'), '')
                if not match_lang or not isinstance(match_lang, SastLanguages):  # 2nd condition for typing
                    raise TypeError(f'file type {rule_match.path.suffix} is not supported by sast framework')
                semgrep_results_by_language.setdefault(match_lang.value, []).append(rule_match)

        self.registry.delete_temp_rules_file()

        reports = []
        for language, results in semgrep_results_by_language.items():
            if results:
                reports.append(create_report(self.check_type, language, results))
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
