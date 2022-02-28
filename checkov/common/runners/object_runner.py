import logging
import os
from abc import abstractmethod

from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.runner_filter import RunnerFilter


class Runner(BaseRunner):

    def _load_files(self, files_to_load, definitions, definitions_raw, filename_fn=None):
        files_to_load = [filename_fn(file) if filename_fn else file for file in files_to_load]
        results = parallel_runner.run_function(lambda f: (f, self._parse_file(f)), files_to_load)
        for file, result in results:
            if result:
                (definitions[file], definitions_raw[file]) = result

    @abstractmethod
    def _parse_file(self, f):
        raise Exception("parser should be imported by deriving class")

    def run(self, root_folder=None, external_checks_dir=None, files=None,
            runner_filter=RunnerFilter(), collect_skip_comments=True) -> Report:
        registry = self.import_registry()

        definitions = {}
        definitions_raw = {}

        report = Report(self.check_type)

        if not files and not root_folder:
            logging.debug("No resources to scan.")
            return report

        if not external_checks_dir and self.require_external_checks():
            logging.debug("The runner requires that external checks are defined.")
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

        for file_path in definitions.keys():
            results = registry.scan(
                file_path, definitions[file_path], [], runner_filter
            )
            for key, result in results.items():
                result_config = result["results_configuration"]
                start = 0
                end = 0
                check = result["check"]
                end, start = self.get_start_end_lines(end, result_config, start)
                record = Record(
                    check_id=check.id,
                    bc_check_id=check.bc_id,
                    check_name=check.name,
                    check_result=result,
                    code_block=definitions_raw[file_path][start:end + 1],
                    file_path=file_path,
                    file_line_range=[start + 1, end + 1],
                    resource=f"{file_path}.{key}",
                    evaluations=None,
                    check_class=check.__class__.__module__,
                    file_abs_path=os.path.abspath(file_path),
                    entity_tags=None,
                    severity=check.bc_severity
                )
                report.add_record(record)

        return report

    @abstractmethod
    def get_start_end_lines(self, end, result_config, start):
        raise Exception("should be handled by derived class")

    @abstractmethod
    def import_registry(self):
        raise Exception("registry should be imported by deriving class")

    def require_external_checks(self):
        return True

    @staticmethod
    def _change_files_path_to_relative(report: Report):
        for record in report.get_all_records():
            record.file_path = record.file_path.replace(os.getcwd(), '')
            record.resource = record.resource.replace(os.getcwd(), '')
