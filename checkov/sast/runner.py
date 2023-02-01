from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Any, Callable, TYPE_CHECKING  # noqa: F401  # Callable is used in the TypeAlias
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.report import Report
from semgrep.semgrep_main import main as run_semgrep
from semgrep.output import OutputSettings
from semgrep.constants import OutputFormat
from semgrep.output import OutputHandler
from io import StringIO

if TYPE_CHECKING:
    from typing_extensions import TypeAlias


logger = logging.getLogger(__name__)


class Runner():
    check_type = CheckType.SAST  # noqa: CCE003  # a static attribute

    def run(self, root_folder: str | None, external_checks_dir: list[str] | None = None, files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None, collect_skip_comments: bool = True) -> Report:
        report = Report(self.check_type)

        output_settings = OutputSettings(output_format=OutputFormat.JSON)
        StringIO()
        output_handler = OutputHandler(output_settings)

        if root_folder:
            # targets = ['/Users/arosenfeld/Desktop/fff/bb.py']
            targets = [root_folder]
        if files:
            targets = files

        # config = ['/Users/arosenfeld/Desktop/dev/semgrep/rule.yaml']
        config = runner_filter.sast_config

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

        record = Record(check_id=check.id, bc_check_id=check.bc_id, check_name=check.name,
                        check_result=check_result,
                        code_block=censored_code_lines, file_path=sls_file,
                        file_line_range=entity_lines_range,
                        resource=cf_resource_id, evaluations=variable_evaluations,
                        check_class=check.__class__.__module__, file_abs_path=file_abs_path,
                        entity_tags=tags, severity=check.severity)

        return report