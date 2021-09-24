import json
import logging
import os

from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.common.parsers.json import parse
from checkov.json.registry import registry
from checkov.runner_filter import RunnerFilter


class Runner(BaseRunner):
    check_type = "json"

    def run(self, root_folder=None, external_checks_dir=None, files=None, runner_filter=RunnerFilter(),
            collect_skip_comments=True):
        report = Report(self.check_type)
        definitions = {}
        definitions_raw = {}
        parsing_errors = {}

        def load_files(files_to_load, filename_fn=None, key_fn=None):
            for file in files_to_load:
                f = filename_fn(file) if filename_fn else file
                key = key_fn(f) if key_fn else f
                (definitions[key], definitions_raw[key]) = parse(f)

        if not external_checks_dir:
            logging.warning("The json runner requires that external checks are defined.")
            return report

        for directory in external_checks_dir:
            registry.load_external_checks(directory)

        if files:
            load_files(files)

        if root_folder:
            for root, d_names, f_names in os.walk(root_folder):
                filter_ignored_paths(root, d_names, runner_filter.excluded_paths)
                filter_ignored_paths(root, f_names, runner_filter.excluded_paths)
                load_files(
                    f_names,
                    lambda f: os.path.join(root, f),
                    # lambda k: f"{os.sep}{os.path.relpath(k, os.path.commonprefix((root_folder, k)))}"
                )

        for json_file_path in definitions.keys():
            results = registry.scan(
                json_file_path, definitions[json_file_path], [], runner_filter
            )
            for check, result in results.items():
                result_config = result["results_configuration"]
                start = result_config.start_mark.line
                end = result_config.end_mark.line
                record = Record(
                    check_id=check.id,
                    bc_check_id=check.bc_id,
                    check_name=check.name,
                    check_result=result,
                    code_block=definitions_raw[json_file_path][start:end + 1],
                    file_path=json_file_path,
                    file_line_range=[start + 1, end + 1],
                    resource=f"{json_file_path}",
                    evaluations=None,
                    check_class=check.__class__.__module__,
                    file_abs_path=os.path.abspath(json_file_path),
                    entity_tags=None
                )
                report.add_record(record)

        return report
