from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Union, List, Tuple, Optional, Dict, Any

from colorama import init, Fore, Style
from termcolor import colored

from checkov.common.bridgecrew.severities import Severity
from checkov.common.models.enums import CheckResult
from checkov.common.typing import _CheckResult
from checkov.common.util.file_utils import convert_to_unix_path
from checkov.common.util.type_forcers import force_int

init(autoreset=True)

ANSI_COLORS_DISABLED = bool(os.getenv('ANSI_COLORS_DISABLED'))
CURRENT_LOCAL_DRIVE = Path.cwd().drive
DEFAULT_SEVERITY = "none"  # equivalent to a score of 0.0 in the CVSS v3.0 Ratings
OUTPUT_CODE_LINE_LIMIT = force_int(os.getenv('CHECKOV_OUTPUT_CODE_LINE_LIMIT')) or 50

SCA_PACKAGE_SCAN_CHECK_NAME = "SCA package scan"
SCA_LICENSE_CHECK_NAME = "SCA license"


class Record:
    def __init__(
        self,
        check_id: str,
        check_name: str,
        check_result: _CheckResult,
        code_block: List[Tuple[int, str]],
        file_path: str,
        file_line_range: List[int],
        resource: str,
        evaluations: Optional[Dict[str, Any]],
        check_class: str,
        file_abs_path: str,
        entity_tags: Optional[Dict[str, str]] = None,
        caller_file_path: Optional[str] = None,
        caller_file_line_range: Optional[Tuple[int, int]] = None,
        bc_check_id: Optional[str] = None,
        resource_address: Optional[str] = None,
        severity: Optional[Severity] = None,
        bc_category: Optional[str] = None,
        benchmarks: dict[str, list[str]] | None = None,
        description: Optional[str] = None,
        short_description: Optional[str] = None,
        vulnerability_details: Optional[Dict[str, Any]] = None,
        connected_node: Optional[Dict[str, Any]] = None,
        details: Optional[List[str]] = None,
        check_len: int | None = None,
        definition_context_file_path: Optional[str] = None
    ) -> None:
        """
        :param evaluations: A dict with the key being the variable name, value being a dict containing:
                             - 'var_file'
                             - 'value'
                             - 'definitions', a list of dicts which contain 'definition_expression'
        """
        self.check_id = check_id
        self.bc_check_id = bc_check_id
        self.check_name = check_name
        self.check_result = check_result
        self.code_block = code_block
        self.file_path = file_path
        self.file_abs_path = file_abs_path
        self.repo_file_path = self._determine_repo_file_path(file_abs_path)
        self.file_line_range = file_line_range
        self.resource = resource
        self.evaluations = evaluations
        self.check_class = check_class
        self.fixed_definition = None
        self.entity_tags = entity_tags
        self.caller_file_path = caller_file_path  # When created from a module
        self.caller_file_line_range = caller_file_line_range  # When created from a module
        self.resource_address = resource_address
        self.severity = severity
        self.bc_category = bc_category
        self.benchmarks = benchmarks
        self.description = description  # used by SARIF output
        self.short_description = short_description  # used by SARIF and GitLab SAST output
        self.vulnerability_details = vulnerability_details  # Stores package vulnerability details
        self.connected_node = connected_node
        self.guideline: str | None = None
        self.details: List[str] = details or []
        self.check_len = check_len
        self.definition_context_file_path = definition_context_file_path

    @staticmethod
    def _determine_repo_file_path(file_path: Union[str, "os.PathLike[str]"]) -> str:
        # matches file paths given in the BC platform and should always be a unix path
        repo_file_path = Path(file_path)
        if CURRENT_LOCAL_DRIVE == repo_file_path.drive:
            return convert_to_unix_path(f"/{os.path.relpath(repo_file_path)}").replace("/..", "")

        return f"/{'/'.join(repo_file_path.parts[1:])}"

    def set_guideline(self, guideline: Optional[str]) -> None:
        self.guideline = guideline

    @staticmethod
    def _trim_special_chars(expression: str) -> str:
        return "".join(re.findall(re.compile(r"[^ ${\}]+"), expression))

    @staticmethod
    def _is_expression_in_code_lines(expression: str, code_block: List[Tuple[int, str]]) -> bool:
        stripped_expression = Record._trim_special_chars(expression)
        return any(stripped_expression in Record._trim_special_chars(line) for (_, line) in code_block)

    @staticmethod
    def _code_line_string(code_block: List[Tuple[int, str]], colorized: bool = True) -> str:
        code_output = []
        color_codes = (Fore.WHITE if colorized else "", Fore.YELLOW if colorized else "")
        last_line_number_len = len(str(code_block[-1][0]))

        if len(code_block) >= OUTPUT_CODE_LINE_LIMIT:
            return f'\t\t{color_codes[1]}Code lines for this resource are too many. ' \
                   f'Please use IDE of your choice to review the file.'

        for line_num, line in code_block:
            spaces = " " * (last_line_number_len - len(str(line_num)))
            if line.lstrip().startswith("#"):
                code_output.append(f"\t\t{color_codes[0]}{line_num}{spaces} | {line}")
            else:
                code_output.append(f"\t\t{color_codes[0]}{line_num}{spaces} | {color_codes[1]}{line}")
        return "".join(code_output)

    @staticmethod
    def get_guideline_string(guideline: Optional[str]) -> str:
        if guideline:
            return (
                "\tGuide: "
                + Style.BRIGHT
                + colored(f"{guideline}\n", "blue", attrs=["underline"])
                + Style.RESET_ALL
            )
        return ''

    @staticmethod
    def get_code_lines_string(code_block: List[Tuple[int, str]]) -> str:
        if code_block:
            return "\n{}\n".format("".join([Record._code_line_string(code_block, not (ANSI_COLORS_DISABLED))]))
        return ''

    @staticmethod
    def get_details_string(details: List[str]) -> str:
        if details:
            detail_buffer = [colored(f"\tDetails: {details[0]}\n", "blue")]
            for t in details[1:]:
                detail_buffer.append(colored(f"\t         {t}\n", "blue"))
            return "".join(detail_buffer)
        return ''

    @staticmethod
    def get_caller_file_details_string(caller_file_path: Optional[str], caller_file_line_range: Optional[Tuple[int, int]]) -> str:
        if caller_file_path and caller_file_line_range:
            return colored(
                "\tCalling File: {}:{}\n".format(
                    caller_file_path, "-".join([str(x) for x in caller_file_line_range])
                ),
                "magenta",
            )
        return ''

    @staticmethod
    def get_evaluation_string(evaluations: Optional[Dict[str, Any]], code_block: List[Tuple[int, str]]) -> str:
        if evaluations:
            for (var_name, var_evaluations) in evaluations.items():
                var_file = var_evaluations["var_file"]
                var_definitions = var_evaluations["definitions"]
                for definition_obj in var_definitions:
                    definition_expression = definition_obj["definition_expression"]
                    if Record._is_expression_in_code_lines(definition_expression, code_block):
                        return colored(
                            f'\tVariable {colored(var_name, "yellow")} (of {var_file}) evaluated to value "{colored(var_evaluations["value"], "yellow")}" '
                            f'in expression: {colored(definition_obj["definition_name"] + " = ", "yellow")}{colored(definition_obj["definition_expression"], "yellow")}\n',
                            "white",
                        )
        return ''

    def to_string(self, compact: bool = False, use_bc_ids: bool = False) -> str:
        status = ""
        status_color = "white"
        suppress_comment = ""
        if self.check_result["result"] == CheckResult.PASSED:
            status = CheckResult.PASSED.name
            status_color = "green"
        elif self.check_result["result"] == CheckResult.FAILED:
            status = CheckResult.FAILED.name
            status_color = "red"
        elif self.check_result["result"] == CheckResult.SKIPPED:
            status = CheckResult.SKIPPED.name
            status_color = "blue"
            suppress_comment = "\tSuppress comment: {}\n".format(self.check_result.get("suppress_comment", ""))

        check_message = colored('Check: {}: "{}"\n'.format(self.get_output_id(use_bc_ids), self.check_name), "white")
        guideline_message = self.get_guideline_string(self.guideline)

        severity_message = f'\tSeverity: {self.severity.name}\n' if self.severity else ''

        file_details = colored(
            "\tFile: {}:{}\n".format(self.file_path, "-".join([str(x) for x in self.file_line_range])), "magenta"
        )
        code_lines = self.get_code_lines_string(self.code_block)
        detail = self.get_details_string(self.details)
        caller_file_details = self.get_caller_file_details_string(self.caller_file_path, self.caller_file_line_range)
        evaluation_message = self.get_evaluation_string(self.evaluations, self.code_block)

        status_message = colored("\t{} for resource: {}\n".format(status, self.resource), status_color)

        if self.check_result["result"] == CheckResult.FAILED and code_lines and not compact:
            return f"{check_message}{status_message}{severity_message}{detail}{file_details}{caller_file_details}{guideline_message}{code_lines}{evaluation_message}"

        if self.check_result["result"] == CheckResult.SKIPPED:
            return f"{check_message}{status_message}{severity_message}{suppress_comment}{detail}{file_details}{caller_file_details}{guideline_message}"
        else:
            return f"{check_message}{status_message}{severity_message}{detail}{file_details}{caller_file_details}{evaluation_message}{guideline_message}"

    def __str__(self) -> str:
        return self.to_string()

    def get_output_id(self, use_bc_ids: bool) -> str:
        return self.bc_check_id if self.bc_check_id and use_bc_ids else self.check_id

    def get_unique_string(self) -> str:
        return f"{self.check_id}.{self.check_result}.{self.file_abs_path}.{self.file_line_range}.{self.resource}"
