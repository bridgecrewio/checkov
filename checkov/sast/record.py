from typing import List, Dict, Any, Tuple, Optional, Union

from termcolor import colored

from checkov.common.bridgecrew.severities import Severity
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.typing import _CheckResult


class SastRecord(Record):
    def __init__(self,
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
                 severity: Optional[Severity],
                 bc_check_id: Optional[str] = None,
                 cwe: Optional[Union[List[str], str]] = None,
                 owasp: Optional[Union[List[str], str]] = None,
                 show_severity: Optional[bool] = False  # should be false in case the severities are just a default value
                 ) -> None:
        super().__init__(
            check_id=check_id,
            bc_check_id=bc_check_id,
            check_name=check_name,
            check_result=check_result,
            code_block=code_block,
            file_path=file_path,
            file_line_range=file_line_range,
            resource=resource,
            evaluations=evaluations,
            check_class=check_class,
            file_abs_path=file_abs_path,
            severity=severity,
        )
        self.cwe = cwe
        self.owasp = owasp
        self.show_severity = show_severity

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

        check_message = colored('Check: {}: "{}"\n'.format(self.get_output_id(use_bc_ids), self.check_name),
                                "white")
        guideline_message = self.get_guideline_string(self.guideline)

        severity_message = f'\tSeverity: {self.severity.name}\n' if self.severity and self.show_severity else ''

        file_details = f'{self.file_path}:{" -> ".join([str(x) for x in self.file_line_range])}'
        code_lines = self.get_code_lines_string(self.code_block)
        detail = self.get_details_string(self.details)
        caller_file_details = self.get_caller_file_details_string(self.caller_file_path,
                                                                  self.caller_file_line_range)
        evaluation_message = self.get_evaluation_string(self.evaluations, self.code_block)

        status_message = colored("\t{} for file - {}\n".format(status, file_details), status_color)  # type: ignore

        cwe_message = colored(f'\t{self.cwe}\n') if self.cwe else ''

        if self.check_result["result"] == CheckResult.FAILED and code_lines and not compact:
            return f"{check_message}{severity_message}{status_message}{cwe_message}{detail}{caller_file_details}{guideline_message}{code_lines}{evaluation_message}\n"

        if self.check_result["result"] == CheckResult.SKIPPED:
            return f"{check_message}{severity_message}{status_message}{cwe_message}{suppress_comment}{detail}{caller_file_details}{guideline_message}\n"
        else:
            return f"{check_message}{severity_message}{status_message}{cwe_message}{detail}{caller_file_details}{evaluation_message}{guideline_message}\n"
