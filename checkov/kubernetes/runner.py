import logging
import operator
import os
from functools import reduce
from typing import Type, Optional, List

from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.checks_infra.registry import BaseRegistry
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.common.graph.graph_manager import GraphManager
from checkov.common.output.record import Record
from checkov.common.output.report import Report, merge_reports, CheckType
from checkov.common.runners.base_runner import BaseRunner, CHECKOV_CREATE_GRAPH
from checkov.kubernetes.checks.resource.registry import registry
from checkov.kubernetes.graph_builder.local_graph import KubernetesLocalGraph
from checkov.kubernetes.graph_manager import KubernetesGraphManager
from checkov.kubernetes.kubernetes_utils import create_definitions, build_definitions_context, get_skipped_checks, get_resource_id
from checkov.runner_filter import RunnerFilter


class Runner(BaseRunner):
    def __init__(
        self,
        graph_class: Type[LocalGraph] = KubernetesLocalGraph,
        db_connector: NetworkxConnector = NetworkxConnector(),
        source: str = "Kubernetes",
        graph_manager: Optional[GraphManager] = None,
        external_registries: Optional[List[BaseRegistry]] = None
    ) -> None:
        super().__init__(file_extensions=['.yml', '.yaml'])
        self.external_registries = [] if external_registries is None else external_registries
        self.check_type = CheckType.KUBERNETES
        self.graph_class = graph_class
        self.graph_manager = \
            graph_manager if graph_manager else KubernetesGraphManager(source=source, db_connector=db_connector)

        self.graph_registry = get_graph_checks_registry(self.check_type)
        self.definitions_raw = {}
        self.report_mutator_data = None

    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter(), collect_skip_comments=True, helmChart=None):
        report = Report(self.check_type)
        if self.context is None or self.definitions is None:
            if files or root_folder:
                self.definitions, self.definitions_raw = create_definitions(root_folder, files, runner_filter)
            else:
                return report
            if external_checks_dir:
                for directory in external_checks_dir:
                    registry.load_external_checks(directory)

                    if CHECKOV_CREATE_GRAPH:
                        self.graph_registry.load_external_checks(directory)

            self.context = build_definitions_context(self.definitions, self.definitions_raw)

            if CHECKOV_CREATE_GRAPH:
                logging.info("creating Kubernetes graph")
                local_graph = self.graph_manager.build_graph_from_definitions(self.definitions)
                logging.info("Successfully created Kubernetes graph")

                for vertex in local_graph.vertices:
                    file_abs_path = _get_entity_abs_path(root_folder, vertex.path)
                    report.add_resource(f'{file_abs_path}:{vertex.id}')
                self.graph_manager.save_graph(local_graph)
                self.definitions = local_graph.definitions

        report = self.check_definitions(root_folder, runner_filter, report, collect_skip_comments=collect_skip_comments, helmChart=helmChart)

        if CHECKOV_CREATE_GRAPH:
            graph_report = self.get_graph_checks_report(root_folder, runner_filter, helmChart=helmChart)
            merge_reports(report, graph_report)

        return report

    def check_definitions(self, root_folder, runner_filter, report, collect_skip_comments=True, helmChart=None,):
        for k8_file in self.definitions.keys():
            # There are a few cases here. If -f was used, there could be a leading / because it's an absolute path,
            # or there will be no leading slash; root_folder will always be none.
            # If -d is used, root_folder will be the value given, and -f will start with a / (hardcoded above).
            # The goal here is simply to get a valid path to the file (which sls_file does not always give).
            file_abs_path = _get_entity_abs_path(root_folder, k8_file)
            k8_file_path = f"/{os.path.relpath(file_abs_path, root_folder)}"
            # Run for each definition
            for entity_conf in self.definitions[k8_file]:
                entity_type = entity_conf.get("kind")

                # Skip Kustomization Templates. 
                # Should be handled by Kusomize framework handler when it finds kustomization.yaml files.
                # TODO: FUTURE: Potentially call the framework if we find items here that aren't in a file called kustomization.yaml - validate this edge case.
                if entity_type == "Kustomization":
                    continue

                skipped_checks = get_skipped_checks(entity_conf)
                results = registry.scan(k8_file, entity_conf, skipped_checks, runner_filter)

                # TODO? - Variable Eval Message!
                variable_evaluations = {}

                report = self.mutateKubernetesResults(results, report, k8_file, k8_file_path, file_abs_path, entity_conf, variable_evaluations)

        return report

    def get_graph_checks_report(self, root_folder: str, runner_filter: RunnerFilter, helmChart) -> Report:
        report = Report(self.check_type)
        checks_results = self.run_graph_checks_results(runner_filter)
        report = self.mutateKubernetesGraphResults(root_folder, runner_filter, report, checks_results)
        return report

    def mutateKubernetesResults(self, results, report, k8_file=None, k8_file_path=None, file_abs_path=None, entity_conf=None, variable_evaluations=None):
        # Moves report generation logic out of run() method in Runner class.
        # Allows function overriding of a much smaller function than run() for other "child" frameworks such as Kustomize, Helm
        # Where Kubernetes CHECKS are needed, but the specific file references are to another framework for the user output (or a mix of both).
        for check, check_result in results.items():
            resource_id = get_resource_id(entity_conf)
            entity_context = self.context[k8_file][resource_id]

            record = Record(
                check_id=check.id, bc_check_id=check.bc_id, check_name=check.name,
                check_result=check_result, code_block=entity_context.get("code_lines"), file_path=k8_file_path,
                file_line_range=[entity_context.get("start_line"), entity_context.get("end_line")],
                resource=resource_id, evaluations=variable_evaluations,
                check_class=check.__class__.__module__, file_abs_path=file_abs_path, severity=check.severity)
            record.set_guideline(check.guideline)
            report.add_record(record=record)
        
        return report

    def mutateKubernetesGraphResults(self, root_folder: str, runner_filter: RunnerFilter, report: Report, checks_results) -> Report:
        # Moves report generation logic out of run() method in Runner class.
        # Allows function overriding of a much smaller function than run() for other "child" frameworks such as Kustomize, Helm
        # Where Kubernetes CHECKS are needed, but the specific file references are to another framework for the user output (or a mix of both).
        for check, check_results in checks_results.items():
            for check_result in check_results:
                entity = check_result["entity"]
                entity_file_path = entity.get(CustomAttributes.FILE_PATH)
                entity_file_abs_path = _get_entity_abs_path(root_folder, entity_file_path)
                entity_id = entity.get(CustomAttributes.ID)
                entity_context = self.context[entity_file_path][entity_id]

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
                    file_abs_path=entity_file_abs_path,
                    severity=check.severity
                )
                record.set_guideline(check.guideline)
                report.add_record(record=record)
        return report


def _get_entity_abs_path(root_folder, entity_file_path):
    if entity_file_path[0] == '/' and (root_folder and not entity_file_path.startswith(root_folder)):
        path_to_convert = (root_folder + entity_file_path) if root_folder else entity_file_path
    else:
        path_to_convert = (os.path.join(root_folder, entity_file_path)) if root_folder else entity_file_path
    return os.path.abspath(path_to_convert)


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
