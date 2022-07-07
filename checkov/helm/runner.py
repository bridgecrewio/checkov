from __future__ import annotations

import io
import itertools
import logging
import os
import subprocess  # nosec
import tempfile
from typing import Any, Type, Optional, List
import yaml

from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.common.graph.graph_manager import GraphManager
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.common.output.report import Report, CheckType
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.helm.registry import registry
from checkov.kubernetes.graph_builder.local_graph import KubernetesLocalGraph
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.runner_filter import RunnerFilter
from checkov.common.parallelizer.parallel_runner import parallel_runner


class K8sHelmRunner(k8_runner):
    def __init__(self, graph_class: Type[LocalGraph] = KubernetesLocalGraph,
                 db_connector: NetworkxConnector = NetworkxConnector(),
                 source: str = "Kubernetes",
                 graph_manager: Optional[GraphManager] = None,
                 external_registries: Optional[List[BaseRegistry]] = None) -> None:
        self.check_type = CheckType.HELM
        super().__init__(graph_class, db_connector, source, graph_manager, external_registries)
        self.chart_dir_and_meta = []
        self.pbar.turn_off_progress_bar()

    def run(self, root_folder: str | None, external_checks_dir: list[str] | None = None, files: list[str] | None = None,
            runner_filter: RunnerFilter = RunnerFilter(), collect_skip_comments: bool = True) -> Report:
        report = Report(self.check_type)
        if not self.chart_dir_and_meta:
            return report
        if external_checks_dir:
            for directory in external_checks_dir:
                registry.load_external_checks(directory)
        try:
            chart_results = super().run(root_folder, external_checks_dir=external_checks_dir, runner_filter=runner_filter)
            fix_report_paths(chart_results, root_folder)
            return chart_results
        except Exception:
            logging.warning(f"Failed to run Kubernetes runner on charts {self.chart_dir_and_meta}", exc_info=True)
            # with tempfile.TemporaryDirectory() as save_error_dir:
            # TODO this will crash the run when target_dir gets cleaned up, since it no longer exists
            # we either need to copy or find another way to extract whatever we want to get from this (the TODO below)
            # logging.debug(
            #    f"Error running k8s scan on {chart_meta['name']}. Scan dir: {target_dir}. Saved context dir: {save_error_dir}")
            # shutil.move(target_dir, save_error_dir)

            # TODO: Export helm dependancies for the chart we've extracted in chart_dependencies
            return report


