from __future__ import annotations
import logging
from enum import Enum
from typing import Iterator

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.record import Record
from checkov.common.output.report import Report


class SecretsOmitterStatus(Enum):
    Success = 0
    InsufficientReports = 1
    Failed = 2


class SecretsOmitter:
    def __init__(self, reports: list[Report]):
        self.reports: list[Report] = [report for report in reports if report.check_type != CheckType.SECRETS]
        secrets_report = [report for report in reports if report.check_type == CheckType.SECRETS]
        self.secrets_report: Report | None = secrets_report[0] if len(secrets_report) == 1 else None

    def _secret_check(self) -> Iterator[Record]:
        if not self.secrets_report:
            # Should not reach here, used for typing
            return

        for check in self.secrets_report.failed_checks:
            yield check

    def _non_secret_check(self) -> Iterator[Record]:
        for report in self.reports:
            checks = report.failed_checks + report.passed_checks
            for check in checks:
                yield check

    @staticmethod
    def get_secret_lines(code_block: list[tuple[int, str]]) -> tuple[list[int], list[str]]:
        secret_lines_range = [-1, -1]
        secrets_lines = []
        for idx, line in code_block:
            if '*' in line:
                secrets_lines.append(line)
                if secret_lines_range[0] == -1:
                    secret_lines_range[0] = idx
                else:
                    secret_lines_range[1] = idx
        if secret_lines_range[1] == -1:
            secret_lines_range[1] = secret_lines_range[0]

        return secret_lines_range, secrets_lines

    @staticmethod
    def _line_range_overlaps(r1: list[int], r2: list[int]) -> bool:
        return r1[0] <= r2[1] and r1[1] >= r2[0]

    def omit(self) -> SecretsOmitterStatus:
        if not self.reports or not self.secrets_report:
            logging.debug("Insufficient reports to omit secrets")
            return SecretsOmitterStatus.InsufficientReports

        for secret_check in self._secret_check():
            secret_check_file_path = secret_check.file_path
            secret_check_line_range, secrets_check_lines = SecretsOmitter.get_secret_lines(secret_check.code_block)
            if secret_check_line_range == [-1, -1]:
                continue

            for check in self._non_secret_check():
                check_file_path = check.file_path
                check_line_range = check.file_line_range

                if secret_check_file_path != check_file_path or \
                        not SecretsOmitter._line_range_overlaps(secret_check_line_range, check_line_range):
                    continue

                for secret_line_index, omitted_line in \
                        zip(range(secret_check_line_range[0], secret_check_line_range[1] + 1), secrets_check_lines):
                    for entry_index, (line_index, _) in enumerate(check.code_block):
                        if secret_line_index == line_index:
                            check.code_block[entry_index] = (line_index, omitted_line)

        return SecretsOmitterStatus.Success
