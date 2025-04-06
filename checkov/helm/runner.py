from __future__ import annotations

import io
import itertools
import logging
import os
import shutil
import subprocess  # nosec
import tempfile
import threading
from typing import Any, Type, TYPE_CHECKING
import yaml

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.common.typing import LibraryGraphConnector
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.images.image_referencer import fix_related_resource_ids, Image
from checkov.common.output.report import Report
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.helm.image_referencer.manager import HelmImageReferencerManager
from checkov.helm.registry import registry
from checkov.kubernetes.graph_builder.local_graph import KubernetesLocalGraph
from checkov.kubernetes.runner import Runner as k8_runner, handle_timeout, _KubernetesContext, _KubernetesDefinitions
from checkov.runner_filter import RunnerFilter
import signal

if TYPE_CHECKING:
    from checkov.kubernetes.graph_manager import KubernetesGraphManager
    from networkx import DiGraph


class K8sHelmRunner(k8_runner):
    check_type = CheckType.HELM  # noqa: CCE003  # a static attribute

    def __init__(
        self,
        graph_class: Type[KubernetesLocalGraph] = KubernetesLocalGraph,
        db_connector: LibraryGraphConnector | None = None,
        source: str = GraphSource.KUBERNETES,
        graph_manager: KubernetesGraphManager | None = None,
        external_registries: list[BaseRegistry] | None = None
    ) -> None:
        super().__init__(graph_class, db_connector, source, graph_manager, external_registries)
        self.chart_dir_and_meta: list[tuple[str, dict[str, Any]]] = []
        self.pbar.turn_off_progress_bar()
        self.original_root_dir = ''
        self.tmp_root_dir = ''

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
                helm_report = next(
                    chart_result for chart_result in chart_results if chart_result.check_type == self.check_type
                )
                sca_image_report = next(
                    chart_result for chart_result in chart_results if chart_result.check_type == CheckType.SCA_IMAGE
                )
            else:
                helm_report = chart_results
                sca_image_report = None

            if root_folder is not None:
                fix_report_paths(report=helm_report, tmp_dir=root_folder)
                if self.original_root_dir:
                    fix_related_resource_ids(report=sca_image_report, tmp_dir=self.original_root_dir)
                else:
                    fix_related_resource_ids(report=sca_image_report, tmp_dir=root_folder)

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

    def get_image_report(self, root_folder: str | None, runner_filter: RunnerFilter) -> Report | None:
        if not self.graph_manager:
            return None
        return self.check_container_image_references(
            graph_connector=self.graph_manager.get_reader_endpoint(),
            root_path=self.original_root_dir,
            runner_filter=runner_filter,
        )

    def extract_images(
            self,
            graph_connector: DiGraph | None = None,
            definitions: None = None,
            definitions_raw: dict[str, list[tuple[int, str]]] | None = None
    ) -> list[Image]:
        if not graph_connector:
            # should not happen
            return []

        manager = HelmImageReferencerManager(graph_connector=graph_connector, original_root_dir=self.original_root_dir,
                                             temp_root_dir=self.tmp_root_dir)
        images = manager.extract_images_from_resources()

        return images


