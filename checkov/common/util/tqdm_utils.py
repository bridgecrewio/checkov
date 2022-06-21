import os
import sys

from colorama import Fore, Back
from tqdm import tqdm  # type: ignore

DEFAULT_BAR_FORMAT = '{l_bar}%s{bar:20}%s|[{n_fmt}/{total_fmt}]{postfix}' % (Fore.WHITE, Fore.RESET)
SLOW_RUNNER_BAR_FORMAT = '{l_bar}%s{bar:20}%s|[{n_fmt}/{total_fmt}] %s[Slow Runner Warning]%s{postfix}' %\
                         (Fore.LIGHTBLACK_EX, Fore.RESET, Back.YELLOW, Back.RESET)

SLOW_RUNNERS = {'sca_package', 'terraform', 'cloudformation', 'helm', 'kubernetes', 'kustomize', 'secrets'}
LOGS_ENABLED = os.environ.get('LOG_LEVEL', False)


class ProgressBar:
    def __init__(self, framework: str) -> None:
        self.pbar = None
        self.is_off = not self.should_show_progress_bar()
        self.framework = framework

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
        self.pbar.update(value)  # type: ignore

    def set_description(self, desc: str) -> None:
        if self.is_off:
            return
        self.pbar.set_description(desc=desc)  # type: ignore

    def close(self) -> None:
        if self.is_off:
            return
        self.pbar.close()  # type: ignore

    def set_additional_data(self, data: dict[str, str]) -> None:
        if self.is_off:
            return
        self.pbar.set_postfix(data)  # type: ignore

    def turn_off_progress_bar(self) -> None:
        self.is_off = True

    @staticmethod
    def should_show_progress_bar() -> bool:
        if all([not LOGS_ENABLED, sys.__stdout__.isatty()]):
            return True
        return False

    @staticmethod
    def get_progress_bar_format(framework: str) -> str:
        if framework in SLOW_RUNNERS:
            return SLOW_RUNNER_BAR_FORMAT
        return DEFAULT_BAR_FORMAT
