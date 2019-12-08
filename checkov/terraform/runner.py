import logging

from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.output.record import Record
from checkov.terraform.output.report import Report
from checkov.terraform.parser import Parser


class Runner:

    def run(self, root_folder):
        report = Report()
        tf_definitions = {}
        parsing_errors = {}

        Parser().hcl2(directory=root_folder, tf_definitions=tf_definitions, parsing_errors=parsing_errors)
        report.add_parsing_errors(parsing_errors.keys())
        for definition in tf_definitions.items():
            scanned_file = definition[0].split(root_folder)[1]
            logging.debug("Scanning file: %s", scanned_file)
            if 'resource' in definition[1]:
                for resource in definition[1]['resource']:
                    results = resource_registry.scan(resource, scanned_file)
                    for check, check_result in results.items():
                        resource_name = "{}.{}".format(list(resource.keys())[0],
                                                       list(list(resource.values())[0].keys())[0])
                        # TODO get data from context here
                        record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                        code_block="", file_path=scanned_file, file_line_range="",
                                        resource=resource_name)
                        report.add_record(record=record)
        return report
