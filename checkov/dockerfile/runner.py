import logging
import os
from dockerfile_parse.constants import DOCKERFILE_FILENAME

from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_directories
from checkov.dockerfile.parser import parse, collect_skipped_checks
from checkov.dockerfile.registry import registry
from checkov.runner_filter import RunnerFilter

DOCKER_FILE_MASK = [DOCKERFILE_FILENAME]


class Runner(BaseRunner):
    check_type = "dockerfile"

    def run(self, root_folder=None, external_checks_dir=None, files=None, runner_filter=RunnerFilter(),
            collect_skip_comments=True):
        report = Report(self.check_type)
        definitions = {}
        definitions_raw = {}
        parsing_errors = {}
        files_list = []
        if external_checks_dir:
            for directory in external_checks_dir:
                registry.load_external_checks(directory)

        if files:
            for file in files:
                if os.path.basename(file) in DOCKER_FILE_MASK:
                    (definitions[file], definitions_raw[file]) = parse(file)

        if root_folder:
            for root, d_names, f_names in os.walk(root_folder):
                filter_ignored_directories(d_names)
                for file in f_names:
                    if file in DOCKER_FILE_MASK:
                        files_list.append(os.path.join(root, file))

            for file in files_list:
                relative_file_path = f'/{os.path.relpath(file, os.path.commonprefix((root_folder, file)))}'
                try:
                    (definitions[relative_file_path], definitions_raw[relative_file_path]) = parse(file)
                except TypeError:
                    logging.info(f'Dockerfile skipping {file} as it is not a valid dockerfile template')

        for docker_file_path in definitions.keys():

            # There are a few cases here. If -f was used, there could be a leading / because it's an absolute path,
            # or there will be no leading slash; root_folder will always be none.
            # If -d is used, root_folder will be the value given, and -f will start with a / (hardcoded above).
            # The goal here is simply to get a valid path to the file (which docker_file_path does not always give).
            if docker_file_path[0] == '/':
                path_to_convert = (root_folder + docker_file_path) if root_folder else docker_file_path
            else:
                path_to_convert = (os.path.join(root_folder, docker_file_path)) if root_folder else docker_file_path

            file_abs_path = os.path.abspath(path_to_convert)
            skipped_checks = collect_skipped_checks(definitions[docker_file_path])
            instructions = definitions[docker_file_path]

            results = registry.scan(docker_file_path, instructions, skipped_checks,
                                    runner_filter)
            for check, check_result in results.items():
                result_configuration = check_result['results_configuration']
                startline = 0
                endline = 0
                result_instruction = ""
                if result_configuration:
                    startline = result_configuration['startline']
                    endline = result_configuration['endline']
                    result_instruction = result_configuration["instruction"]

                codeblock = []
                self.calc_record_codeblock(codeblock, definitions_raw, docker_file_path, endline, startline)
                record = Record(check_id=check.id, check_name=check.name, check_result=check_result,
                                code_block=codeblock,
                                file_path=docker_file_path,
                                file_line_range=[startline,
                                                 endline],
                                resource="{}.{}".format(docker_file_path,
                                                        result_instruction,
                                                        startline),
                                evaluations=None, check_class=check.__class__.__module__,
                                file_abs_path=file_abs_path, entity_tags=None)
                report.add_record(record=record)

        return report


    def calc_record_codeblock(self, codeblock, definitions_raw, docker_file_path, endline, startline):
        for line in range(startline, endline + 1):
            codeblock.append((line, definitions_raw[docker_file_path][line]))
