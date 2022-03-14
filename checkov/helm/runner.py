from __future__ import annotations

import io
import logging
import operator
import os
import shutil
import subprocess  # nosec
import tempfile
from functools import reduce
from typing import Any

import yaml

from checkov.common.output.report import Report, CheckType
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.helm.registry import registry
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.runner_filter import RunnerFilter

K8_POSSIBLE_ENDINGS = [".yaml", ".yml", ".json"]


class Runner(BaseRunner):
    check_type = CheckType.HELM
    helm_command = 'helm'
    system_deps = True

    @staticmethod
    def find_chart_directories(root_folder, files, excluded_paths):
        chart_directories = []
        if not excluded_paths:
            excluded_paths = []
        if files:
            logging.info('Running with --file argument; checking for Helm Chart.yaml files')
            for file in files:
                if os.path.basename(file) == 'Chart.yaml':
                    chart_directories.append(os.path.dirname(file))

        if root_folder:
            for root, d_names, f_names in os.walk(root_folder):
                filter_ignored_paths(root, d_names, excluded_paths)
                filter_ignored_paths(root, f_names, excluded_paths)
                if 'Chart.yaml' in f_names:
                    chart_directories.append(root)

        return chart_directories

    @staticmethod
    def parse_helm_dependency_output(o):
        output = o.decode('utf-8')
        chart_dependencies = {}
        if "WARNING" in output:
            # Helm  output showing no deps, example: 'WARNING: no dependencies at helm-charts/charts/prometheus-kafka-exporter/charts\n'
            pass
        else:
            lines = output.split('\n')
            for line in lines:
                if line != "":
                    if "NAME" not in line:
                        chart_name, chart_version, chart_repo, chart_status = line.split("\t")
                        chart_dependencies.update({chart_name.rstrip(): {'chart_name': chart_name.rstrip(),
                                                                         'chart_version': chart_version.rstrip(),
                                                                         'chart_repo': chart_repo.rstrip(),
                                                                         'chart_status': chart_status.rstrip()}})
        return chart_dependencies

    @staticmethod
    def parse_helm_chart_details(chart_path: str) -> dict[str, Any]:
        with open(f"{chart_path}/Chart.yaml", 'r') as chartyaml:
            try:
                chart_meta = yaml.safe_load(chartyaml)
            except yaml.YAMLError:
                logging.info(f"Failed to load chart metadata from {chart_path}/Chart.yaml.", exc_info=True)
        return chart_meta

    def check_system_deps(self):
        # Ensure local system dependancies are available and of the correct version.
        # Returns framework names to skip if deps fail.
        logging.info(f"Checking necessary system dependancies for {self.check_type} checks.")
        try:
            proc = subprocess.Popen([self.helm_command, 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
            o, e = proc.communicate()
            oString = str(o, 'utf-8')
            if "Version:" in oString:
                helmVersionOutput = oString[oString.find(':') + 2: oString.find(',') - 1]
                if "v3" in helmVersionOutput:
                    logging.info(f"Found working version of {self.check_type} dependancies: {helmVersionOutput}")
                    return None
            else:
                return self.check_type
        except Exception:
            logging.info(f"Error running necessary tools to process {self.check_type} checks.")
            return self.check_type

    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter(),
            collect_skip_comments=True):

        if external_checks_dir:
            for directory in external_checks_dir:
                registry.load_external_checks(directory)

        chart_directories = self.find_chart_directories(root_folder, files, runner_filter.excluded_paths)

        report = Report(self.check_type)

        chart_dir_and_meta = parallel_runner.run_function(
            lambda cd: (cd, self.parse_helm_chart_details(cd)), chart_directories)
        for chart_dir, chart_meta in chart_dir_and_meta:
            # chart_name = os.path.basename(chart_dir)
            logging.info(
                f"Processing chart found at: {chart_dir}, name: {chart_meta['name']}, version: {chart_meta['version']}")
            with tempfile.TemporaryDirectory() as target_dir:
                # dependency list is nicer to parse than dependency update.
                helmBinaryListChartDeps = subprocess.Popen([self.helm_command, 'dependency', 'list', chart_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
                o, e = helmBinaryListChartDeps.communicate()
                if e:
                    if "Warning: Dependencies" in str(e, 'utf-8'):
                        logging.info(
                            f"V1 API chart without Chart.yaml dependancies. Skipping chart dependancy list for {chart_meta['name']} at dir: {chart_dir}. Working dir: {target_dir}. Error details: {str(e, 'utf-8')}")
                    else:
                        logging.info(
                            f"Error processing helm dependancies for {chart_meta['name']} at source dir: {chart_dir}. Working dir: {target_dir}. Error details: {str(e, 'utf-8')}")

                self.parse_helm_dependency_output(o)

                if runner_filter.var_files:
                    var_files_helm_formatted = []
                    for var in runner_filter.var_files:
                        var_files_helm_formatted.append("--values")
                        var_files_helm_formatted.append(var)
                    try:
                        # --dependency-update needed to pull in deps before templating.
                        helmBinaryTemplateOutput = subprocess.Popen([self.helm_command, 'template', '--dependency-update', chart_dir] + var_files_helm_formatted, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
                        o, e = helmBinaryTemplateOutput.communicate()
                        logging.debug(
                            f"Ran helm command to template chart output. Chart: {chart_meta['name']}. dir: {target_dir}. Output: {str(o, 'utf-8')}")

                    except Exception:
                        logging.info(
                            f"Error processing helm chart {chart_meta['name']} at dir: {chart_dir}. Working dir: {target_dir}.",
                            exc_info=True,
                        )

                else:
                    try:
                        # --dependency-update needed to pull in deps before templating.
                        proc = subprocess.Popen([self.helm_command, 'template', '--dependency-update', chart_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
                        o, e = proc.communicate()
                        logging.debug(
                            f"Ran helm command to template chart output. Chart: {chart_meta['name']}. dir: {target_dir}. Output: {str(o, 'utf-8')}")
                
                    except Exception:
                        logging.info(
                            f"Error processing helm chart {chart_meta['name']} at dir: {chart_dir}. Working dir: {target_dir}.",
                            exc_info=True,
                        )
              

                output = str(o, 'utf-8')
                reader = io.StringIO(output)
                cur_source_file = None
                cur_writer = None
                last_line_dashes = False
                line_num = 1
                for s in reader:
                    s = s.rstrip()
                    if s == '---':
                        last_line_dashes = True
                        continue

                    if last_line_dashes:
                        # The next line should contain a "Source" comment saying the name of the file it came from
                        # So we will close the old file, open a new file, and write the dashes from last iteration plus this line

                        if not s.startswith('# Source: '):
                            raise Exception(f'Line {line_num}: Expected line to start with # Source: {s}')
                        source = s[10:]
                        if source != cur_source_file:
                            if cur_writer:
                                cur_writer.close()
                            file_path = os.path.join(target_dir, source)
                            parent = os.path.dirname(file_path)
                            os.makedirs(parent, exist_ok=True)
                            cur_source_file = source
                            cur_writer = open(os.path.join(target_dir, source), 'a')
                        cur_writer.write('---' + os.linesep)
                        cur_writer.write(s + os.linesep)

                        last_line_dashes = False
                    else:
                        if s.startswith('# Source: '):
                            raise Exception(f'Line {line_num}: Unexpected line starting with # Source: {s}')

                        if not cur_writer:
                            continue
                        else:
                            cur_writer.write(s + os.linesep)

                    line_num += 1

                if cur_writer:
                    cur_writer.close()

                try:
                    k8s_runner = k8_runner()
                    chart_results = k8s_runner.run(target_dir, external_checks_dir=external_checks_dir,
                                                   runner_filter=runner_filter, helmChart=chart_meta['name'])
                    logging.debug(f"Sucessfully ran k8s scan on {chart_meta['name']}. Scan dir : {target_dir}")
                    report.failed_checks += chart_results.failed_checks
                    report.passed_checks += chart_results.passed_checks
                    report.parsing_errors += chart_results.parsing_errors
                    report.skipped_checks += chart_results.skipped_checks
                    report.resources.update(chart_results.resources)

                except Exception:
                    logging.warning("Failed to run Kubernetes runner", exc_info=True)
                    with tempfile.TemporaryDirectory() as save_error_dir:
                        logging.debug(
                            f"Error running k8s scan on {chart_meta['name']}. Scan dir: {target_dir}. Saved context dir: {save_error_dir}")
                        shutil.move(target_dir, save_error_dir)

                        # TODO: Export helm dependancies for the chart we've extracted in chart_dependencies
        return report


def get_skipped_checks(entity_conf):
    skipped = []
    metadata = {}
    if not isinstance(entity_conf, dict):
        return skipped
    if entity_conf["kind"] == "containers" or entity_conf["kind"] == "initContainers":
        metadata = entity_conf["parent_metadata"]
    else:
        if "metadata" in entity_conf.keys():
            metadata = entity_conf["metadata"]
    if "annotations" in metadata.keys() and metadata["annotations"] is not None:
        for key in metadata["annotations"].keys():
            skipped_item = {}
            if "checkov.io/skip" in key or "bridgecrew.io/skip" in key:
                if "CKV_K8S" in metadata["annotations"][key]:
                    if "=" in metadata["annotations"][key]:
                        (skipped_item["id"], skipped_item["suppress_comment"]) = metadata["annotations"][key].split("=")
                    else:
                        skipped_item["id"] = metadata["annotations"][key]
                        skipped_item["suppress_comment"] = "No comment provided"
                    skipped.append(skipped_item)
                else:
                    logging.info(f"Parse of Annotation Failed for {metadata['annotations'][key]}: {entity_conf}")
                    continue
    return skipped


def _get_from_dict(data_dict, map_list):
    return reduce(operator.getitem, map_list, data_dict)


def _set_in_dict(data_dict, map_list, value):
    _get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value


def find_lines(node, kv):
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        for i in node:
            for x in find_lines(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in find_lines(j, kv):
                yield x
