from __future__ import annotations

import copy
import io
import logging
import multiprocessing
import os
import pathlib
import platform
import shutil
import subprocess  # nosec
import tempfile
import yaml
from typing import Optional, Dict, Any, Type, TextIO, TYPE_CHECKING

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.common.typing import _CheckResult
from checkov.kubernetes.kubernetes_utils import get_resource_id
from checkov.kubernetes.runner import Runner as K8sRunner
from checkov.kubernetes.runner import _get_entity_abs_path
from checkov.runner_filter import RunnerFilter
from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.kubernetes.graph_builder.local_graph import KubernetesLocalGraph

if TYPE_CHECKING:
    from checkov.common.checks.base_check import BaseCheck
    from checkov.kubernetes.graph_manager import KubernetesGraphManager


class K8sKustomizeRunner(K8sRunner):
    def __init__(
        self,
        graph_class: Type[KubernetesLocalGraph] = KubernetesLocalGraph,
        db_connector: NetworkxConnector | None = None,
        source: str = "Kubernetes",
        graph_manager: KubernetesGraphManager | None = None,
        external_registries: list[BaseRegistry] | None = None
    ) -> None:

        super().__init__(graph_class, db_connector, source, graph_manager, external_registries, CheckType.KUSTOMIZE)
        self.check_type = CheckType.KUSTOMIZE
        self.report_mutator_data = {}
        self.pbar.turn_off_progress_bar()

    def set_external_data(
        self,
        definitions: Optional[Dict[str, Dict[str, Any]]],
        context: Optional[Dict[str, Dict[str, Any]]],
        breadcrumbs: Optional[Dict[str, Dict[str, Any]]],
        report_mutator_data: Optional[Dict[str, Dict[str, Any]]]
    ) -> None:
        super().set_external_data(definitions, context, breadcrumbs)
        self.report_mutator_data = report_mutator_data

    def set_report_mutator_data(self, report_mutator_data: Optional[Dict[str, Dict[str, Any]]]) -> None:
        self.report_mutator_data = report_mutator_data

    def mutate_kubernetes_results(
        self,
        results: dict[BaseCheck, _CheckResult],
        report: Report,
        k8_file: str,
        k8_file_path: str,
        file_abs_path: str,
        entity_conf: dict[str, Any],
        variable_evaluations: dict[str, Any],
    ) -> Report:
        # Moves report generation logic out of checkov.kubernetes.runner.run() def.
        # Allows us to overriding report file information for "child" frameworks such as Kustomize, Helm
        # Where Kubernetes CHECKS are needed, but the specific file references are to another framework for the user output (or a mix of both).
        kustomizeMetadata = self.report_mutator_data['kustomizeMetadata'],
        kustomizeFileMappings = self.report_mutator_data['kustomizeFileMappings']
        for check, check_result in results.items():
            resource_id = get_resource_id(entity_conf)
            entity_context = self.context[k8_file][resource_id]

            if file_abs_path not in kustomizeFileMappings:
                logging.warning(f"couldn't find {file_abs_path} path in kustomizeFileMappings")
                continue

            realKustomizeEnvMetadata = kustomizeMetadata[0][kustomizeFileMappings[file_abs_path]]
            if 'overlay' in realKustomizeEnvMetadata["type"]:
                kustomizeResourceID = f'{realKustomizeEnvMetadata["type"]}:{str(realKustomizeEnvMetadata["overlay_name"])}:{resource_id}'
            else:
                kustomizeResourceID = f'{realKustomizeEnvMetadata["type"]}:{resource_id}'

            code_lines = entity_context.get("code_lines")
            file_line_range = self.line_range(code_lines)
            record = Record(
                check_id=check.id, bc_check_id=check.bc_id, check_name=check.name,
                check_result=check_result, code_block=code_lines, file_path=realKustomizeEnvMetadata['filePath'],
                file_line_range=file_line_range,
                resource=kustomizeResourceID, evaluations=variable_evaluations,
                check_class=check.__class__.__module__, file_abs_path=realKustomizeEnvMetadata['filePath'], severity=check.severity)
            record.set_guideline(check.guideline)
            report.add_record(record=record)

        return report

    def line_range(self, code_lines):
        num_of_lines = len(code_lines)
        file_line_range = [0, 0]
        if num_of_lines > 0:
            first_line, code = code_lines[0]
            last_line, code = code_lines[num_of_lines - 1]
            file_line_range = [first_line, last_line]
        return file_line_range

    def mutate_kubernetes_graph_results(self, root_folder: str, runner_filter: RunnerFilter, report: Report, checks_results) -> Report:
        # Moves report generation logic out of run() method in Runner class.
        # Allows function overriding of a much smaller function than run() for other "child" frameworks such as Kustomize, Helm
        # Where Kubernetes CHECKS are needed, but the specific file references are to another framework for the user output (or a mix of both).
        kustomizeMetadata = self.report_mutator_data['kustomizeMetadata'],
        kustomizeFileMappings = self.report_mutator_data['kustomizeFileMappings']

        for check, check_results in checks_results.items():
            for check_result in check_results:
                entity = check_result["entity"]
                entity_file_path = entity.get(CustomAttributes.FILE_PATH)
                entity_file_abs_path = _get_entity_abs_path(root_folder, entity_file_path)
                entity_id = entity.get(CustomAttributes.ID)
                entity_context = self.context[entity_file_path][entity_id]

                if entity_file_abs_path in kustomizeFileMappings:
                    realKustomizeEnvMetadata = kustomizeMetadata[0][kustomizeFileMappings[entity_file_abs_path]]
                    if 'overlay' in realKustomizeEnvMetadata["type"]:
                        kustomizeResourceID = f'{realKustomizeEnvMetadata["type"]}:{str(realKustomizeEnvMetadata["overlay_name"])}:{entity_id}'
                    else:
                        kustomizeResourceID = f'{realKustomizeEnvMetadata["type"]}:{entity_id}'
                else:
                    logging.warning(f"couldn't find {entity_file_abs_path} path in kustomizeFileMappings")
                    continue
                code_lines = entity_context.get("code_lines")
                file_line_range = self.line_range(code_lines)

                record = Record(
                    check_id=check.id,
                    check_name=check.name,
                    check_result=check_result,
                    code_block=entity_context.get("code_lines"),
                    file_path=realKustomizeEnvMetadata['filePath'],
                    file_line_range=file_line_range,
                    resource=kustomizeResourceID,  # entity.get(CustomAttributes.ID),
                    evaluations={},
                    check_class=check.__class__.__module__,
                    file_abs_path=entity_file_abs_path,
                    severity=check.severity
                )
                record.set_guideline(check.guideline)
                report.add_record(record=record)

        return report


