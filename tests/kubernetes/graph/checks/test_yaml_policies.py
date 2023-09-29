import copy
import os
import os.path

from parameterized import parameterized_class

from tests.graph_utils.utils import set_db_connector_by_graph_framework, PARAMETERIZED_GRAPH_FRAMEWORKS
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.kubernetes.graph_manager import KubernetesGraphManager
from tests.common.graph.checks.test_yaml_policies_base import TestYamlPoliciesBase


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestYamlPolicies(TestYamlPoliciesBase):
    def tearDown(self) -> None:
        self.get_checks_registry().checks = []

    def __init__(self, args):
        db_connector = set_db_connector_by_graph_framework(self.graph_framework)
        graph_manager = KubernetesGraphManager(db_connector=db_connector)
        real_graph_checks_relative_path = "checkov/kubernetes/checks/graph_checks"
        real_graph_checks_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                                              real_graph_checks_relative_path)
        super().__init__(graph_manager, real_graph_checks_path,
                         os.path.dirname(__file__) + "/test_checks", 'kubernetes', __file__, args)

    def test_AllowedCapabilities(self):
        self.go('AllowedCapabilities')

    def test_AllowPrivilegeEscalation(self):
        self.go('AllowPrivilegeEscalation')

    def test_RoleBindingPE(self) -> None:
        self.go('RoleBindingPE')

    def test_NoCreateNodesProxyOrPodsExec(self) -> None:
        self.go('NoCreateNodesProxyOrPodsExec')
    
    def test_ImpersonatePermissions(self) -> None:
        self.go("ImpersonatePermissions")

    def test_ModifyServicesStatus(self) -> None:
        self.go('ModifyServicesStatus')

    def test_ReadAllSecrets(self) -> None:
        self.go('ReadAllSecrets')

    def test_PodIsPubliclyAccessibleExample(self) -> None:
        self.go('PodIsPubliclyAccessibleExample')

    def test_RequireAllPodsToHaveNetworkPolicy(self) -> None:
        self.go('RequireAllPodsToHaveNetworkPolicy')

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
