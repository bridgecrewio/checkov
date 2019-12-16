from termcolor import colored
from checkov.terraform.models.enums import CheckResult
from colorama import init, Fore

init(autoreset=True)


class Record():
    check_id = ""
    check_name = ""
    check_result = None
    check_class = ""
    code_block = ""
    file_path = ""
    file_line_range = []
    resource = ""

    def __init__(self, check_id, check_name, check_result, code_block, file_path, file_line_range, resource,
                 check_class):
        self.check_id = check_id
        self.check_name = check_name
        self.check_result = check_result
        self.code_block = code_block
        self.file_path = file_path
        self.file_line_range = file_line_range
        self.resource = resource
        self.check_class = check_class

    @staticmethod
    def _code_line_string(line_num, line):
        if '#' in line:
            return "\t\t" + Fore.WHITE + str(line_num) + ' | ' + line
        else:
            return "\t\t" + Fore.WHITE + str(line_num) + ' | ' + Fore.YELLOW + line

    def __str__(self):
        status = ''
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

        check_message = colored("Check: \"{}\"\n".format(self.check_name), "white")
        file_details = colored(
            "\tFile: {}:{}\n\n".format(self.file_path, "-".join([str(x) for x in self.file_line_range])),
            "magenta")
        code_lines = "{}\n".format("".join(
            [self._code_line_string(line_num, line) for (line_num, line) in self.code_block]))
        status_message = colored("\t{} for resource: {}\n".format(status, self.resource), status_color)
        if self.check_result['result'] == CheckResult.FAILED:
            return check_message + status_message + file_details + code_lines

        if self.check_result['result'] == CheckResult.SKIPPED:
            return check_message + status_message + suppress_comment + file_details
        else:
            return check_message + status_message + file_details
