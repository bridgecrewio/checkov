from __future__ import annotations

import logging
from pathlib import Path

from checkov.cdk.checks_infra.base_registry import BaseCdkRegistry
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.report import Report
from checkov.common.sast.consts import CDKLanguages
from checkov.sast.runner import Runner as SastRunner
from checkov.runner_filter import RunnerFilter

logger = logging.getLogger(__name__)

CHECKS_DIR_PATH = Path(__file__).parent / "checks"


class CdkRunner(SastRunner):
    check_type = CheckType.CDK  # noqa: CCE003  # a static attribute

    def __init__(self,) -> None:
        super().__init__()
        self.registry = BaseCdkRegistry(checks_dir=str(CHECKS_DIR_PATH))

    def run(
        self,
        root_folder: str | None = None,
        external_checks_dir: list[str] | None = None,
        files: list[str] | None = None,
        runner_filter: RunnerFilter | None = None,
        collect_skip_comments: bool = True,
    ) -> list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        runner_filter.remove_default_sast_policies = True

        for lang in CDKLanguages.set():
            self.cdk_langs.append(lang)

        reports = super().run(
            root_folder=root_folder,
            external_checks_dir=external_checks_dir,
            files=files,
            runner_filter=runner_filter,
            collect_skip_comments=collect_skip_comments,
        )

        reports_to_keep = []
        for report in reports:
            if report.check_type.startswith('cdk'):
                reports_to_keep.append(report)

        return reports_to_keep
