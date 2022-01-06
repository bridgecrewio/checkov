import logging
import os

from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.parsers.json import parse
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.runner_filter import RunnerFilter


class Runner(BaseRunner):
    check_type = "json"

    @staticmethod
    def _load_files(files_to_load, definitions, definitions_raw, filename_fn=None):
        files_to_load = [filename_fn(file) if filename_fn else file for file in files_to_load]
        results = parallel_runner.run_function(lambda f: (f, parse(f)), files_to_load)
        for file, result in results:
            (definitions[file], definitions_raw[file]) = result

    def run(self, root_folder=None, external_checks_dir=None, files=None,
            runner_filter=RunnerFilter(), collect_skip_comments=True):
        registry = self.import_registry()

        definitions = {}
        definitions_raw = {}

        report = Report(self.check_type)

        if not files and not root_folder:
            logging.debug("No resources to scan.")
            return report

        if not external_checks_dir and self.require_external_checks():
            logging.debug("The json runner requires that external checks are defined.")
            return report
        if external_checks_dir:
            for directory in external_checks_dir:
                registry.load_external_checks(directory)

        if files:
            self._load_files(files, definitions, definitions_raw)

        if root_folder:
            for root, d_names, f_names in os.walk(root_folder):
                filter_ignored_paths(root, d_names, runner_filter.excluded_paths)
                filter_ignored_paths(root, f_names, runner_filter.excluded_paths)
                self._load_files(
                    f_names,
                    definitions,
                    definitions_raw,
                    lambda f: os.path.join(root, f)
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

    def import_registry(self):
        from checkov.json_doc.registry import registry
        return registry

    def require_external_checks(self):
        return True
