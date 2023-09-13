import os
import warnings
from pathlib import Path
from typing import List
from parameterized import parameterized_class

from tests.graph_utils.utils import set_db_connector_by_graph_framework, PARAMETERIZED_GRAPH_FRAMEWORKS
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.bridgecrew.check_type import CheckType
from checkov.dockerfile.graph_manager import DockerfileGraphManager
from tests.common.graph.checks.test_yaml_policies_base import TestYamlPoliciesBase


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestYamlPolicies(TestYamlPoliciesBase):
    def __init__(self, args):
        db_connector = set_db_connector_by_graph_framework(self.graph_framework)

        graph_manager = DockerfileGraphManager(db_connector=db_connector)
        super().__init__(
            graph_manager=graph_manager,
            real_graph_checks_path=str(
                Path(__file__).parent.parent.parent.parent.parent / "checkov/dockerfile/checks/graph_checks"
            ),
            test_checks_path="",
            check_type=CheckType.GITHUB_ACTIONS,
            test_file_path=__file__,
            args=args,
        )

    def setUp(self) -> None:
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    def test_RunUsingSudo(self):
        self.go("RunUsingSudo")
    
    def test_RunUnsafeCurl(self):
        self.go("RunUnsafeCurl")

    def test_RunUnsafeWget(self):
        self.go("RunUnsafeWget")

    def test_RunPipTrustedHost(self):
        self.go("RunPipTrustedHost")

    def test_EnvPythonHttpsVerify(self):
        self.go("EnvPythonHttpsVerify")

    def test_EnvNodeTlsRejectUnauthorized(self):
        self.go("EnvNodeTlsRejectUnauthorized")

    def test_RunApkAllowUntrusted(self):
        self.go("RunApkAllowUntrusted")

    def test_RunAptGetAllowUnauthenticated(self):
        self.go("RunAptGetAllowUnauthenticated")
    
    def test_RunYumNoGpgCheck(self):
        self.go("RunYumNoGpgCheck")

    def test_RunRpmNoSignature(self):
        self.go("RunRpmNoSignature")

    def test_RunAptGetForceYes(self):
        self.go("RunAptGetForceYes")

    def test_EnvNpmConfigStrictSsl(self):
        self.go("EnvNpmConfigStrictSsl")

    def test_RunNpmConfigSetStrictSsl(self):
        self.go("RunNpmConfigSetStrictSsl")

    def test_EnvGitSslNoVerify(self):
        self.go("EnvGitSslNoVerify")

    def test_RunYumConfigManagerSslVerify(self):
        self.go("RunYumConfigManagerSslVerify")

    def test_EnvPipTrustedHost(self):
        self.go("EnvPipTrustedHost")

    def test_RunChpasswd(self):
        self.go("RunChpasswd")

    def test_registry_load(self):
        registry = self.get_checks_registry()
        self.assertGreater(len(registry.checks), 0)

    def assert_evaluated_keys(self, expected_evaluated_keys: List[str], results: List[Record]):
        evaluated_keys_results = results[0].check_result["evaluated_keys"]
        self.assertCountEqual(expected_evaluated_keys, evaluated_keys_results)

    def create_report_from_graph_checks_results(self, checks_results, check):
        report = Report(CheckType.GITHUB_ACTIONS)
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
                resource=entity.get(CustomAttributes.RESOURCE_TYPE),
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

    def assert_entities(self, expected_entities: List[str], results: List[Record], assertion: bool):
        self.assertEqual(
            len(expected_entities),
            len(results),
            f"mismatch in number of results in {'passed' if assertion else 'failed'}, "
            f"expected: {len(expected_entities)}, got: {len(results)}",
        )
        for expected_entity in expected_entities:
            found = False
            for check_result in results:
                entity_id = f"{check_result.file_path.lstrip('/')}.{check_result.resource}"
                if entity_id == expected_entity:
                    found = True
                    break
            self.assertTrue(found, f"expected to find entity {expected_entity}, {'passed' if assertion else 'failed'}")
