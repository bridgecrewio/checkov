from __future__ import annotations

import os
import sys
from typing import NoReturn

from colorama import Fore
from tqdm import tqdm

from checkov.common.util.type_forcers import convert_str_to_bool

DEFAULT_BAR_FORMAT = f'{{l_bar}}{Fore.WHITE}{{bar:20}}{Fore.RESET}|[{{n_fmt}}/{{total_fmt}}]{{postfix}}'
LOGS_ENABLED = os.getenv('LOG_LEVEL', False)
RUN_IN_DOCKER = convert_str_to_bool(os.getenv("RUN_IN_DOCKER", "False"))


class ProgressBar:
    def __init__(self, framework: str) -> None:
        self.pbar: tqdm[NoReturn] | None = None
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
                             bar_format=DEFAULT_BAR_FORMAT,
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

    @staticmethod
    def should_show_progress_bar() -> bool:
        # making sure sys.__stdout__ is not None, but still need the type:ignore
        if all([not LOGS_ENABLED, not RUN_IN_DOCKER, sys.__stdout__, sys.__stdout__.isatty()]):  # type:ignore[union-attr]
            return True
        return False
