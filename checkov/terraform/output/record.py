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
    def code_line_string(line_num, line):
        return "\t\t" + Fore.BLUE + str(line_num) + Fore.WHITE + ' | ' + Fore.YELLOW + line

    def __str__(self):
        if self.check_result == CheckResult.SUCCESS:
            status = "Passed"
            status_color = "green"
        else:
            status = "Failed"
            status_color = "red"
        check_message = colored("Check: \"{}\"\n".format(self.check_name), "white")
        file_details = colored("{}:{}\n\n".format(self.file_path, "-".join([str(x) for x in self.file_line_range])),
                               "magenta")
        code_lines = "{}\n".format("".join([self.code_line_string(*code_line) for code_line in self.code_block]))
        status_message = colored("\t{} for resource: {}\n".format(status, self.resource), status_color)
        return check_message + file_details + code_lines + status_message
