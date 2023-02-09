import copy
import os.path

from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.kubernetes.graph_manager import KubernetesGraphManager
from tests.common.graph.checks.test_yaml_policies_base import TestYamlPoliciesBase


class TestYamlPolicies(TestYamlPoliciesBase):
    def tearDown(self) -> None:
        self.get_checks_registry().checks = []

    def __init__(self, args):
        graph_manager = KubernetesGraphManager(db_connector=NetworkxConnector())
        super().__init__(graph_manager, "checkov/kubernetes/checks/graph_checks",
                         os.path.dirname(__file__) + "/test_checks", 'kubernetes', __file__, args)

    def test_AllowedCapabilities(self):
        self.go('AllowedCapabilities')

    def test_AllowPrivilegeEscalation(self):
        self.go('AllowPrivilegeEscalation')

    def create_report_from_graph_checks_results(self, checks_results, check):
        report = Report("kubernetes")
        first_results_key = list(checks_results.keys())[0]
        for check_result in checks_results[first_results_key]:
            entity = check_result["entity"]
            record = Record(check_id=check['id'],
                            check_name=check['name'],
                            check_result=copy.deepcopy(check_result),
                            code_block="",
                            file_path=entity.get(CustomAttributes.FILE_PATH),
                            file_line_range=[entity.get('__startline__'), entity.get('__endline__')],
                            resource=entity.get(CustomAttributes.BLOCK_NAME),
                            evaluations={},
                            check_class=check.__class__.__module__,
                            file_abs_path=entity.get(CustomAttributes.FILE_PATH))
            if check_result["result"] == CheckResult.PASSED:
                report.passed_checks.append(record)
            if check_result["result"] == CheckResult.FAILED:
                report.failed_checks.append(record)
        return report

    def assert_evaluated_keys(self, checks_results, check):
        pass
