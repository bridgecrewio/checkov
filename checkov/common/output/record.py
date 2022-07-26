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
        connected_node: Optional[Dict[str, Any]] = None
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
        self.short_description = short_description  # used by SARIF output
        self.vulnerability_details = vulnerability_details  # Stores package vulnerability details
        self.connected_node = connected_node
        self.guideline: str | None = None

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

    def _is_expression_in_code_lines(self, expression: str) -> bool:
        stripped_expression = self._trim_special_chars(expression)
        return any(stripped_expression in self._trim_special_chars(line) for (_, line) in self.code_block)

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

    def to_string(self, compact: bool = False, use_bc_ids: bool = False) -> str:
        status = ""
        evaluation_message = ""
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
            suppress_comment = "\tSuppress comment: {}\n".format(self.check_result["suppress_comment"])

        check_message = colored('Check: {}: "{}"\n'.format(self.get_output_id(use_bc_ids), self.check_name), "white")
        guideline_message = ""
        if self.guideline:
            guideline_message = (
                "\tGuide: "
                + Style.BRIGHT
                + colored(f"{self.guideline}\n", "blue", attrs=["underline"])
                + Style.RESET_ALL
            )

        severity_message = f'\tSeverity: {self.severity.name}\n' if self.severity else ''

        file_details = colored(
            "\tFile: {}:{}\n".format(self.file_path, "-".join([str(x) for x in self.file_line_range])), "magenta"
        )
        code_lines = ""
        if self.code_block:
            code_lines = "\n{}\n".format("".join([self._code_line_string(self.code_block, not(ANSI_COLORS_DISABLED))]))
        caller_file_details = ""
        if self.caller_file_path and self.caller_file_line_range:
            caller_file_details = colored(
                "\tCalling File: {}:{}\n".format(
                    self.caller_file_path, "-".join([str(x) for x in self.caller_file_line_range])
                ),
                "magenta",
            )
        if self.evaluations:
            for (var_name, var_evaluations) in self.evaluations.items():
                var_file = var_evaluations["var_file"]
                var_definitions = var_evaluations["definitions"]
                for definition_obj in var_definitions:
                    definition_expression = definition_obj["definition_expression"]
                    if self._is_expression_in_code_lines(definition_expression):
                        evaluation_message = evaluation_message + colored(
                            f'\tVariable {colored(var_name, "yellow")} (of {var_file}) evaluated to value "{colored(var_evaluations["value"], "yellow")}" '
                            f'in expression: {colored(definition_obj["definition_name"] + " = ", "yellow")}{colored(definition_obj["definition_expression"], "yellow")}\n',
                            "white",
                        )

        status_message = colored("\t{} for resource: {}\n".format(status, self.resource), status_color)
        if self.check_result["result"] == CheckResult.FAILED and code_lines and not compact:
            return f"{check_message}{status_message}{severity_message}{file_details}{caller_file_details}{guideline_message}{code_lines}{evaluation_message}"

        if self.check_result["result"] == CheckResult.SKIPPED:
            return f"{check_message}{status_message}{severity_message}{suppress_comment}{file_details}{caller_file_details}{guideline_message}"
        else:
            return f"{check_message}{status_message}{severity_message}{file_details}{caller_file_details}{evaluation_message}{guideline_message}"

    def __str__(self) -> str:
        return self.to_string()

    def get_output_id(self, use_bc_ids: bool) -> str:
        return self.bc_check_id if self.bc_check_id and use_bc_ids else self.check_id

    def get_unique_string(self) -> str:
        return f"{self.check_id}.{self.check_result}.{self.file_abs_path}.{self.file_line_range}.{self.resource}"
