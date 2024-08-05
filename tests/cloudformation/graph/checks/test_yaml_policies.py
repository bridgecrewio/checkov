import copy
import os
import warnings
from typing import List

from parameterized import parameterized_class

from checkov.cloudformation.graph_manager import CloudformationGraphManager
from tests.graph_utils.utils import set_db_connector_by_graph_framework, PARAMETERIZED_GRAPH_FRAMEWORKS
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from tests.common.graph.checks.test_yaml_policies_base import TestYamlPoliciesBase


file_dir = os.path.dirname(__file__)


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestYamlPolicies(TestYamlPoliciesBase):
    def __init__(self, args):
        db_connector = set_db_connector_by_graph_framework(self.graph_framework)
        graph_manager = CloudformationGraphManager(db_connector=db_connector)
        super().__init__(graph_manager,
                         os.path.abspath(os.path.join(file_dir, "../../../../checkov/cloudformation/checks/graph_checks")),
                         os.path.join(file_dir, "test_checks"), "cloudformation", __file__, args)

    def setUp(self) -> None:
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    def test_SagemakerNotebookEncryption(self):
        self.go("SagemakerNotebookEncryption")

    def test_MSKClusterLogging(self):
        self.go("MSKClusterLogging")

    def test_LambdaFunction(self):
        self.go("LambdaFunction")

    def test_SageMakerIAMPolicyOverlyPermissiveToAllTraffic(self):
        self.go("SageMakerIAMPolicyOverlyPermissiveToAllTraffic")

    def test_ALBRedirectHTTPtoHTTPS(self):
        self.go("ALBRedirectHTTPtoHTTPS")

    def test_AppSyncProtectedByWAF(self):
        self.go("AppSyncProtectedByWAF")

    def test_RDSEncryptionInTransit(self):
        self.go("RDSEncryptionInTransit")

    def test_registry_load(self):
        registry = self.get_checks_registry()
        self.assertGreater(len(registry.checks), 0)

    def assert_evaluated_keys(self, expected_evaluated_keys: List[str], results: List[Record]):
        evaluated_keys_results = results[0].check_result["evaluated_keys"]
        self.assertCountEqual(expected_evaluated_keys, evaluated_keys_results)

    def create_report_from_graph_checks_results(self, checks_results, check):
        report = Report("cloudformation")
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
                            entity_tags=entity.get('tags', {}),
                            evaluations=None,
                            check_class=None,
                            file_abs_path=entity.get(CustomAttributes.FILE_PATH))
            if check_result["result"] == CheckResult.PASSED:
                report.passed_checks.append(record)
            if check_result["result"] == CheckResult.FAILED:
                report.failed_checks.append(record)
        return report


def wrap_policy(policy):
    policy['query'] = policy['definition']
    del policy['definition']
