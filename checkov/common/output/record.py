import os
import re
from pathlib import Path
from typing import Union

from colorama import init, Fore, Style
from termcolor import colored

from checkov.common.models.enums import CheckResult
from checkov.common.util.file_utils import convert_to_unix_path

init(autoreset=True)


class Record:
    check_id = ""
    check_name = ""
    check_result = None
    check_class = ""
    code_block = ""
    file_path = ""
    file_line_range = []
    caller_file_path = None           # When created from a module
    caller_file_line_range = None     #
    resource = ""
    guideline = None
    fixed_definition = None
    entity_tags = None

    def __init__(self, check_id, check_name, check_result, code_block, file_path, file_line_range, resource,
                 evaluations, check_class, file_abs_path, entity_tags=None,
                 caller_file_path=None, caller_file_line_range=None, bc_check_id=None, resource_address=None):
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
        self.caller_file_path = caller_file_path
        self.caller_file_line_range = caller_file_line_range
        self.resource_address = resource_address

    @staticmethod
    def _determine_repo_file_path(file_path: Union[str, "os.PathLike[str]"]) -> str:
        # matches file paths given in the BC platform and should always be a unix path
        repo_file_path = Path(file_path)
        if Path.cwd().drive == repo_file_path.drive:
            return convert_to_unix_path(f"/{os.path.relpath(repo_file_path)}").replace("/..", "")

        return f"/{'/'.join(repo_file_path.parts[1:])}"

    def set_guideline(self, guideline):
        self.guideline = guideline

    @staticmethod
    def _trim_special_chars(expression):
        return "".join(re.findall(re.compile(r'[^ ${\}]+'), expression))

    def _is_expression_in_code_lines(self, expression):
        stripped_expression = self._trim_special_chars(expression)
        return any(stripped_expression in self._trim_special_chars(line) for (_, line) in self.code_block)

    @staticmethod
    def _code_line_string(code_block):
        string_block = ''
        last_line_number, _ = code_block[-1]

        for (line_num, line) in code_block:
            spaces = ' ' * (len(str(last_line_number)) - len(str(line_num)))
            if line.lstrip().startswith('#'):
                string_block += "\t\t" + Fore.WHITE + str(line_num) + spaces + ' | ' + line
            else:
                string_block += "\t\t" + Fore.WHITE + str(line_num) + spaces + ' | ' + Fore.YELLOW + line
        return string_block

    def to_string(self, compact=False, use_bc_ids=False):
        status = ''
        evaluation_message = ''
        status_color = "white"
        if self.check_result['result'] == CheckResult.PASSED:
            status = CheckResult.PASSED.name
            status_color = "green"
        elif self.check_result['result'] == CheckResult.FAILED:
            status = CheckResult.FAILED.name
            status_color = "red"
        elif self.check_result['result'] == CheckResult.SKIPPED:
            status = CheckResult.SKIPPED.name
            status_color = 'blue'
            suppress_comment = "\tSuppress comment: {}\n".format(self.check_result['suppress_comment'])

        check_message = colored("Check: {}: \"{}\"\n".format(self.get_output_id(use_bc_ids), self.check_name), "white")
        guideline_message = ''
        if self.guideline:
            guideline_message = "\tGuide: " + Style.BRIGHT + colored(f"{self.guideline}\n", 'blue', attrs=['underline']) + Style.RESET_ALL
        file_details = colored(
            "\tFile: {}:{}\n".format(self.file_path, "-".join([str(x) for x in self.file_line_range])),
            "magenta")
        code_lines = ""
        if self.code_block:
            code_lines = "\n{}\n".format("".join(
                [self._code_line_string(self.code_block)]))
        caller_file_details = ""
        if self.caller_file_path and self.caller_file_line_range:
            caller_file_details = colored(
                "\tCalling File: {}:{}\n".format(self.caller_file_path,
                                                 "-".join([str(x) for x in self.caller_file_line_range])),
                "magenta")
        if self.evaluations:
            for (var_name, var_evaluations) in self.evaluations.items():
                var_file = var_evaluations['var_file']
                var_definitions = var_evaluations['definitions']
                for definition_obj in var_definitions:
                    definition_expression = definition_obj["definition_expression"]
                    if self._is_expression_in_code_lines(definition_expression):
                        evaluation_message = evaluation_message + colored(
                            f'\tVariable {colored(var_name, "yellow")} (of {var_file}) evaluated to value "{colored(var_evaluations["value"], "yellow")}" '
                            f'in expression: {colored(definition_obj["definition_name"] + " = ", "yellow")}{colored(definition_obj["definition_expression"], "yellow")}\n',
                            'white')
        status_message = colored("\t{} for resource: {}\n".format(status, self.resource), status_color)
        if self.check_result['result'] == CheckResult.FAILED and code_lines and not compact:
            return check_message + status_message + file_details + caller_file_details + guideline_message + code_lines + evaluation_message

        if self.check_result['result'] == CheckResult.SKIPPED:
            return check_message + status_message + suppress_comment + file_details + caller_file_details + guideline_message
        else:
            return check_message + status_message + file_details + caller_file_details + evaluation_message + guideline_message

    def __str__(self):
        return self.to_string()

    def get_output_id(self, use_bc_ids: bool) -> str:
        return self.bc_check_id if self.bc_check_id and use_bc_ids else self.check_id

    def get_unique_string(self):
        return f"{self.check_id}.{self.check_result}.{self.file_abs_path}.{self.file_line_range}.{self.resource}"
