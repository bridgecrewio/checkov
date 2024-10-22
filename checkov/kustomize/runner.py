from __future__ import annotations

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
from typing import Optional, Dict, Any, TextIO, TYPE_CHECKING


from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.images.image_referencer import Image
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.common.typing import _CheckResult, _EntityContext
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.common.util.type_forcers import convert_str_to_bool
from checkov.kubernetes.kubernetes_utils import create_check_result, get_resource_id, calculate_code_lines, \
    PARENT_RESOURCE_ID_KEY_NAME
from checkov.kubernetes.runner import Runner as K8sRunner, _get_entity_abs_path, _KubernetesContext, _KubernetesDefinitions
from checkov.kustomize.image_referencer.manager import KustomizeImageReferencerManager
from checkov.kustomize.utils import get_kustomize_version, get_kubectl_version
from checkov.runner_filter import RunnerFilter
from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.common.typing import LibraryGraphConnector
from checkov.kubernetes.graph_builder.local_graph import KubernetesLocalGraph

if TYPE_CHECKING:
    from checkov.common.checks.base_check import BaseCheck
    from checkov.common.graph.checks_infra.base_check import BaseGraphCheck
    from checkov.kubernetes.graph_manager import KubernetesGraphManager
    from networkx import DiGraph


class K8sKustomizeRunner(K8sRunner):
    def __init__(
        self,
        graph_class: type[KubernetesLocalGraph] = KubernetesLocalGraph,
        db_connector: LibraryGraphConnector | None = None,
        source: str = GraphSource.KUBERNETES,
        graph_manager: KubernetesGraphManager | None = None,
        external_registries: list[BaseRegistry] | None = None
    ) -> None:

        super().__init__(graph_class, db_connector, source, graph_manager, external_registries, CheckType.KUSTOMIZE)
        self.check_type = CheckType.KUSTOMIZE
        self.report_mutator_data: "dict[str, dict[str, Any]]" = {}
        self.original_root_dir: str = ''
        self.pbar.turn_off_progress_bar()

        # Allows using kustomize commands to directly edit the user's kustomization.yaml configurations
        self.checkov_allow_kustomize_file_edits = convert_str_to_bool(os.getenv("CHECKOV_ALLOW_KUSTOMIZE_FILE_EDITS",
                                                                                False))

    def set_external_data(
        self,
        definitions: _KubernetesDefinitions | None,
        context: dict[str, dict[str, Any]] | None,
        breadcrumbs: dict[str, dict[str, Any]] | None,
        report_mutator_data: dict[str, dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().set_external_data(definitions, context, breadcrumbs)
        self.report_mutator_data = report_mutator_data or {}

    def set_report_mutator_data(self, report_mutator_data: Optional[Dict[str, Dict[str, Any]]]) -> None:
        self.report_mutator_data = report_mutator_data or {}

    def mutate_kubernetes_results(
        self,
        results: dict[BaseCheck, _CheckResult],
        report: Report,
        k8_file: str,
        k8_file_path: str,
        file_abs_path: str,
        entity_conf: dict[str, Any],
        variable_evaluations: dict[str, Any],
        root_folder: str | None = None
    ) -> Report:
        # Moves report generation logic out of checkov.kubernetes.runner.run() def.
        # Allows us to overriding report file information for "child" frameworks such as Kustomize, Helm
        # Where Kubernetes CHECKS are needed, but the specific file references are to another framework for the user output (or a mix of both).
        if not self.context:
            # this shouldn't happen
            logging.error("context was not set correctly")
            return report

        kustomize_metadata = self.report_mutator_data['kustomizeMetadata'],
        kustomize_file_mappings = self.report_mutator_data['kustomizeFileMappings']
        for check, check_result in results.items():
            resource_id = get_resource_id(entity_conf)
            if not resource_id:
                logging.error(f"Couldn't get resource ID for {entity_conf}")
                continue

            entity_context = self.context[k8_file][resource_id]

            if file_abs_path not in kustomize_file_mappings:
                logging.warning(f"couldn't find {file_abs_path} path in kustomizeFileMappings")
                continue

            realKustomizeEnvMetadata = kustomize_metadata[0][kustomize_file_mappings[file_abs_path]]
            if 'overlay' in realKustomizeEnvMetadata["type"]:
                kustomizeResourceID = f'{realKustomizeEnvMetadata["type"]}:{str(realKustomizeEnvMetadata["overlay_name"])}:{resource_id}'
            else:
                kustomizeResourceID = f'{realKustomizeEnvMetadata["type"]}:{resource_id}'

            external_run_indicator = "Bc"
            file_path = realKustomizeEnvMetadata['filePath']

            caller_file_path = None
            caller_file_line_range = None

            # means this scan originated in the platform
            if type(self.graph_manager).__name__.startswith(external_run_indicator):
                absolute_file_path = file_abs_path
            else:
                absolute_file_path = realKustomizeEnvMetadata['filePath']
                # Fix file path to repo relative path
                if self.original_root_dir:
                    repo_dir = str(pathlib.Path(self.original_root_dir).resolve())

                    if realKustomizeEnvMetadata['filePath'].startswith(repo_dir):
                        file_path = realKustomizeEnvMetadata['filePath'][len(repo_dir):]

            if self.checkov_allow_kustomize_file_edits:
                caller_resource_id = resource_id
                if PARENT_RESOURCE_ID_KEY_NAME in entity_conf:
                    caller_resource_id = entity_conf[PARENT_RESOURCE_ID_KEY_NAME]
                caller_file_line_range, caller_file_path = self._get_caller_file_info(entity_context, k8_file,
                                                                                      k8_file_path,
                                                                                      resource_id,
                                                                                      caller_resource_id,
                                                                                      root_folder)
            code_lines = entity_context.get("code_lines")
            file_line_range = self.line_range(code_lines)

            record = Record(
                check_id=check.id, bc_check_id=check.bc_id, check_name=check.name,
                check_result=check_result, code_block=code_lines,
                file_path=file_path, file_line_range=file_line_range,
                caller_file_path=caller_file_path, caller_file_line_range=caller_file_line_range,
                resource=kustomizeResourceID, evaluations=variable_evaluations,
                check_class=check.__class__.__module__, file_abs_path=absolute_file_path, severity=check.severity)
            record.set_guideline(check.guideline)
            report.add_record(record=record)

        return report

    def _get_caller_file_info(self, entity_context: _EntityContext, k8_file: str, k8_file_path: str, resource_id: str,
                              caller_resource_id: str, root_folder: str | None) -> tuple[tuple[int, int] | None, str | None]:
        origin_relative_path = entity_context.get('origin_relative_path')
        if origin_relative_path is None:
            return None, None
        k8s_file_dir = pathlib.Path(k8_file_path).parent
        raw_file_path = k8s_file_dir / origin_relative_path
        caller_file_path = self._get_caller_file_path(k8s_file_dir, origin_relative_path, raw_file_path)
        if root_folder is None:
            return None, caller_file_path
        caller_file_line_range = self._get_caller_line_range(root_folder, k8_file, origin_relative_path,
                                                             resource_id, caller_resource_id)
        return caller_file_line_range, caller_file_path

    @staticmethod
    def _get_caller_file_path(k8s_file_dir: pathlib.Path, origin_relative_path: str, raw_file_path: pathlib.Path)\
            -> str:
        """
        Creates the correct file path based on the collection of metadata locations we have.

        Example for expected input:
            - k8s_fil_dir - Path('/resources/image_referencer/overlays/prod')
            - origin_relative_path - '../../base/deployment.yaml'
            - raw_file_path - Path('/resources/image_referencer/overlays/prod/../../base/deployment.yaml')
        """
        amount_of_parents = str.count(origin_relative_path, '..')
        directory_prefix_path = k8s_file_dir
        if amount_of_parents == 0:
            # In case we don't have any relative paths, we need to remove the first directory parent
            # (as the first directory is the same one of the kustomization.yaml file)
            directory_prefix_path = k8s_file_dir.parent
        elif amount_of_parents and len(k8s_file_dir.parents) >= amount_of_parents:
            directory_prefix_path = k8s_file_dir.parents[amount_of_parents - 1]

        directory_prefix = str(directory_prefix_path)
        resolved_path = str(raw_file_path.resolve())
        # Make sure the resolved path starts with the root folder, as pathlib.Path.resolve() might change it
        if directory_prefix in resolved_path and not resolved_path.startswith(directory_prefix):
            resolved_path = K8sKustomizeRunner._remove_extra_path_parts(resolved_path, directory_prefix)

        return resolved_path[len(str(directory_prefix)):]

    @staticmethod
    def _remove_extra_path_parts(resolved_path: str, prefix: str) -> str:
        """
        Some pathlib paths can "add" extra arguments at the beginning after running `Path.resolve()`.
        For example, running `Path('/var/example.txt').resolve` might result in `/<not-existent-dir>/var/example.txt`.
        The purpose of this function is to remove any unintentional additions like this one.
        """
        resolved_path_parts = resolved_path.split(prefix)
        if len(resolved_path_parts) > 1:
            resolved_path = f'{prefix}{"".join(resolved_path_parts[1:])}'
        else:
            resolved_path = f'{prefix}{"".join(resolved_path_parts)}'
        return resolved_path

    def _get_caller_line_range(self, root_folder: str, k8_file: str, origin_relative_path: str,
                               resource_id: str, caller_resource_id: str) -> tuple[int, int] | None:
        raw_caller_directory = (pathlib.Path(k8_file.lstrip(os.path.sep)).parent /
                                pathlib.Path(origin_relative_path.lstrip(os.path.sep)).parent)
        caller_directory = str(pathlib.Path(f'{os.path.sep}{raw_caller_directory}').resolve())
        caller_directory = K8sKustomizeRunner._remove_extra_path_parts(caller_directory, root_folder)
        file_ending = pathlib.Path(origin_relative_path).suffix
        caller_file_path = f'{str(pathlib.Path(caller_directory) / caller_resource_id.replace(".", "-"))}{file_ending}'

        if caller_file_path not in self.definitions:
            return None

        caller_resource = None
        for resource in self.definitions[caller_file_path]:
            _resource_id = get_resource_id(resource)
            if _resource_id == resource_id:
                caller_resource = resource
                break

        if caller_resource is None:
            return None

        if caller_file_path not in self.definitions_raw:
            # As we cannot calculate better lines with the `calculate_code_lines` without the raw code,
            # we can use the existing info in the resource
            return caller_resource[START_LINE], caller_resource[END_LINE]

        raw_caller_resource = self.definitions_raw[caller_file_path]

        caller_raw_start_line = caller_resource[START_LINE]
        caller_raw_end_line = min(caller_resource[END_LINE], len(raw_caller_resource))

        _, caller_start_line, caller_end_line = calculate_code_lines(raw_caller_resource, caller_raw_start_line,
                                                                     caller_raw_end_line)
        return caller_start_line, caller_end_line

    def line_range(self, code_lines: list[tuple[int, str]]) -> list[int]:
        num_of_lines = len(code_lines)
        file_line_range = [0, 0]
        if num_of_lines > 0:
            first_line, code = code_lines[0]
            last_line, code = code_lines[num_of_lines - 1]
            file_line_range = [first_line, last_line]
        return file_line_range

    def mutate_kubernetes_graph_results(
        self, root_folder: str | None, runner_filter: RunnerFilter, report: Report, checks_results: dict[BaseGraphCheck, list[_CheckResult]]
    ) -> Report:
        # Moves report generation logic out of run() method in Runner class.
        # Allows function overriding of a much smaller function than run() for other "child" frameworks such as Kustomize, Helm
        # Where Kubernetes CHECKS are needed, but the specific file references are to another framework for the user output (or a mix of both).
        if not self.context:
            if self.context is None:
                # this shouldn't happen
                logging.error("Context for Kustomize runner was not set")
            return report

        kustomize_metadata = self.report_mutator_data['kustomizeMetadata'],
        kustomize_file_mappings = self.report_mutator_data['kustomizeFileMappings']

        for check, check_results in checks_results.items():
            for check_result in check_results:
                entity = check_result["entity"]
                entity_file_path: str = entity[CustomAttributes.FILE_PATH]
                entity_file_abs_path: str = _get_entity_abs_path(root_folder, entity_file_path)
                entity_id: str = entity[CustomAttributes.ID]
                entity_context = super().get_entity_context(entity=entity, entity_file_path=entity_file_path)

                if entity_file_abs_path in kustomize_file_mappings:
                    realKustomizeEnvMetadata = kustomize_metadata[0][kustomize_file_mappings[entity_file_abs_path]]
                    if 'overlay' in realKustomizeEnvMetadata["type"]:
                        kustomizeResourceID = f'{realKustomizeEnvMetadata["type"]}:{str(realKustomizeEnvMetadata["overlay_name"])}:{entity_id}'
                    else:
                        kustomizeResourceID = f'{realKustomizeEnvMetadata["type"]}:{entity_id}'
                else:
                    logging.warning(f"couldn't find {entity_file_abs_path} path in kustomizeFileMappings")
                    continue

                caller_file_path = None
                caller_file_line_range = None
                if self.checkov_allow_kustomize_file_edits:
                    caller_resource_id = entity_id
                    if PARENT_RESOURCE_ID_KEY_NAME in entity:
                        caller_resource_id = entity[PARENT_RESOURCE_ID_KEY_NAME]
                    caller_file_line_range, caller_file_path = self._get_caller_file_info(entity_context,
                                                                                          entity_file_path,
                                                                                          entity_file_path,
                                                                                          entity_id,
                                                                                          caller_resource_id,
                                                                                          root_folder)
                code_lines = entity_context["code_lines"]
                file_line_range = self.line_range(code_lines)

                clean_check_result = create_check_result(check_result=check_result, entity_context=entity_context, check_id=check.id)

                record = Record(
                    check_id=check.id,
                    check_name=check.name,
                    check_result=clean_check_result,
                    code_block=code_lines,
                    file_path=realKustomizeEnvMetadata['filePath'],
                    file_line_range=file_line_range,
                    caller_file_path=caller_file_path,
                    caller_file_line_range=caller_file_line_range,
                    resource=kustomizeResourceID,  # entity.get(CustomAttributes.ID),
                    evaluations={},
                    check_class=check.__class__.__module__,
                    file_abs_path=entity_file_abs_path,
                    severity=check.severity
                )
                record.set_guideline(check.guideline)
                report.add_record(record=record)

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

        manager = KustomizeImageReferencerManager(graph_connector=graph_connector, report_mutator_data=self.report_mutator_data)
        images = manager.extract_images_from_resources()

        return images


class Runner(BaseRunner[_KubernetesDefinitions, _KubernetesContext, "KubernetesGraphManager"]):
    kustomize_command = 'kustomize'  # noqa: CCE003  # a static attribute
    kubectl_command = 'kubectl'  # noqa: CCE003  # a static attribute
    check_type = CheckType.KUSTOMIZE  # noqa: CCE003  # a static attribute
    system_deps = True  # noqa: CCE003  # a static attribute
    kustomizeSupportedFileTypes = ('kustomization.yaml', 'kustomization.yml')  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__(file_names=Runner.kustomizeSupportedFileTypes)
        self.potentialBases: "list[str]" = []
        self.potentialOverlays: "list[str]" = []
        self.kustomizeProcessedFolderAndMeta: "dict[str, dict[str, str]]" = {}
        self.kustomizeFileMappings: "dict[str, str]" = {}
        self.templateRendererCommand: str | None = None
        self.target_folder_path = ''

        self.checkov_allow_kustomize_file_edits = convert_str_to_bool(os.getenv("CHECKOV_ALLOW_KUSTOMIZE_FILE_EDITS",
                                                                                False))

    def get_k8s_target_folder_path(self) -> str:
        return self.target_folder_path

    def get_kustomize_metadata(self) -> dict[str, dict[str, Any]]:
        return {'kustomizeMetadata': self.kustomizeProcessedFolderAndMeta,
                'kustomizeFileMappings': self.kustomizeFileMappings}

    def _parseKustomization(self, kustomize_dir: str) -> dict[str, Any]:
        # We may have multiple results for "kustomization.yaml" files. These could be:
        # - Base and Environment (overlay) DIR's for the same kustomize-powered deployment
        # - OR, Multiple different Kustomize-powered deployments
        # - OR, a mixture of the two.
        # We need parse some of the Kustomization.yaml files to work out which
        # This is so we can provide "Environment" information back to the user as part of the checked resource name/description.
        # TODO: We could also add a --kustomize-environment option so we only scan certain overlay names (prod, test etc) useful in CI.
        yaml_path = os.path.join(kustomize_dir, "kustomization.yaml")
        yml_path = os.path.join(kustomize_dir, "kustomization.yml")
        if os.path.isfile(yml_path):
            kustomization_path = yml_path
        elif os.path.isfile(yaml_path):
            kustomization_path = yaml_path
        else:
            return {}

        with open(kustomization_path, 'r') as kustomization_file:
            metadata: dict[str, Any] = {}
            try:
                file_content = yaml.safe_load(kustomization_file)
            except yaml.YAMLError:
                logging.info(f"Failed to load Kustomize metadata from {kustomization_path}.", exc_info=True)
                return {}

            if not isinstance(file_content, dict):
                return {}

            if 'resources' in file_content:
                resources = file_content['resources']

                # We can differentiate between "overlays" and "bases" based on if the `resources` refers to a directory,
                # which represents an "overlay", or only files which represents a "base"
                resources_representing_directories = [r for r in resources if pathlib.Path(r).suffix == '']
                if resources_representing_directories:
                    logging.debug(
                        f"Kustomization contains resources: section with directories. Likely an overlay/env."
                        f" {kustomization_path}")
                    metadata['type'] = "overlay"
                    metadata['referenced_bases'] = resources_representing_directories
                else:
                    logging.debug(f"Kustomization contains resources: section with only files (no dirs). Likley a base."
                                  f" {kustomization_path}")
                    metadata['type'] = "base"

            elif 'patchesStrategicMerge' in file_content:
                logging.debug(f"Kustomization contains patchesStrategicMerge: section. Likley an overlay/env. {kustomization_path}")
                metadata['type'] = "overlay"
                if 'bases' in file_content:
                    metadata['referenced_bases'] = file_content['bases']

            elif 'bases' in file_content:
                logging.debug(f"Kustomization contains bases: section. Likley an overlay/env. {kustomization_path}")
                metadata['type'] = "overlay"
                metadata['referenced_bases'] = file_content['bases']

            metadata['fileContent'] = file_content
            metadata['filePath'] = f"{kustomization_path}"
            if metadata.get('type') == "base":
                self.potentialBases.append(metadata['filePath'])

            if metadata.get('type') == "overlay":
                self.potentialOverlays.append(metadata['filePath'])

        return metadata

    def check_system_deps(self) -> str | None:
        # Ensure local system dependancies are available and of the correct version.
        # Returns framework names to skip if deps **fail** (ie, return None for a successful deps check).
        logging.info(f"Checking necessary system dependancies for {self.check_type} checks.")

        if shutil.which(self.kubectl_command) is not None:
            kubectl_version = get_kubectl_version(kubectl_command=self.kubectl_command)
            if kubectl_version and kubectl_version >= 1.14:
                logging.info(f"Found working version of {self.check_type} dependancy {self.kubectl_command}: {kubectl_version}")
                self.templateRendererCommand = self.kubectl_command
                return None
            else:
                return self.check_type
        elif shutil.which(self.kustomize_command) is not None:
            kustomize_version = get_kustomize_version(kustomize_command=self.kustomize_command)
            if kustomize_version:
                logging.info(
                    f"Found working version of {self.check_type} dependency {self.kustomize_command}: {kustomize_version}"
                )
                self.templateRendererCommand = self.kustomize_command
                return None
            else:
                return self.check_type
        else:
            logging.info(f"Could not find usable tools locally to process {self.check_type} checks. Framework will be disabled for this run.")
            return self.check_type

    def _handle_overlay_case(self, file_path: str,
                             kustomizeProcessedFolderAndMeta: dict[str, dict[str, Any]] | None = None) -> None:
        if kustomizeProcessedFolderAndMeta is None:
            kustomizeProcessedFolderAndMeta = self.kustomizeProcessedFolderAndMeta
        for parent in pathlib.Path(file_path).parents:
            for potentialBase in self.potentialBases:
                pathlib_base_object = pathlib.Path(potentialBase)
                potential_base_path = pathlib_base_object.parents[1]
                if parent == potential_base_path.resolve():
                    kustomizeProcessedFolderAndMeta[file_path]['calculated_bases'] = str(pathlib_base_object.parent)
        try:
            relativeToFullPath = f"{file_path}/{kustomizeProcessedFolderAndMeta[file_path]['referenced_bases'][0]}"
            if pathlib.Path(kustomizeProcessedFolderAndMeta[file_path]['calculated_bases']) == pathlib.Path(relativeToFullPath).resolve():
                kustomizeProcessedFolderAndMeta[file_path]['validated_base'] = str(pathlib.Path(kustomizeProcessedFolderAndMeta[file_path]['calculated_bases']))
                checkov_kustomize_env_name_by_path = str(pathlib.Path(file_path).relative_to(pathlib.Path(kustomizeProcessedFolderAndMeta[file_path]['calculated_bases']).parent))
                kustomizeProcessedFolderAndMeta[file_path]['overlay_name'] = checkov_kustomize_env_name_by_path
                logging.debug(f"Overlay based on {kustomizeProcessedFolderAndMeta[file_path]['validated_base']}, naming overlay {checkov_kustomize_env_name_by_path} for Checkov Results.")
            else:
                checkov_kustomize_env_name_by_path = pathlib.Path(file_path).stem
                kustomizeProcessedFolderAndMeta[file_path]['overlay_name'] = checkov_kustomize_env_name_by_path
                logging.debug(f"Could not confirm base dir for Kustomize overlay/env. Using {checkov_kustomize_env_name_by_path} for Checkov Results.")

        except KeyError:
            checkov_kustomize_env_name_by_path = pathlib.Path(file_path).stem
            kustomizeProcessedFolderAndMeta[file_path]['overlay_name'] = checkov_kustomize_env_name_by_path
            logging.debug(f"Could not confirm base dir for Kustomize overlay/env. Using {checkov_kustomize_env_name_by_path} for Checkov Results.")

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
                if cur_writer:
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

    def _get_kubectl_output(self, filePath: str, template_renderer_command: str, source_type: str | None) -> bytes | None:
        # Template out the Kustomizations to Kubernetes YAML
        if template_renderer_command == "kubectl":
            template_render_command_options = "kustomize"
        elif template_renderer_command == "kustomize":
            template_render_command_options = "build"
        else:
            logging.error(f"Template renderer command has an invalid value: {template_renderer_command}")
            return None

        add_origin_annotations_return_code = None

        if self.checkov_allow_kustomize_file_edits:
            add_origin_annotations_command = 'kustomize edit add buildmetadata originAnnotations'
            add_origin_annotations_return_code = subprocess.run(add_origin_annotations_command.split(' '),  # nosec
                                                                cwd=filePath).returncode

        full_command = f'{template_renderer_command} {template_render_command_options}'
        proc = subprocess.Popen(full_command.split(' '), cwd=filePath, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
        output, _ = proc.communicate()

        if self.checkov_allow_kustomize_file_edits and add_origin_annotations_return_code == 0:
            # If the return code is not 0, we didn't add the new buildmetadata field, so we shouldn't remove it
            remove_origin_annotaions = 'kustomize edit remove buildmetadata originAnnotations'
            subprocess.run(remove_origin_annotaions.split(' '), cwd=filePath)  # nosec

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
                base_path_parts = pathlib.Path(kustomize_processed_folder_and_meta[file_path]['calculated_bases']).parts
                most_significant_base_path = f"/{base_path_parts[-3]}/{base_path_parts[-2]}"
                env_or_base_path_prefix = f"{most_significant_base_path}/{kustomize_processed_folder_and_meta[file_path]['overlay_name']}"

        elif kustomize_processed_folder_and_meta[file_path].get('type') == "base":
            # Validated base last three parents as a path
            base_path_parts = pathlib.Path(kustomize_processed_folder_and_meta[file_path]['filePath']).parts
            most_significant_base_path = f"/{base_path_parts[-4]}/{base_path_parts[-3]}/{base_path_parts[-2]}"
            env_or_base_path_prefix = most_significant_base_path

        return env_or_base_path_prefix

    def get_binary_output_from_directory(
            self,
            file_path: str,
            template_renderer_command: str,
    ) -> tuple[bytes, str] | tuple[None, None]:
        kustomizeProcessedFolderAndMeta = {file_path: self._parseKustomization(file_path)}
        if kustomizeProcessedFolderAndMeta[file_path].get('type') == 'overlay':
            self._handle_overlay_case(file_path, kustomizeProcessedFolderAndMeta)
        return self.get_binary_output(file_path, kustomizeProcessedFolderAndMeta, template_renderer_command)

    def get_binary_output(
        self,
        file_path: str,
        kustomize_processed_folder_and_meta: dict[str, dict[str, Any]],
        template_renderer_command: str,
    ) -> tuple[bytes, str] | tuple[None, None]:
        source_type = kustomize_processed_folder_and_meta[file_path].get('type')
        logging.debug(f"Kustomization at {file_path} likley a {source_type}")
        try:
            output = self._get_kubectl_output(file_path, template_renderer_command, source_type)
            if output is None:
                return None, None

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

    def _run_kustomize_parser(
        self,
        file_path: str,
        shared_kustomize_file_mappings: dict[str, str],
        kustomize_processed_folder_and_meta: dict[str, dict[str, Any]],
        template_renderer_command: str,
        target_folder_path: str,
    ) -> None:
        output, _ = self.get_binary_output(file_path, kustomize_processed_folder_and_meta, template_renderer_command)
        if not output:
            return
        Runner._parse_output(output, file_path, kustomize_processed_folder_and_meta, target_folder_path, shared_kustomize_file_mappings)

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
        for file_path in self.kustomizeProcessedFolderAndMeta:
            if self.kustomizeProcessedFolderAndMeta[file_path].get('type') == 'overlay':
                self._handle_overlay_case(file_path)

        if platform.system() == 'Windows':
            if not self.templateRendererCommand:
                logging.error("The 'templateRendererCommand' was not set correctly")
                return

            shared_kustomize_file_mappings: dict[str, str] = {}
            for file_path in self.kustomizeProcessedFolderAndMeta:
                self._run_kustomize_parser(
                    file_path=file_path,
                    shared_kustomize_file_mappings=shared_kustomize_file_mappings,
                    kustomize_processed_folder_and_meta=self.kustomizeProcessedFolderAndMeta,
                    template_renderer_command=self.templateRendererCommand,
                    target_folder_path=self.target_folder_path,
                )
            self.kustomizeFileMappings = shared_kustomize_file_mappings
            return

        manager = multiprocessing.Manager()
        # make sure we have new dict
        shared_kustomize_file_mappings = pickle_deepcopy(manager.dict())  # type:ignore[arg-type]  # works with DictProxy
        shared_kustomize_file_mappings.clear()

        jobs = []
        for filePath in self.kustomizeProcessedFolderAndMeta:
            p = multiprocessing.Process(
                target=self._run_kustomize_parser,
                args=(
                    filePath,
                    shared_kustomize_file_mappings,
                    self.kustomizeProcessedFolderAndMeta,
                    self.templateRendererCommand,
                    self.target_folder_path
                )
            )
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()

        self.kustomizeFileMappings = dict(shared_kustomize_file_mappings)

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
        report: "Report | list[Report]" = Report(self.check_type)

        if not self.kustomizeProcessedFolderAndMeta:
            # nothing to process
            return report

        target_dir = ""
        try:
            k8s_runner = K8sKustomizeRunner()
            # k8s_runner.run() will kick off both CKV_ and CKV2_ checks and return a merged results object.
            target_dir = self.get_k8s_target_folder_path()
            k8s_runner.report_mutator_data = self.get_kustomize_metadata()
            if root_folder:
                k8s_runner.original_root_dir = root_folder

            # the returned report can be a list of reports, which also includes an SCA image report
            report = k8s_runner.run(target_dir, external_checks_dir=external_checks_dir, runner_filter=runner_filter)
            self.graph_manager = k8s_runner.graph_manager
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