class Runner(BaseRunner):
    kustomize_command = 'kustomize'  # noqa: CCE003  # a static attribute
    kubectl_command = 'kubectl'  # noqa: CCE003  # a static attribute
    check_type = CheckType.KUSTOMIZE  # noqa: CCE003  # a static attribute
    system_deps = True  # noqa: CCE003  # a static attribute
    kustomizeSupportedFileTypes = ('kustomization.yaml', 'kustomization.yml')  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__(file_names=Runner.kustomizeSupportedFileTypes)
        self.potentialBases = []
        self.potentialOverlays = []
        self.kustomizeProcessedFolderAndMeta = {}
        self.kustomizeFileMappings: dict[str, str] = {}
        self.templateRendererCommand: str | None = None
        self.target_folder_path = ''

    def get_k8s_target_folder_path(self) -> str:
        return self.target_folder_path

    def get_kustomize_metadata(self) -> dict[str, dict[str, Any]]:
        return {'kustomizeMetadata': self.kustomizeProcessedFolderAndMeta,
                'kustomizeFileMappings': self.kustomizeFileMappings}

    def _parseKustomization(self, parseKustomizationData):
        # We may have multiple results for "kustomization.yaml" files. These could be:
        # - Base and Environment (overlay) DIR's for the same kustomize-powered deployment
        # - OR, Multiple different Kustomize-powered deployments
        # - OR, a mixture of the two.
        # We need parse some of the Kustomization.yaml files to work out which
        # This is so we can provide "Environment" information back to the user as part of the checked resource name/description.
        # TODO: We could also add a --kustomize-environment option so we only scan certain overlay names (prod, test etc) useful in CI.
        yaml_path = os.path.join(parseKustomizationData, "kustomization.yaml")
        yml_path = os.path.join(parseKustomizationData, "kustomization.yml")
        if os.path.isfile(yml_path):
            kustomization_path = yml_path
        elif os.path.isfile(yaml_path):
            kustomization_path = yaml_path
        else:
            return {}

        with open(kustomization_path, 'r') as kustomizationFile:
            metadata = {}
            try:
                fileContent = yaml.safe_load(kustomizationFile)
            except yaml.YAMLError:
                logging.info(f"Failed to load Kustomize metadata from {kustomization_path}.", exc_info=True)

            if 'resources' in fileContent:
                logging.debug(f"Kustomization contains resources: section. Likley a base. {kustomization_path}")
                metadata['type'] = "base"

            elif 'patchesStrategicMerge' in fileContent:
                logging.debug(f"Kustomization contains patchesStrategicMerge: section. Likley an overlay/env. {kustomization_path}")
                metadata['type'] = "overlay"
                if 'bases' in fileContent:
                    metadata['referenced_bases'] = fileContent['bases']

            elif 'bases' in fileContent:
                logging.debug(f"Kustomization contains bases: section. Likley an overlay/env. {kustomization_path}")
                metadata['type'] = "overlay"
                metadata['referenced_bases'] = fileContent['bases']

            metadata['fileContent'] = fileContent
            metadata['filePath'] = f"{kustomization_path}"
            if metadata.get('type') == "base":
                self.potentialBases.append(metadata['filePath'])

            if metadata.get('type') == "overlay":
                self.potentialOverlays.append(metadata['filePath'])

        return metadata

    def check_system_deps(self):
        # Ensure local system dependancies are available and of the correct version.
        # Returns framework names to skip if deps **fail** (ie, return None for a successful deps check).
        logging.info(f"Checking necessary system dependancies for {self.check_type} checks.")

        if shutil.which(self.kubectl_command) is not None:
            try:
                proc = subprocess.Popen([self.kubectl_command, 'version', '--client=true'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
                o, e = proc.communicate()
                oString = str(o, 'utf-8')

                if "Client Version:" in oString:
                    kubectlVersionMajor = oString.split('\n')[0].split('Major:\"')[1].split('"')[0]
                    kubectlVersionMinor = oString.split('\n')[0].split('Minor:\"')[1].split('"')[0]
                    kubectlVersion = float(f"{kubectlVersionMajor}.{kubectlVersionMinor}")
                    if kubectlVersion >= 1.14:
                        logging.info(f"Found working version of {self.check_type} dependancy {self.kubectl_command}: {kubectlVersion}")
                        self.templateRendererCommand = self.kubectl_command
                        return None

            except Exception:
                logging.debug(f"An error occured testing the {self.kubectl_command} command: {e}")
                pass

        elif shutil.which(self.kustomize_command) is not None:

            try:
                proc = subprocess.Popen([self.kustomize_command, 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
                o, e = proc.communicate()
                oString = str(o, 'utf-8')

                if "Version:" in oString:
                    kustomizeVersionOutput = oString[oString.find('/') + 1: oString.find('G') - 1]
                    logging.info(f"Found working version of {self.check_type} dependancy {self.kustomize_command}: {kustomizeVersionOutput}")
                    self.templateRendererCommand = self.kustomize_command
                    return None
                else:
                    return self.check_type

            except Exception:
                logging.debug(f"An error occured testing the {self.kustomize_command} command: {e}")
                pass

        else:
            logging.info(f"Could not find usable tools locally to process {self.check_type} checks. Framework will be disabled for this run.")
            return self.check_type

    def _handle_overlay_case(self, file_path: str) -> None:
        for parent in pathlib.Path(file_path).parents:
            for potentialBase in self.potentialBases:
                pathlibBaseObject = pathlib.Path(potentialBase)
                potentialBasePath = pathlibBaseObject.parents[1]
                if parent == potentialBasePath.resolve():
                    self.kustomizeProcessedFolderAndMeta[file_path]['calculated_bases'] = str(pathlibBaseObject.parent)
        try:
            relativeToFullPath = f"{file_path}/{self.kustomizeProcessedFolderAndMeta[file_path]['referenced_bases'][0]}"
            if pathlib.Path(self.kustomizeProcessedFolderAndMeta[file_path]['calculated_bases']) == pathlib.Path(relativeToFullPath).resolve():
                self.kustomizeProcessedFolderAndMeta[file_path]['validated_base'] = str(pathlib.Path(self.kustomizeProcessedFolderAndMeta[file_path]['calculated_bases']))
                checkovKustomizeEnvNameByPath = pathlib.Path(file_path).relative_to(pathlib.Path(self.kustomizeProcessedFolderAndMeta[file_path]['calculated_bases']).parent)
                self.kustomizeProcessedFolderAndMeta[file_path]['overlay_name'] = str(checkovKustomizeEnvNameByPath)
                logging.debug(f"Overlay based on {self.kustomizeProcessedFolderAndMeta[file_path]['validated_base']}, naming overlay {checkovKustomizeEnvNameByPath} for Checkov Results.")
            else:
                checkovKustomizeEnvNameByPath = f"{pathlib.Path(file_path).stem}"
                self.kustomizeProcessedFolderAndMeta[file_path]['overlay_name'] = checkovKustomizeEnvNameByPath
                logging.debug(f"Could not confirm base dir for Kustomize overlay/env. Using {checkovKustomizeEnvNameByPath} for Checkov Results.")

        except KeyError:
            checkovKustomizeEnvNameByPath = f"{pathlib.Path(file_path).stem}"
            self.kustomizeProcessedFolderAndMeta[file_path]['overlay_name'] = checkovKustomizeEnvNameByPath
            logging.debug(f"Could not confirm base dir for Kustomize overlay/env. Using {checkovKustomizeEnvNameByPath} for Checkov Results.")

    @staticmethod
    def _get_parsed_output(
        file_path: str, extract_dir: str, output: str, shared_kustomize_file_mappings: dict[str, str]
    ) -> TextIO | None:
        cur_source_file = None
        cur_writer = None
        last_line_dashes = False
        line_num = 1
        file_num = 0

        # page-to-file parser from helm framework works well, but we expect the file to start with --- in this case from Kustomize.
        output = "---\n" + output
        reader = io.StringIO(output)
        for s in reader:
            s = s.rstrip()
            if s == '---':
                last_line_dashes = True
                continue

            if last_line_dashes:
                # The next line should contain a "apiVersion" line for the next Kubernetes manifest
                # So we will close the old file, open a new file, and write the dashes from last iteration plus this line
                source = file_num
                file_num += 1
                if source != cur_source_file:
                    if cur_writer:
                        # Here we are about to close a "complete" file. The function will validate it looks like a K8S manifest before continuing.
                        Runner._curWriterValidateStoreMapAndClose(cur_writer, file_path, shared_kustomize_file_mappings)
                    parent = os.path.dirname(os.path.join(extract_dir, str(source)))
                    os.makedirs(parent, exist_ok=True)
                    cur_source_file = source
                    cur_writer = open(os.path.join(extract_dir, str(source)), 'a')
                cur_writer.write('---' + os.linesep)
                cur_writer.write(s + os.linesep)
                last_line_dashes = False
            else:
                if not cur_writer:
                    continue
                else:
                    cur_writer.write(s + os.linesep)
            line_num += 1
        return cur_writer

    @staticmethod
    def _get_kubectl_output(filePath: str, template_renderer_command: str, source_type: str | None) -> bytes:
        # Template out the Kustomizations to Kubernetes YAML
        if template_renderer_command == "kubectl":
            template_render_command_options = "kustomize"
        if template_renderer_command == "kustomize":
            template_render_command_options = "build"
        proc = subprocess.Popen([template_renderer_command, template_render_command_options, filePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
        output, _ = proc.communicate()
        logging.info(
            f"Ran kubectl to build Kustomize output. DIR: {filePath}. TYPE: {source_type}.")
        return output

    @staticmethod
    def _get_env_or_base_path_prefix(
        file_path: str, kustomize_processed_folder_and_meta: dict[str, dict[str, Any]]
    ) -> str | None:
        env_or_base_path_prefix = None
        if kustomize_processed_folder_and_meta[file_path].get('type') == "overlay":
            if 'calculated_bases' not in kustomize_processed_folder_and_meta[file_path]:
                logging.debug(f"Kustomize: Overlay with unknown base. User may have specified overlay dir directly. {file_path}")
                env_or_base_path_prefix = ""
            else:
                basePathParents = pathlib.Path(kustomize_processed_folder_and_meta[file_path]['calculated_bases']).parents
                mostSignificantBasePath = "/" + basePathParents._parts[-3] + "/" + basePathParents._parts[-2] + "/" + basePathParents._parts[-1]
                env_or_base_path_prefix = f"{mostSignificantBasePath}/{kustomize_processed_folder_and_meta[file_path]['overlay_name']}"

        if kustomize_processed_folder_and_meta[file_path].get('type') == "base":
            # Validated base last three parents as a path
            basePathParents = pathlib.Path(kustomize_processed_folder_and_meta[file_path]['filePath']).parents
            mostSignificantBasePath = "/" + basePathParents._parts[-4] + "/" + basePathParents._parts[-3] + "/" + basePathParents._parts[-2]
            env_or_base_path_prefix = mostSignificantBasePath

        return env_or_base_path_prefix

    @staticmethod
    def get_binary_output(
        file_path: str,
        kustomize_processed_folder_and_meta: dict[str, dict[str, Any]],
        template_renderer_command: str,
    ) -> tuple[bytes, str] | tuple[None, None]:
        source_type = kustomize_processed_folder_and_meta[file_path].get('type')
        logging.debug(f"Kustomization at {file_path} likley a {source_type}")
        try:
            output = Runner._get_kubectl_output(file_path, template_renderer_command, source_type)
            return output, file_path
        except Exception:
            logging.warning(f"Error building Kustomize output at dir: {file_path}.", exc_info=True)
            return None, None

    @staticmethod
    def _parse_output(
        output: bytes,
        file_path: str,
        kustomize_processed_folder_and_meta: dict[str, dict[str, Any]],
        target_folder_path: str,
        shared_kustomize_file_mappings: dict[str, str],
    ) -> None:
        env_or_base_path_prefix = Runner._get_env_or_base_path_prefix(file_path, kustomize_processed_folder_and_meta)
        if env_or_base_path_prefix is None:
            logging.warning(f"env_or_base_path_prefix is None, filePath: {file_path}", exc_info=True)
            return

        extract_dir = target_folder_path + env_or_base_path_prefix
        os.makedirs(extract_dir, exist_ok=True)

        logging.debug(f"Kustomize: Temporary directory for {file_path} at {extract_dir}")
        output_str = output.decode("utf-8")
        cur_writer = Runner._get_parsed_output(file_path, extract_dir, output_str, shared_kustomize_file_mappings)
        if cur_writer:
            Runner._curWriterValidateStoreMapAndClose(cur_writer, file_path, shared_kustomize_file_mappings)

    @staticmethod
    def _run_kustomize_parser(
        filePath: str,
        sharedKustomizeFileMappings: dict[str, str],
        kustomizeProcessedFolderAndMeta: dict[str, dict[str, Any]],
        templateRendererCommand: str,
        target_folder_path: str,
    ) -> None:
        output, _ = Runner.get_binary_output(filePath, kustomizeProcessedFolderAndMeta, templateRendererCommand)
        if not output:
            return
        Runner._parse_output(output, filePath, kustomizeProcessedFolderAndMeta, target_folder_path, sharedKustomizeFileMappings)

    def run_kustomize_to_k8s(
        self, root_folder: str | None, files: list[str] | None, runner_filter: RunnerFilter
    ) -> None:
        kustomize_dirs = find_kustomize_directories(root_folder, files, runner_filter.excluded_paths)
        if not kustomize_dirs:
            # nothing to process
            return

        for kustomize_dir in kustomize_dirs:
            self.kustomizeProcessedFolderAndMeta[kustomize_dir] = self._parseKustomization(kustomize_dir)
        self.target_folder_path = tempfile.mkdtemp()
        for filePath in self.kustomizeProcessedFolderAndMeta:
            if self.kustomizeProcessedFolderAndMeta[filePath].get('type') == 'overlay':
                self._handle_overlay_case(filePath)

        if platform.system() == 'Windows':
            sharedKustomizeFileMappings: dict[str, str] = {}
            for filePath in self.kustomizeProcessedFolderAndMeta:
                Runner._run_kustomize_parser(filePath, sharedKustomizeFileMappings, self.kustomizeProcessedFolderAndMeta,
                                             self.templateRendererCommand, self.target_folder_path)
            self.kustomizeFileMappings = sharedKustomizeFileMappings
            return

        manager = multiprocessing.Manager()
        # make sure we have new dict
        sharedKustomizeFileMappings = copy.copy(manager.dict())
        sharedKustomizeFileMappings.clear()
        jobs = []
        for filePath in self.kustomizeProcessedFolderAndMeta:
            p = multiprocessing.Process(
                target=Runner._run_kustomize_parser,
                args=(
                    filePath,
                    sharedKustomizeFileMappings,
                    self.kustomizeProcessedFolderAndMeta,
                    self.templateRendererCommand,
                    self.target_folder_path
                )
            )
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()

        self.kustomizeFileMappings = dict(sharedKustomizeFileMappings)

    def run(
        self,
        root_folder: str | None,
        external_checks_dir: list[str] | None = None,
        files: list[str] | None = None,
        runner_filter: RunnerFilter | None = None,
        collect_skip_comments: bool = True,
    ) -> Report | list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

        self.run_kustomize_to_k8s(root_folder, files, runner_filter)
        report = Report(self.check_type)

        if not self.kustomizeProcessedFolderAndMeta:
            # nothing to process
            return report

        target_dir = ""
        try:
            k8s_runner = K8sKustomizeRunner()
            # k8s_runner.run() will kick off both CKV_ and CKV2_ checks and return a merged results object.
            target_dir = self.get_k8s_target_folder_path()
            k8s_runner.report_mutator_data = self.get_kustomize_metadata()

            # the returned report can be a list of reports, which also includes an SCA image report
            report = k8s_runner.run(target_dir, external_checks_dir=None, runner_filter=runner_filter)
            logging.debug(f"Sucessfully ran k8s scan on Kustomization templated files in tmp scan dir : {target_dir}")

            shutil.rmtree(target_dir)

        except Exception:
            logging.warning("Failed to run Kubernetes runner", exc_info=True)
            with tempfile.TemporaryDirectory() as save_error_dir:
                logging.debug(
                    f"Error running k8s scan on Scan dir: {target_dir}. Saved context dir: {save_error_dir}")
                shutil.move(target_dir, save_error_dir)

        return report

    @staticmethod
    def _curWriterValidateStoreMapAndClose(
        cur_writer: TextIO, file_path: str, shared_kustomize_file_mappings: dict[str, str]
    ) -> None:
        currentFileName = cur_writer.name
        cur_writer.close()
        # Now we have a complete k8s manifest as we closed the writer, and it's temporary file name (currentFileName) plus the original file templated out (FilePath)
        # Rename them to useful information from the K8S metadata before conting.
        # Then keep a mapping of template files to original kustomize repo locations for use with Checkov output later.
        try:
            with open(currentFileName) as f:
                currentYamlObject = yaml.safe_load(f)
                # Validate we have a K8S manifest
                if "apiVersion" in currentYamlObject:
                    itemName = []
                    itemName.append(currentYamlObject['kind'])
                    if 'namespace' in currentYamlObject['metadata']:
                        itemName.append(currentYamlObject['metadata']['namespace'])
                    else:
                        itemName.append("default")
                    if 'name' in currentYamlObject['metadata']:
                        itemName.append(currentYamlObject['metadata']['name'])
                    else:
                        itemName.append("noname")

                    filename = f"{'-'.join(itemName)}.yaml"
                    newFullPathFilename = str(pathlib.Path(currentFileName).parent / filename)
                    os.rename(currentFileName, newFullPathFilename)
                    shared_kustomize_file_mappings[newFullPathFilename] = file_path
                else:
                    raise Exception(f'Not a valid Kubernetes manifest (no apiVersion) while parsing Kustomize template: {file_path}. Templated output: {currentFileName}.')
        except IsADirectoryError:
            pass


def find_kustomize_directories(
    root_folder: str | None, files: list[str] | None, excluded_paths: list[str]
) -> list[str]:
    kustomize_directories = []
    if not excluded_paths:
        excluded_paths = []
    if files:
        logging.info('Running with --file argument; file must be a kustomization.yaml file')
        for file in files:
            if os.path.basename(file) in Runner.kustomizeSupportedFileTypes:
                kustomize_directories.append(os.path.dirname(file))

    if root_folder:
        for root, d_names, f_names in os.walk(root_folder):
            filter_ignored_paths(root, d_names, excluded_paths)
            filter_ignored_paths(root, f_names, excluded_paths)
            kustomize_directories.extend(
                os.path.abspath(root) for x in f_names if x in Runner.kustomizeSupportedFileTypes
            )

    return kustomize_directories
