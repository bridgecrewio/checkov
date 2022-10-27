from __future__ import annotations

import io
import itertools
import logging
import os
import subprocess  # nosec
import tempfile
import threading
from typing import Any, Type, TYPE_CHECKING
import yaml

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.output.report import Report
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.helm.registry import registry
from checkov.kubernetes.graph_builder.local_graph import KubernetesLocalGraph
from checkov.kubernetes.runner import Runner as k8_runner, handle_timeout
from checkov.runner_filter import RunnerFilter
import signal

if TYPE_CHECKING:
    from checkov.kubernetes.graph_manager import KubernetesGraphManager


class K8sHelmRunner(k8_runner):
    def __init__(
        self,
        graph_class: Type[KubernetesLocalGraph] = KubernetesLocalGraph,
        db_connector: NetworkxConnector | None = None,
        source: str = "Kubernetes",
        graph_manager: KubernetesGraphManager | None = None,
        external_registries: list[BaseRegistry] | None = None
    ) -> None:
        db_connector = db_connector or NetworkxConnector()

        self.check_type = CheckType.HELM
        super().__init__(graph_class, db_connector, source, graph_manager, external_registries)
        self.chart_dir_and_meta: list[tuple[str, dict[str, Any]]] = []
        self.pbar.turn_off_progress_bar()

    def run(
        self,
        root_folder: str | None,
        external_checks_dir: list[str] | None = None,
        files: list[str] | None = None,
        runner_filter: RunnerFilter | None = None,
        collect_skip_comments: bool = True
    ) -> Report | list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        report = Report(self.check_type)

        if not self.chart_dir_and_meta:
            return report
        if external_checks_dir:
            for directory in external_checks_dir:
                registry.load_external_checks(directory)
        try:
            chart_results = super().run(root_folder, external_checks_dir=external_checks_dir, runner_filter=runner_filter)

            if isinstance(chart_results, list):
                helm_report = next(chart_result for chart_result in chart_results if chart_result.check_type == self.check_type)
            else:
                helm_report = chart_results

            fix_report_paths(helm_report, root_folder)

            return chart_results
        except Exception:
            logging.warning(f"Failed to run Kubernetes runner on charts {self.chart_dir_and_meta}", exc_info=True)
            # with tempfile.TemporaryDirectory() as save_error_dir:
            # TODO this will crash the run when target_dir gets cleaned up, since it no longer exists
            # we either need to copy or find another way to extract whatever we want to get from this (the TODO below)
            # logging.debug(
            #    f"Error running k8s scan on {chart_meta['name']}. Scan dir: {target_dir}. Saved context dir: {save_error_dir}")
            # shutil.move(target_dir, save_error_dir)

            # TODO: Export helm dependencies for the chart we've extracted in chart_dependencies
            return report


