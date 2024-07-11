import warnings
from pathlib import Path
from typing import List

from checkov.arm.graph_manager import ArmGraphManager
from parameterized import parameterized_class
from tests.graph_utils.utils import set_db_connector_by_graph_framework, PARAMETERIZED_GRAPH_FRAMEWORKS

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.bridgecrew.check_type import CheckType
from tests.common.graph.checks.test_yaml_policies_base import TestYamlPoliciesBase


@parameterized_class(
    PARAMETERIZED_GRAPH_FRAMEWORKS
)
class TestYamlPolicies(TestYamlPoliciesBase):
    def __init__(self, args):
        db_connector = set_db_connector_by_graph_framework(self.graph_framework)

        graph_manager = ArmGraphManager(db_connector=db_connector)
        super().__init__(
            graph_manager=graph_manager,
            real_graph_checks_path=str(
                Path(__file__).parent.parent.parent.parent.parent / "checkov/arm/checks/graph_checks"
            ),
            test_checks_path="",
            check_type="bicep",
            test_file_path=__file__,
            args=args,
        )

    def setUp(self) -> None:
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    def test_AzureSpringCloudConfigWithVnet(self):
        self.go("AzureSpringCloudConfigWithVnet")

    def test_AzureMLWorkspacePublicNetwork(self):
        self.go("AzureMLWorkspacePublicNetwork")

    def test_SynapseLogMonitoringEnabledForSQLPool(self):
        self.go("SynapseLogMonitoringEnabledForSQLPool")

    def test_SynapseSQLPoolHasSecurityAlertPolicy(self):
        self.go("SynapseSQLPoolHasSecurityAlertPolicy")

    def test_SynapseSQLPoolHasVulnerabilityAssessment(self):
        self.go("SynapseSQLPoolHasVulnerabilityAssessment")
    
    def test_SynapseWorkspaceHasExtendedAuditLogs(self):
        self.go("SynapseWorkspaceHasExtendedAuditLogs")

    def test_registry_load(self):
        registry = self.get_checks_registry()
        self.assertGreater(len(registry.checks), 0)

    def assert_evaluated_keys(self, expected_evaluated_keys: List[str], results: List[Record]):
        evaluated_keys_results = results[0].check_result["evaluated_keys"]
        self.assertCountEqual(expected_evaluated_keys, evaluated_keys_results)

    def create_report_from_graph_checks_results(self, checks_results, check):
        report = Report(CheckType.ARM)
        first_results_key = list(checks_results.keys())[0]
        for check_result in checks_results[first_results_key]:
            entity = check_result["entity"]
            record = Record(
                check_id=check["id"],
                check_name=check["name"],
                check_result=check_result,
                code_block=[(0, "")],
                file_path=entity.get(CustomAttributes.FILE_PATH),
                file_line_range=[entity.get("__startline__"), entity.get("__endline__")],
                resource=f"{entity.get(CustomAttributes.RESOURCE_TYPE)}.{entity.get(CustomAttributes.BLOCK_NAME)}",
                entity_tags=entity.get("tags", {}),
                evaluations=None,
                check_class="",
                file_abs_path=entity.get(CustomAttributes.FILE_PATH),
            )
            if check_result["result"] == CheckResult.PASSED:
                report.passed_checks.append(record)
            if check_result["result"] == CheckResult.FAILED:
                report.failed_checks.append(record)
        return report