class Runner(BaseRunner):
    check_type = CheckType.HELM
    helm_command = 'helm'
    system_deps = True

    def __init__(self):
        super().__init__()
        self.file_names = ['Chart.yaml']
        self.target_folder_path = ''
        self.root_folder = ''
        self.runner_filter = None

    def get_k8s_target_folder_path(self) -> str:
        return self.target_folder_path

    @staticmethod
    def parse_helm_chart_details(chart_path: str) -> dict[str, Any] | None:
        with open(f"{chart_path}/Chart.yaml", 'r') as chartyaml:
            try:
                chart_meta = yaml.safe_load(chartyaml)
            except yaml.YAMLError:
                logging.info(f"Failed to load chart metadata from {chart_path}/Chart.yaml.", exc_info=True)
                return None
        return chart_meta

    def check_system_deps(self) -> str | None:
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

    def _parse_output(self, target_dir: str, output: bytes) -> None:
        output = str(output, 'utf-8')
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

    def _convert_chart_to_k8s(self, chart_item):
        (chart_dir, chart_meta) = chart_item
        target_dir = chart_dir.replace(self.root_folder, f'{self.target_folder_path}/')
        target_dir.replace("//", "/")
        chart_name = chart_meta.get('name', chart_meta.get('Name'))
        chart_version = chart_meta.get('version', chart_meta.get('Version'))
        if target_dir.endswith('/'):
            target_dir = target_dir[:-1]
        if target_dir.endswith(chart_name):
            target_dir = target_dir[:-len(chart_name)]
        logging.info(
            f"Processing chart found at: {chart_dir}, name: {chart_name}, version: {chart_version}")
        # dependency list is nicer to parse than dependency update.
        helm_binary_list_chart_deps = subprocess.Popen([self.helm_command, 'dependency', 'list', chart_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
        o, e = helm_binary_list_chart_deps.communicate()
        logging.debug(
            f"Ran helm command to get dependency output. Chart: {chart_name}. dir: {target_dir}. Output: {str(o, 'utf-8')}. Errors: {str(e, 'utf-8')}")
        if e:
            if "Warning: Dependencies" in str(e, 'utf-8'):
                logging.warning(
                    f"V1 API chart without Chart.yaml dependancies. Skipping chart dependancy list for {chart_name} at dir: {chart_dir}. Working dir: {target_dir}. Error details: {str(e, 'utf-8')}")
            else:
                logging.warning(
                    f"Error processing helm dependancies for {chart_name} at source dir: {chart_dir}. Working dir: {target_dir}. Error details: {str(e, 'utf-8')}")

        helm_command_args = [self.helm_command, 'template', '--dependency-update', chart_dir]
        if self.runner_filter.var_files:
            for var in self.runner_filter.var_files:
                helm_command_args.append("--values")
                helm_command_args.append(var)

        try:
            # --dependency-update needed to pull in deps before templating.
            proc = subprocess.Popen(helm_command_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
            o, e = proc.communicate()
            if e:
                logging.warning(
                    f"Error processing helm chart {chart_name} at dir: {chart_dir}. Working dir: {target_dir}. Error details: {str(e, 'utf-8')}")
            logging.debug(
                f"Ran helm command to template chart output. Chart: {chart_name}. dir: {target_dir}. Output: {str(o, 'utf-8')}. Errors: {str(e, 'utf-8')}")

        except Exception:
            logging.info(
                f"Error processing helm chart {chart_name} at dir: {chart_dir}. Working dir: {target_dir}.",
                exc_info=True,
            )

        try:
            self._parse_output(target_dir, o)
        except Exception:
            logging.info(
                f"Error parsing output {chart_name} at dir: {chart_dir}. Working dir: {target_dir}.",
                exc_info=True,
            )

    def convert_helm_to_k8s(self, root_folder: str, files: list[str], runner_filter: RunnerFilter) -> list[tuple[Any, dict[str, Any]]]:
        self.root_folder = root_folder
        self.runner_filter = runner_filter
        chart_directories = find_chart_directories(root_folder, files, runner_filter.excluded_paths)
        chart_dir_and_meta = list(parallel_runner.run_function(
            lambda cd: (cd, self.parse_helm_chart_details(cd)), chart_directories))
        # remove parsing failures
        chart_dir_and_meta = [chart_meta for chart_meta in chart_dir_and_meta if chart_meta[1]]
        self.target_folder_path = tempfile.mkdtemp()

        processed_chart_dir_and_meta = []
        for chart_dir, chart_meta in chart_dir_and_meta:
            processed_chart_dir_and_meta.append((chart_dir.replace(root_folder, ""), chart_meta))

        list(parallel_runner.run_function(lambda cd: self._convert_chart_to_k8s(cd), chart_dir_and_meta))
        return processed_chart_dir_and_meta

    def run(self, root_folder: str | None, external_checks_dir: list[str] | None = None, files: list[str] | None = None,
            runner_filter: RunnerFilter = RunnerFilter(), collect_skip_comments: bool = True) -> Report:
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

        k8s_runner = K8sHelmRunner()
        k8s_runner.chart_dir_and_meta = self.convert_helm_to_k8s(root_folder, files, runner_filter)
        return k8s_runner.run(self.get_k8s_target_folder_path(), external_checks_dir=external_checks_dir, runner_filter=runner_filter)


def fix_report_paths(report: Report, tmp_dir: str) -> None:
    for check in itertools.chain(report.failed_checks, report.passed_checks):
        check.repo_file_path = check.repo_file_path.replace(tmp_dir, '', 1)
        check.file_abs_path = check.file_abs_path.replace(tmp_dir, '', 1)
    report.resources = {r.replace(tmp_dir, '', 1) for r in report.resources}


def get_skipped_checks(entity_conf: dict) -> List:
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


def find_chart_directories(root_folder: str, files: list[str], excluded_paths: list[str]) -> List[str]:
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
