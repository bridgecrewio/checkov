from checkov.cloudformation.parser.node import dict_node
from checkov.serverless.parsers.parser import FUNCTIONS_TOKEN, PROVIDER_TOKEN, IAM_ROLE_STATEMENTS_TOKEN
from checkov.cloudformation.context_parser import ContextParser as CfnContextParser


class ContextParser(object):
    """
    serverless functions template context parser
    """

    def __init__(self, sls_file, sls_template, sls_template_lines):
        self.sls_file = sls_file
        self.sls_template = sls_template
        self.sls_template_lines = sls_template_lines
        self.provider_conf = sls_template[PROVIDER_TOKEN]
        self.functions_conf = sls_template[FUNCTIONS_TOKEN]

    def extract_function_code_lines(self, sls_function):
        find_lines_result_list = list(CfnContextParser.find_lines(sls_function, '__startline__'))
        if len(find_lines_result_list) >= 1:
            start_line = min(find_lines_result_list) - 1
            end_line = max(list(CfnContextParser.find_lines(sls_function, '__endline__')))

            entity_lines_range = [start_line, end_line - 1]

            entity_code_lines = self.sls_template_lines[start_line - 1: end_line - 1]
            return entity_lines_range, entity_code_lines
        return None, None

    def enrich_function_iam_roles(self, sls_function_name):
        if self.provider_conf.get(IAM_ROLE_STATEMENTS_TOKEN):
            global_iam_role = self.provider_conf.get(IAM_ROLE_STATEMENTS_TOKEN)
            template_function = self.functions_conf[sls_function_name]
            if template_function.get(IAM_ROLE_STATEMENTS_TOKEN):
                template_function[IAM_ROLE_STATEMENTS_TOKEN].extend(global_iam_role)
            else:
                template_function[IAM_ROLE_STATEMENTS_TOKEN] = global_iam_role
