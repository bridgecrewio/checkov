import os
from typing import List, Dict, Any

from colorama import Style
from termcolor import colored

from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record, ANSI_COLORS_DISABLED


class Policy3dRecord(Record):
    def __init__(self,
                 check_id,
                 bc_check_id,
                 check_name,
                 check_result,
                 code_block,
                 file_path,
                 file_line_range,
                 resource,
                 evaluations,
                 check_class,
                 file_abs_path,
                 entity_tags,
                 severity,
                 vulnerabilities: List[Dict[str, Any]],
                 iac_bc_check_ids: List[str]
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
            entity_tags=entity_tags,
            severity=severity,
        )
        self.vulnerabilities = vulnerabilities
        self.iac_bc_check_ids = iac_bc_check_ids

    def render_iac_output(self, compact: bool = False, use_bc_ids: bool = False) -> str:
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
            suppress_comment = "\tSuppress comment: {}\n".format(self.check_result.get("suppress_comment", ""))

        check_message = colored('Check: {}: "{}"\n'.format(self.get_output_id(use_bc_ids), self.check_name),
                                "white")
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

        iac_violation_header = ''
        last_bc_check_id_index = len(self.iac_bc_check_ids) - 1
        for i, bc_check_id in enumerate(self.iac_bc_check_ids):
            if i == 0:
                iac_violation_header += colored(f'\tIaC Resource that Violates {bc_check_id}', attrs=['bold'])
            elif i == last_bc_check_id_index:
                iac_violation_header += colored(f' and {bc_check_id}', attrs=['bold'])
            else:
                iac_violation_header += colored(f', {bc_check_id}', attrs=['bold'])
        if iac_violation_header:
            iac_violation_header += colored(':', attrs=['bold'])

        code_lines = ""
        if self.code_block:
            code_lines = "\n{}\n".format(
                "".join([self._code_line_string(self.code_block, not (ANSI_COLORS_DISABLED))]))

        detail = ""
        if self.details:
            detail_buffer = [colored(f"\tDetails: {self.details[0]}\n", "blue")]

            for t in self.details[1:]:
                detail_buffer.append(colored(f"\t         {t}\n", "blue"))

            detail = "".join(detail_buffer)

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

        # Improve this part by leveraging inheritance of SecretsRecord
        secret_validation_status_string = ""  # nosec
        if self.check_result["result"] == CheckResult.FAILED and \
                hasattr(self, 'validation_status') and \
                os.getenv("CKV_VALIDATE_SECRETS") and \
                hasattr(self,
                        '_get_secret_validation_status_message'):  # for typing purposes, can't check with isinstance cause of circular dependency
            secret_validation_status_string = self._get_secret_validation_status_message()

        if self.check_result["result"] == CheckResult.FAILED and code_lines and not compact:
            return f"{check_message}{status_message}{secret_validation_status_string}{severity_message}{detail}{file_details}{caller_file_details}{guideline_message}{iac_violation_header}{code_lines}{evaluation_message}"

        if self.check_result["result"] == CheckResult.SKIPPED:
            return f"{check_message}{status_message}{severity_message}{suppress_comment}{detail}{file_details}{caller_file_details}{guideline_message}"
        else:
            return f"{check_message}{status_message}{severity_message}{detail}{file_details}{caller_file_details}{evaluation_message}{guideline_message}"
