from __future__ import annotations

import itertools
import logging
from enum import Enum
from typing import Iterator, TYPE_CHECKING, Any

from checkov.common.bridgecrew.check_type import CheckType

if TYPE_CHECKING:
    from checkov.common.output.record import Record
    from checkov.common.output.report import Report


class SecretsOmitterStatus(Enum):
    SUCCESS = 0
    INSUFFICIENT_REPORTS = 1


class SecretsOmitter:
    def __init__(self, reports: list[Report]):
        self.reports: list[Report] = [report for report in reports if report.check_type != CheckType.SECRETS]
        self.secrets_report: dict[str, Any] | None = self._get_secrets_report(reports)

    @staticmethod
    def _get_secrets_report(reports: list[Report]) -> dict[str, Any] | None:
        """
        Setting the secrets report from checkov runner or bucket
        """
        secrets_report_list = [report for report in reports if report.check_type == CheckType.SECRETS]
        return secrets_report_list[0].get_dict(full_report=True) if len(secrets_report_list) == 1 else None

    def _secret_check(self) -> Iterator[dict[str, Any]]:
        if not self.secrets_report:
            # Should not reach here, used for typing
            return

        for check in self.secrets_report.get("checks", {}).get("failed_checks"):
            yield check

    def _non_secret_check(self) -> Iterator[Record]:
        for report in self.reports:
            for check in itertools.chain(report.failed_checks, report.passed_checks):
                yield check

    @staticmethod
    def get_secret_lines(code_block: list[tuple[int, str]] | None) -> tuple[list[int], list[str]]:
        """
        Given a code block object, returns the lines containing asterisks including the line range
        :param code_block: list of tuples containing line number and the line itself
        :return: list of size 2, representing the range of lines containing secrets from code_block,
         and a list containing the lines from the range.
        """
        secret_lines_range = [-1, -1]
        secrets_lines: list[str] = []
        if not code_block:
            return secret_lines_range, secrets_lines

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
            return SecretsOmitterStatus.INSUFFICIENT_REPORTS

        files_with_secrets: set[str] = {secret_check.get("file_path", "") for secret_check in self._secret_check()}
        for check in self._non_secret_check():
            check_file_path = check.file_path
            check_abs_file_path = check.file_abs_path
            check_line_range = check.file_line_range

            if (check_file_path not in files_with_secrets and check_abs_file_path not in files_with_secrets)\
                    or not check_line_range or None in check_line_range:
                continue

            for secret_check in self._secret_check():
                secret_check_file_path = secret_check.get("file_path", "")
                secret_check_line_range, secrets_check_lines = self.get_secret_lines(secret_check.get("code_block"))
                if secret_check_line_range == [-1, -1]:
                    continue

                if secret_check_file_path not in (check_file_path, check_abs_file_path) or \
                        not self._line_range_overlaps(secret_check_line_range, check_line_range):
                    continue

                if len(secrets_check_lines) != secret_check_line_range[1] - secret_check_line_range[0] + 1:
                    logging.error("Secrets lines does not match the length of the line range, sanity check failed")
                    continue

                for secret_line_index, omitted_line in \
                        zip(list(range(secret_check_line_range[0], secret_check_line_range[1] + 1)),  # noqa: B905
                            secrets_check_lines):
                    for entry_index, (line_index, _) in enumerate(check.code_block):
                        if secret_line_index == line_index:
                            check.code_block[entry_index] = (line_index, omitted_line)

        return SecretsOmitterStatus.SUCCESS
