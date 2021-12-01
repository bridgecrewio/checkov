import logging
import operator
import os
from functools import reduce

from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.util.data_structures_utils import search_deep_keys
from checkov.common.util.type_forcers import force_list
from checkov.common.output.record import Record
from checkov.common.output.report import Report, merge_reports
from checkov.common.runners.base_runner import BaseRunner
from checkov.kubernetes.graph_builder.local_graph import KubernetesLocalGraph
from checkov.kubernetes.graph_manager import KubernetesGraphManager
from checkov.kubernetes.kubernetes_utils import get_files_definitions, get_folder_definitions, \
    build_definitions_context, get_skipped_checks
from checkov.kubernetes.checks.resource.registry import registry
from checkov.runner_filter import RunnerFilter


class Runner(BaseRunner):
    def __init__(
        self,
        graph_class=KubernetesLocalGraph,
        db_connector=NetworkxConnector(),
        source="Kubernetes",
        graph_manager=None,
    ):
        self.check_type = "kubernetes"
        self.graph_class = graph_class
        self.graph_manager = \
            graph_manager if graph_manager else KubernetesGraphManager(source=source, db_connector=db_connector)

        self.graph_registry = get_graph_checks_registry(self.check_type)
        self.definitions_raw = {}

    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter(), collect_skip_comments=True, helmChart=None):
        report = Report(self.check_type)
        if self.context is None or self.definitions is None:
            if files:
                self.definitions, self.definitions_raw = get_files_definitions(files)
            elif root_folder:
                self.definitions, self.definitions_raw = get_folder_definitions(root_folder, runner_filter.excluded_paths)
            else:
                return report
            if external_checks_dir:
                for directory in external_checks_dir:
                    registry.load_external_checks(directory)
                    self.graph_registry.load_external_checks(directory)
            self.context = build_definitions_context(self.definitions, self.definitions_raw)

            logging.info("creating kubernetes graph")
            local_graph = self.graph_manager.build_graph_from_definitions(self.definitions)
            for vertex in local_graph.vertices:
                report.add_resource(f'{vertex.path}:{vertex.id}')
            self.graph_manager.save_graph(local_graph)
            self.definitions = local_graph.definitions

        report = self.check_definitions(root_folder, runner_filter, report)
        graph_report = self.get_graph_checks_report(root_folder, runner_filter)
        merge_reports(report, graph_report)

        return report

    def check_definitions(self, root_folder, runner_filter, report):
        for k8_file in self.definitions.keys():
            # There are a few cases here. If -f was used, there could be a leading / because it's an absolute path,
            # or there will be no leading slash; root_folder will always be none.
            # If -d is used, root_folder will be the value given, and -f will start with a / (hardcoded above).
            # The goal here is simply to get a valid path to the file (which sls_file does not always give).
            if k8_file[0] == '/':
                path_to_convert = (root_folder + k8_file) if root_folder else k8_file
            else:
                path_to_convert = (os.path.join(root_folder, k8_file)) if root_folder else k8_file

            file_abs_path = os.path.abspath(path_to_convert)

            if self.definitions[k8_file]:
                for entity_conf in self.definitions[k8_file]:
                    if _is_invalid_k8_definition(entity_conf):
                        continue
                    logging.debug("Template Dump for {}: {}".format(k8_file, entity_conf, indent=2))

                    if not isinstance(entity_conf, dict) or entity_conf.get("kind") == "List":
                        continue

                    metadata = entity_conf.get("metadata", {})

                    # Skip entity without metadata["name"]
                    # Skip entity with parent (metadata["ownerReferences"]) in runtime
                    # We will alert in runtime only
                    if not metadata or isinstance(metadata, int) or "name" not in metadata or \
                            metadata.get("ownerReferences"):
                        continue

                    # Append containers and initContainers to definitions list
                    for type in ["containers", "initContainers"]:
                        if entity_conf["kind"] == "CustomResourceDefinition":
                            continue
                        containers = search_deep_keys(type, entity_conf, [])
                        if not containers:
                            continue
                        containers = containers.pop()
                        namespace = metadata.get("namespace", "default")
                        container_def = containers.pop()
                        if not container_def:
                            continue

                        container_def = force_list(container_def)
                        for i, cd in enumerate(container_def):
                            cd["apiVersion"] = entity_conf["apiVersion"]
                            cd["kind"] = type
                            cd["parent"] = "{}.{}.{} (container {})".format(
                                entity_conf["kind"], entity_conf["metadata"]["name"], namespace, str(i))
                            cd["parent_metadata"] = entity_conf["metadata"]
                        self.definitions[k8_file].extend(container_def)

                # Run for each definition included added container definitions
                for i, entity_conf in enumerate(self.definitions[k8_file]):
                    if _is_invalid_k8_definition(entity_conf):
                        continue
                    logging.debug("Template Dump for {}: {}".format(k8_file, entity_conf, indent=2))

                    if not entity_conf or not isinstance(entity_conf, dict):
                        continue
                    entity_type = entity_conf.get("kind")
                    # Skip List and Kustomization Templates (for now)
                    if not entity_type or isinstance(entity_type, int) or entity_type in ["List", "Kustomization"]:
                        continue

                    metadata = entity_conf.get("metadata")
                    # Skip entity without metadata["name"] or parent_metadata["name"]
                    if entity_type not in ["containers", "initContainers"]:
                        if not metadata or isinstance(metadata, int) or "name" not in metadata:
                            continue

                    # Skip entity with parent (metadata["ownerReferences"]) in runtime
                    # We will alert in runtime only
                    if metadata and metadata.get("ownerReferences"):
                        continue

                    skipped_checks = get_skipped_checks(entity_conf)
                    results = registry.scan(k8_file, entity_conf, skipped_checks, runner_filter)

                    start_line = entity_conf["__startline__"]
                    end_line = entity_conf["__endline__"]

                    if start_line == end_line:
                        entity_lines_range = [start_line, end_line]
                        entity_code_lines = self.definitions_raw[k8_file][start_line - 1: end_line]
                    else:
                        entity_lines_range = [start_line, end_line - 1]
                        entity_code_lines = self.definitions_raw[k8_file][start_line - 1: end_line - 1]

                    # TODO? - Variable Eval Message!
                    variable_evaluations = {}

                    for check, check_result in results.items():
                        resource_id = check.get_resource_id(entity_conf)
                        report.add_resource(f'{k8_file}:{resource_id}')
                        record = Record(check_id=check.id, bc_check_id=check.bc_id,
                                        check_name=check.name, check_result=check_result,
                                        code_block=entity_code_lines, file_path=k8_file,
                                        file_line_range=entity_lines_range,
                                        resource=resource_id, evaluations=variable_evaluations,
                                        check_class=check.__class__.__module__, file_abs_path=file_abs_path)
                        record.set_guideline(check.guideline)
                        report.add_record(record=record)

        return report

    def get_graph_checks_report(self, root_folder: str, runner_filter: RunnerFilter) -> Report:
        report = Report(self.check_type)
        checks_results = self.run_graph_checks_results(runner_filter)

        for check, check_results in checks_results.items():
            for check_result in check_results:
                entity = check_result["entity"]
                entity_file_abs_path = entity.get(CustomAttributes.FILE_PATH)
                entity_file_path = f"/{os.path.relpath(entity_file_abs_path, root_folder)}"
                entity_id = entity.get(CustomAttributes.ID)
                entity_context = self.context[entity_file_abs_path][entity_id]

                record = Record(
                    check_id=check.id,
                    check_name=check.name,
                    check_result=check_result,
                    code_block=entity_context.get("code_lines"),
                    file_path=entity_file_path,
                    file_line_range=[entity_context.get("start_line"), entity_context.get("end_line")],
                    resource=entity.get(CustomAttributes.ID),
                    evaluations={},
                    check_class=check.__class__.__module__,
                    file_abs_path=entity_file_abs_path
                )
                record.set_guideline(check.guideline)
                report.add_record(record=record)
        return report


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


def _is_invalid_k8_definition(definition: dict) -> bool:
    return isinstance(definition, dict) and 'apiVersion' not in definition.keys() and 'kind' not in \
           definition.keys()