class Runner(BaseRunner):
    check_type: str = CheckType.HELM  # noqa: CCE003  # a static attribute
    helm_command = 'helm'  # noqa: CCE003  # a static attribute
    system_deps = True  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
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
                chart_meta: dict[str, Any] = yaml.safe_load(chartyaml)
            except (yaml.YAMLError, UnicodeDecodeError):
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

    @staticmethod
    def _parse_output(target_dir: str, output: bytes) -> None:
        output_str = str(output, 'utf-8')
        reader = io.StringIO(output_str)
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

    @staticmethod
    def _get_target_dir(chart_item: tuple[str, dict[str, Any]], root_folder: str, target_folder_path: str) -> str | None:
        (chart_dir, chart_meta) = chart_item
        target_dir = chart_dir.replace(root_folder, f'{target_folder_path}/')
        target_dir.replace("//", "/")
        chart_name = chart_meta.get('name', chart_meta.get('Name'))
        if not chart_name:
            logging.info(
                f"Error parsing chart located {chart_dir}, chart has no name available",
                exc_info=True,
            )
            return None
        if target_dir.endswith('/'):
            target_dir = target_dir[:-1]
        if target_dir.endswith(chart_name):
            target_dir = target_dir[:-len(chart_name)]
        return target_dir

    @staticmethod
    def get_binary_output(
        chart_item: tuple[str, dict[str, Any]], target_dir: str, helm_command: str, runner_filter: RunnerFilter, timeout: int = 3600
    ) -> tuple[bytes, tuple[str, dict[str, Any]]] | tuple[None, None]:
        (chart_dir, chart_meta) = chart_item
        chart_name = chart_meta.get('name', chart_meta.get('Name'))
        chart_version = chart_meta.get('version', chart_meta.get('Version'))
        logging.info(
            f"Processing chart found at: {chart_dir}, name: {chart_name}, version: {chart_version}")
        # dependency list is nicer to parse than dependency update.
        try:
            helm_binary_list_chart_deps = subprocess.Popen([helm_command, 'dependency', 'list', chart_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
            o, e = helm_binary_list_chart_deps.communicate()
        except Exception:
            logging.error('Error run helm command', exc_info=True)
            return None, None
        logging.debug(
            f"Ran helm command to get dependency output. Chart: {chart_name}. dir: {target_dir}. Output: {str(o, 'utf-8')}. Errors: {str(e, 'utf-8')}")
        if e:
            if "Warning: Dependencies" in str(e, 'utf-8'):
                logging.warning(
                    f"V1 API chart without Chart.yaml dependancies. Skipping chart dependancy list for {chart_name} at dir: {chart_dir}. Working dir: {target_dir}. Error details: {str(e, 'utf-8')}")
            else:
                logging.warning(
                    f"Error processing helm dependancies for {chart_name} at source dir: {chart_dir}. Working dir: {target_dir}. Error details: {str(e, 'utf-8')}")

        helm_command_args = [helm_command, 'template', '--dependency-update', chart_dir]
        if runner_filter.var_files:
            for var in runner_filter.var_files:
                helm_command_args.append("--values")
                helm_command_args.append(var)

        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGALRM, handle_timeout)
            signal.alarm(timeout)

        try:
            # --dependency-update needed to pull in deps before templating.
            proc = subprocess.Popen(helm_command_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
            o, e = proc.communicate()
            if threading.current_thread() is threading.main_thread():
                signal.alarm(0)
            if e:
                logging.warning(
                    f"Error processing helm chart {chart_name} at dir: {chart_dir}. Working dir: {target_dir}. Error details: {str(e, 'utf-8')}")
                return None, None
            logging.debug(
                f"Ran helm command to template chart output. Chart: {chart_name}. dir: {target_dir}. Output: {str(o, 'utf-8')}. Errors: {str(e, 'utf-8')}")
            logging.info(f'Done helm run for: {chart_dir}')
            return o, chart_item

        except Exception as e:
            if threading.current_thread() is threading.main_thread():
                signal.alarm(0)
            if isinstance(e, TimeoutError):
                logging.info(
                    f"Error processing helm chart {chart_name} at dir: {chart_dir}. Working dir: {target_dir}. got timeout"
                )
            else:
                logging.info(
                    f"Error processing helm chart {chart_name} at dir: {chart_dir}. Working dir: {target_dir}.",
                    exc_info=True,
                )
            return None, None

    @staticmethod
    def _convert_chart_to_k8s(
        chart_item: tuple[str, dict[str, Any]],
        root_folder: str,
        target_folder_path: str,
        helm_command: str,
        runner_filter: RunnerFilter,
    ) -> None:
        target_dir = Runner._get_target_dir(chart_item, root_folder, target_folder_path)
        if not target_dir:
            return
        o, _ = Runner.get_binary_output(chart_item, target_folder_path, helm_command, runner_filter)
        try:
            Runner._parse_output(target_dir, o)
        except Exception:
            (chart_dir, chart_meta) = chart_item
            chart_name = chart_meta.get('name', chart_meta.get('Name'))
            logging.info(
                f"Error parsing output {chart_name} at dir: {chart_dir}. Working dir: {target_dir}.",
                exc_info=True,
            )

    @staticmethod
    def _get_chart_dir_and_meta(
        root_folder: str, files: list[str], runner_filter: RunnerFilter
    ) -> list[tuple[str, dict[str, Any]]]:
        chart_directories = find_chart_directories(root_folder, files, runner_filter.excluded_paths)
        chart_dir_and_meta = list(parallel_runner.run_function(
            lambda cd: (cd, Runner.parse_helm_chart_details(cd)), chart_directories))
        # remove parsing failures
        chart_dir_and_meta = [chart_meta for chart_meta in chart_dir_and_meta if chart_meta[1]]
        return chart_dir_and_meta

    @staticmethod
    def _get_processed_chart_dir_and_meta(
        chart_dir_and_meta: list[tuple[str, dict[str, Any]]], root_folder: str
    ) -> list[tuple[str, dict[str, Any]]]:
        processed_chart_dir_and_meta = []
        for chart_dir, chart_meta in chart_dir_and_meta:
            processed_chart_dir_and_meta.append((chart_dir.replace(root_folder, ""), chart_meta))
        return processed_chart_dir_and_meta

    def convert_helm_to_k8s(
        self, root_folder: str | None, files: list[str] | None, runner_filter: RunnerFilter
    ) -> list[tuple[Any, dict[str, Any]]]:
        self.root_folder = root_folder
        self.runner_filter = runner_filter
        self.target_folder_path = tempfile.mkdtemp()
        chart_dir_and_meta = Runner._get_chart_dir_and_meta(self.root_folder, files, self.runner_filter)

        list(
            parallel_runner.run_function(
                lambda cd: Runner._convert_chart_to_k8s(
                    chart_item=cd,
                    root_folder=self.root_folder,
                    target_folder_path=self.target_folder_path,
                    helm_command=self.helm_command,
                    runner_filter=self.runner_filter,
                ),
                chart_dir_and_meta,
            )
        )
        return Runner._get_processed_chart_dir_and_meta(chart_dir_and_meta, self.root_folder)

    def run(
        self,
        root_folder: str | None,
        external_checks_dir: list[str] | None = None,
        files: list[str] | None = None,
        runner_filter: RunnerFilter | None = None,
        collect_skip_comments: bool = True
    ) -> Report | list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

        k8s_runner = K8sHelmRunner()
        k8s_runner.chart_dir_and_meta = self.convert_helm_to_k8s(root_folder, files, runner_filter)
        return k8s_runner.run(self.get_k8s_target_folder_path(), external_checks_dir=external_checks_dir, runner_filter=runner_filter)


def fix_report_paths(report: Report, tmp_dir: str) -> None:
    for check in itertools.chain(report.failed_checks, report.passed_checks):
        check.repo_file_path = check.repo_file_path.replace(tmp_dir, '', 1)
    report.resources = {r.replace(tmp_dir, '', 1) for r in report.resources}


def get_skipped_checks(entity_conf: dict[str, Any]) -> list[dict[str, str]]:
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


def find_chart_directories(root_folder: str | None, files: list[str] | None, excluded_paths: list[str]) -> list[str]:
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
