from checkov.cloudformation.parser.node import dict_node, list_node, str_node
from checkov.serverless.parsers.parser import FUNCTIONS_TOKEN, PROVIDER_TOKEN, IAM_ROLE_STATEMENTS_TOKEN, \
    ENVIRONMENT_TOKEN
from checkov.cloudformation.context_parser import ContextParser as CfnContextParser


class ContextParser(object):
    """
    serverless functions template context parser
    """
    # control on inherited provider attributes to scanned functions
    ENRICHED_ATTRIBUTES = [IAM_ROLE_STATEMENTS_TOKEN, ENVIRONMENT_TOKEN]

    def __init__(self, sls_file, sls_template, sls_template_lines):
        self.sls_file = sls_file
        self.sls_template = sls_template
        self.sls_template_lines = sls_template_lines
        self.provider_conf = sls_template[PROVIDER_TOKEN]
        self.functions_conf = sls_template[FUNCTIONS_TOKEN]
        self.provider_type = self._infer_provider_type()

    def extract_function_code_lines(self, sls_function):
        find_lines_result_list = list(CfnContextParser.find_lines(sls_function, '__startline__'))
        if len(find_lines_result_list) >= 1:
            start_line = min(find_lines_result_list) - 1
            end_line = max(list(CfnContextParser.find_lines(sls_function, '__endline__')))

            entity_lines_range = [start_line, end_line - 1]

            entity_code_lines = self.sls_template_lines[start_line - 1: end_line - 1]
            return entity_lines_range, entity_code_lines
        return None, None

    def enrich_function_with_provider(self, sls_function_name):
        """
        Update inplace a function's template with pre-defined inherited provider attributes
        :param sls_function_name: scanned function
        :return: None
        """
        if isinstance(self.provider_conf, dict_node):
            for enriched_attribute in self.ENRICHED_ATTRIBUTES:
                if self.provider_conf.get(enriched_attribute):
                    provider_attribute = self.provider_conf.get(enriched_attribute)
                    template_function = self.functions_conf[sls_function_name]
                    if template_function.get(enriched_attribute):
                        if isinstance(template_function[enriched_attribute], list_node):
                            template_function[enriched_attribute].extend(provider_attribute)
                        if isinstance(template_function[enriched_attribute], dict_node):
                            template_function[enriched_attribute].update(provider_attribute)
                    else:
                        template_function[enriched_attribute] = provider_attribute

    def _infer_provider_type(self):
        if isinstance(self.provider_conf, dict_node):
            return self.provider_conf.get('name')
        if isinstance(self.provider_conf, str_node):
            return self.provider_conf