class Runner(BaseRunner[_KubernetesDefinitions, _KubernetesContext, "KubernetesGraphManager"]):
    check_type: str = CheckType.HELM  # noqa: CCE003  # a static attribute
    helm_command = 'helm'  # noqa: CCE003  # a static attribute
    system_deps = True  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__()
        self.file_names = ['Chart.yaml']
        self.target_folder_path = ''
        self.root_folder = ''
        self.runner_filter: "RunnerFilter | None" = None

    def get_k8s_target_folder_path(self) -> str:
        return self.target_folder_path

    @staticmethod
    def parse_helm_chart_details(chart_path: str) -> tuple[str, dict[str, Any] | None]:
        with open(f"{chart_path}/Chart.yaml", 'r') as chartyaml:
            try:
                chart_meta: dict[str, Any] = yaml.safe_load(chartyaml)
            except (yaml.YAMLError, UnicodeDecodeError):
                logging.info(f"Failed to load chart metadata from {chart_path}/Chart.yaml.", exc_info=True)
                return chart_path, None
        return chart_path, chart_meta

    def check_system_deps(self) -> str | None:
        # Ensure local system dependencies are available and of the correct version.
        # Returns framework names to skip if deps fail.
        logging.info(f"Checking necessary system dependencies for {self.check_type} checks.")
        try:
            proc = subprocess.Popen([self.helm_command, 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
            o, e = proc.communicate()
            oString = str(o, 'utf-8')
            if "Version:" in oString:
                helmVersionOutput = oString[oString.find(':') + 2: oString.find(',') - 1]
                if "v3" in helmVersionOutput:
                    logging.info(f"Found working version of {self.check_type} dependencies: {helmVersionOutput}")
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
                if cur_writer:
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
    def get_binary_output_from_directory(chart_dir: str, target_dir: str, helm_command: str,
                                         runner_filter: RunnerFilter, timeout: int = 3600) \
            -> tuple[bytes, tuple[str, dict[str, Any]]] | tuple[None, None]:
        _, chart_meta = Runner.parse_helm_chart_details(chart_dir)
        chart_item = (chart_dir, chart_meta or {})
        return Runner.get_binary_output(chart_item, target_dir, helm_command, runner_filter, timeout)

    @staticmethod
    def get_binary_output(
        chart_item: tuple[str, dict[str, Any]], target_dir: str, helm_command: str, runner_filter: RunnerFilter, timeout: int = 3600
    ) -> tuple[bytes, tuple[str, dict[str, Any]]] | tuple[None, None]:
        (chart_dir, chart_meta) = chart_item
        if not isinstance(chart_meta, dict):
            logging.error(f"invalid chart meta {chart_meta}")
            return None, None
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
                    f"V1 API chart without Chart.yaml dependencies. Skipping chart dependancy list for {chart_name} at dir: {chart_dir}. Working dir: {target_dir}. Error details: {str(e, 'utf-8')}")
            else:
                logging.warning(
                    f"Error processing helm dependencies for {chart_name} at source dir: {chart_dir}. Working dir: {target_dir}. Error details: {str(e, 'utf-8')}")

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
                    f"Failed processing helm chart {chart_name} at dir: {chart_dir}. Working dir: {target_dir}. Failure details: {str(e, 'utf-8')}")
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
        if o is None:
            return

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
        root_folder: str | None, files: list[str] | None, runner_filter: RunnerFilter
    ) -> list[tuple[str, dict[str, Any]]]:
        chart_directories = find_chart_directories(root_folder, files, runner_filter.excluded_paths)
        chart_dir_and_meta = parallel_runner.run_function(func=Runner.parse_helm_chart_details, items=chart_directories)
        # remove parsing failures
        cleaned_chart_dir_and_meta = [(chart_dir, meta) for chart_dir, meta in chart_dir_and_meta if meta]
        return cleaned_chart_dir_and_meta

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
        self.root_folder = root_folder or ""
        self.runner_filter = runner_filter
        self.target_folder_path = tempfile.mkdtemp()
        chart_dir_and_meta = Runner._get_chart_dir_and_meta(self.root_folder, files, runner_filter)
        chart_items = [
            (chart_item, self.root_folder, self.target_folder_path, self.helm_command, runner_filter)
            for chart_item in chart_dir_and_meta
        ]

        list(parallel_runner.run_function(func=Runner._convert_chart_to_k8s, items=chart_items))
        return Runner._get_processed_chart_dir_and_meta(chart_dir_and_meta, self.root_folder)

    def remove_target_folder(self) -> None:
        try:
            shutil.rmtree(self.target_folder_path)  # delete directory
        except OSError as exc:
            logging.debug("failed to remove helm target folder path", exc_info=exc)

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
        k8s_runner.original_root_dir = str(root_folder)
        k8s_runner.tmp_root_dir = self.get_k8s_target_folder_path()
        report = k8s_runner.run(self.get_k8s_target_folder_path(), external_checks_dir=external_checks_dir, runner_filter=runner_filter)
        self.graph_manager = k8s_runner.graph_manager
        self.remove_target_folder()
        return report


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
