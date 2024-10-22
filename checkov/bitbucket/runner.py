from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.bitbucket.dal import Bitbucket
from checkov.common.bridgecrew.check_type import CheckType
from checkov.json_doc.runner import Runner as JsonRunner
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from checkov.common.output.report import Report


class Runner(JsonRunner):
    check_type = CheckType.BITBUCKET_CONFIGURATION  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        self.bitbucket = Bitbucket()
        super().__init__()

    def run(
        self,
        root_folder: str | None = None,
        external_checks_dir: list[str] | None = None,
        files: list[str] | None = None,
        runner_filter: RunnerFilter | None = None,
        collect_skip_comments: bool = True
    ) -> Report | list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

        self.prepare_data()

        report = super().run(
            root_folder=self.bitbucket.bitbucket_conf_dir_path,
            external_checks_dir=external_checks_dir,
            files=None,  # ignore file scans
            runner_filter=runner_filter,
            collect_skip_comments=collect_skip_comments,
        )

        return report

    def prepare_data(self) -> None:
        self.bitbucket.persist_all_confs()

    def require_external_checks(self) -> bool:
        # default json runner require only external checks. Bitbucket runner brings build in checks
        return False

    def import_registry(self) -> BaseCheckRegistry:
        from checkov.bitbucket.registry import registry
        return registry
