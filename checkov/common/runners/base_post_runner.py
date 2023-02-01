from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from checkov.common.util.tqdm_utils import ProgressBar

from checkov.common.output.report import Report
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from checkov.common.checks.base_check import BaseCheck  # noqa
    from checkov.policies3d.checks_infra.base_check import Base3dPolicyCheck  # noqa

_Check = TypeVar("_Check", bound="BaseCheck|Base3dPolicyCheck")


class BasePostRunner(ABC, Generic[_Check]):
    check_type = ''  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        self.pbar = ProgressBar(self.check_type)

    @abstractmethod
    def run(
            self,
            checks: list[_Check] | None = None,
            scan_reports: list[Report] | None = None,
            runner_filter: RunnerFilter | None = None
    ) -> Report:
        raise NotImplementedError()
