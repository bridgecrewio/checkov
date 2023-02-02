from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from checkov.common.checks.base_check import BaseCheck
from checkov.common.util.tqdm_utils import ProgressBar

from checkov.common.output.report import Report
from checkov.policies_3d.checks_infra.base_check import Base3dPolicyCheck
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from checkov.common.graph.graph_manager import GraphManager  # noqa


class BasePostRunner(ABC):
    check_type = ''  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        self.pbar = ProgressBar(self.check_type)

    @abstractmethod
    def run(
            self,
            checks: list[BaseCheck | Base3dPolicyCheck],
            scan_reports: list[Report],
            runner_filter: RunnerFilter | None = None
    ) -> Report:
        raise NotImplementedError()
