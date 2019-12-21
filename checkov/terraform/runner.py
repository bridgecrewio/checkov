import logging

from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.output.record import Record
from checkov.terraform.output.report import Report
from checkov.terraform.parser import Parser


class Runner:

    def run(self, root_folder, external_checks_dir=None):
        report = Report()
        tf_definitions = {}
        parsing_errors = {}

        if external_checks_dir:
            for directory in external_checks_dir:
                resource_registry.load_external_checks(directory)

        Parser().hcl2(directory=root_folder, tf_definitions=tf_definitions, parsing_errors=parsing_errors)
        report.add_parsing_errors(parsing_errors.keys())
        for definition in tf_definitions.items():
            full_file_path = definition[0]
            definition_context = parser_registry.enrich_definitions_context(definition)
            scanned_file = definition[0].split(root_folder)[1]
            logging.debug("Scanning file: %s", scanned_file)
            if 'resource' in definition[1]:
                for resource in definition[1]['resource']:
                    resource_type = list(resource.keys())[0]
                    resource_name = list(list(resource.values())[0].keys())[0]
                    resource_id = "{}.{}".format(resource_type, resource_name)

                    resource_context = definition_context[full_file_path][resource_type][resource_name]
                    resource_lines_range = [resource_context['start_line'], resource_context['end_line']]
                    resource_code_lines = resource_context['code_lines']
                    skipped_checks = resource_context.get('skipped_checks')
                    results = resource_registry.scan(resource, scanned_file, skipped_checks)
                    for check, check_result in results.items():
                        record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                        code_block=resource_code_lines, file_path=scanned_file,
                                        file_line_range=resource_lines_range,
                                        resource=resource_id, check_class=check.__class__.__module__)
                        report.add_record(record=record)
        return report
