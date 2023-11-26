from __future__ import annotations

from typing import Any

from checkov.serverless.parsers.parser import FUNCTIONS_TOKEN, PROVIDER_TOKEN, IAM_ROLE_STATEMENTS_TOKEN, \
    ENVIRONMENT_TOKEN, STACK_TAGS_TOKEN, TAGS_TOKEN
from checkov.cloudformation.context_parser import ContextParser as CfnContextParser, STARTLINE, ENDLINE


class ContextParser(object):
    """
    serverless functions template context parser
    """
    # control on inherited provider attributes to scanned functions
    # Values are the source and destination
    ENRICHED_ATTRIBUTES = [
        (IAM_ROLE_STATEMENTS_TOKEN, IAM_ROLE_STATEMENTS_TOKEN),
        (ENVIRONMENT_TOKEN, ENVIRONMENT_TOKEN),
        (STACK_TAGS_TOKEN, TAGS_TOKEN),
        ("runtime", "runtime"),
        ("timeout", "timeout"),
        ("memorySize", "memorySize")
    ]

    def __init__(self, sls_file: str, sls_template: dict[str, Any], sls_template_lines: list[tuple[int, str]]) -> None:
        self.sls_file = sls_file
        self.sls_template = sls_template
        self.sls_template_lines = sls_template_lines
        self.provider_conf = sls_template.get(PROVIDER_TOKEN)
        self.functions_conf = sls_template.get(FUNCTIONS_TOKEN) or {}
        self.provider_type = self._infer_provider_type()

    def extract_code_lines(
        self, content: dict[str, Any]
    ) -> tuple[list[int], list[tuple[int, str]]] | tuple[None, None]:
        find_lines_result_list = list(CfnContextParser.find_lines(content, STARTLINE))
        if len(find_lines_result_list) >= 1:
            start_line = min(find_lines_result_list) - 1
            end_line = max(list(CfnContextParser.find_lines(content, ENDLINE)))

            entity_lines_range = [start_line, end_line - 1]

            entity_code_lines = self.sls_template_lines[start_line - 1: end_line - 1]
            return entity_lines_range, entity_code_lines
        return None, None

    def enrich_function_with_provider(self, sls_function_name: str) -> None:
        """
        Update inplace a function's template with pre-defined inherited provider attributes
        :param sls_function_name: scanned function
        :return: None
        """
        if not self.provider_conf or not isinstance(self.provider_conf, dict):
            return

        for src_attribute, dst_enriched_attribute in self.ENRICHED_ATTRIBUTES:
            provider_attribute = self.provider_conf.get(src_attribute)
            if not provider_attribute:
                continue

            template_function = self.functions_conf.get(sls_function_name)
            if not template_function:
                continue
            function_attribute = template_function.get(dst_enriched_attribute)
            if function_attribute:
                if not isinstance(function_attribute, type(provider_attribute)):
                    # Do not enrich maps with strings etc
                    continue
                if isinstance(template_function[dst_enriched_attribute], list):
                    template_function[dst_enriched_attribute].extend(provider_attribute)
                if isinstance(template_function[dst_enriched_attribute], dict):
                    template_function[dst_enriched_attribute].update(provider_attribute)
            else:
                template_function[dst_enriched_attribute] = provider_attribute

    def _infer_provider_type(self) -> str | None:
        if isinstance(self.provider_conf, dict):
            return self.provider_conf.get('name')
        if isinstance(self.provider_conf, str):
            return self.provider_conf

        return None
