from __future__ import annotations

import os
import sys

from checkov.common.output.report import CheckType
from colorama import Fore, Back
from tqdm import tqdm  # type: ignore

DEFAULT_BAR_FORMAT = f'{{l_bar}}{Fore.WHITE}{{bar:20}}{Fore.RESET}|[{{n_fmt}}/{{total_fmt}}]{{postfix}}'
SLOW_RUNNER_BAR_FORMAT = f'{{l_bar}}{Fore.LIGHTBLACK_EX}{{bar:20}}{Fore.RESET}|[{{n_fmt}}/{{total_fmt}}]' \
                         f' {Back.YELLOW}[Slow Runner Warning]{Back.RESET}{{postfix}}'
SLOW_RUNNERS = {CheckType.SCA_PACKAGE, CheckType.TERRAFORM, CheckType.CLOUDFORMATION, CheckType.HELM,
                CheckType.KUBERNETES, CheckType.KUSTOMIZE, CheckType.SECRETS}
DISABLED_PROGRESS_BARS = {CheckType.SECRETS}
LOGS_ENABLED = os.getenv('LOG_LEVEL', False)


class ProgressBar:
    def __init__(self, framework: str) -> None:
        self.pbar = None
        self.framework = framework
        self.is_off = not self.should_show_progress_bar()

    def initiate(self, total: int) -> None:
        if total <= 0:
            self.is_off = True

        if self.is_off:
            return

        if self.pbar is not None:
            self.pbar.reset(total)
        else:
            self.pbar = tqdm(total=total,
                             bar_format=self.get_progress_bar_format(self.framework),
                             desc=f'[ {self.framework} framework ]')

    def update(self, value: int = 1) -> None:
        if self.is_off:
            return
        if not self.pbar:
            raise AttributeError('Progress bar was not initiated, cannot update')

        self.pbar.update(value)

    def set_description(self, desc: str) -> None:
        if self.is_off:
            return
        if not self.pbar:
            raise AttributeError('Progress bar was not initiated, cannot set description')

        self.pbar.set_description(desc=desc)

    def close(self) -> None:
        if self.is_off:
            return
        if not self.pbar:
            raise AttributeError('Progress bar was not initiated, cannot close')

        self.pbar.close()

    def set_additional_data(self, data: dict[str, str]) -> None:
        if self.is_off:
            return
        if not self.pbar:
            raise AttributeError('Progress bar was not initiated, cannot set additional data')

        self.pbar.set_postfix(data)

    def turn_off_progress_bar(self) -> None:
        self.is_off = True

    def should_show_progress_bar(self) -> bool:
        if all([not LOGS_ENABLED, sys.__stdout__.isatty(), self.framework not in DISABLED_PROGRESS_BARS]):
            return True
        return False

    @staticmethod
    def get_progress_bar_format(framework: str) -> str:
        if framework in SLOW_RUNNERS:
            return SLOW_RUNNER_BAR_FORMAT
        return DEFAULT_BAR_FORMAT
