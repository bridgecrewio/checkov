import unittest
from typing import Optional

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severity, Severities, BcSeverities
from checkov.kubernetes.checks.resource.base_registry import Registry
from checkov.runner_filter import RunnerFilter


class TestCheck:
    def __init__(self, id: str, bc_id: Optional[str] = None, severity: Optional[Severity] = None):
        self.id = id
        self.bc_id = bc_id
        self.severity = severity


class TestRunnerFilter(unittest.TestCase):

    def test_run_by_id_default(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=[], skip_checks=[])
        check = TestCheck('CKV_1')
        self.assertTrue(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_id_specific_enable(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=["CKV_1"], skip_checks=[])
        check = TestCheck('CKV_1')
        self.assertTrue(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_severity(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=["LOW"], skip_checks=[])
        check = TestCheck('CKV_1', severity=Severities[BcSeverities.LOW])
        self.assertTrue(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_severity_omitted(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=["HIGH"], skip_checks=[])
        check = TestCheck('CKV_1', severity=Severities[BcSeverities.LOW])
        self.assertFalse(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_severity_implicit(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=["LOW"], skip_checks=[])
        check = TestCheck('CKV_1', severity=Severities[BcSeverities.HIGH])
        self.assertTrue(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_skip_severity(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=[], skip_checks=["LOW"])
        check = TestCheck('CKV_1', severity=Severities[BcSeverities.LOW])
        self.assertFalse(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_skip_severity_implicit(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=[], skip_checks=["HIGH"])
        check = TestCheck('CKV_1', severity=Severities[BcSeverities.LOW])
        self.assertFalse(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_skip_severity_omitted(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=[], skip_checks=["LOW"])
        check = TestCheck('CKV_1', severity=Severities[BcSeverities.HIGH])
        self.assertTrue(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_id_specific_enable_bc_id(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=["BC_CKV_1"], skip_checks=[])
        check = TestCheck('CKV_1', 'BC_CKV_1')
        self.assertTrue(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_id_omitted_specific_enable(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=["CKV_1"], skip_checks=[])
        check = TestCheck('CKV_999')
        self.assertFalse(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_id_omitted_specific_enablebc_id(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=["BC_CKV_1"], skip_checks=[])
        check = TestCheck('CKV_999', 'BC_CKV_999')
        self.assertFalse(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_id_specific_disable(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=[], skip_checks=["CKV_1"])
        check = TestCheck('CKV_1')
        self.assertFalse(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_id_specific_disable_bc_id(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=[], skip_checks=["BC_CKV_1"])
        check = TestCheck('CKV_1', 'BC_CKV_1')
        self.assertFalse(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_id_omitted_specific_disable(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=[], skip_checks=["CKV_1"])
        check = TestCheck('CKV_999')
        self.assertTrue(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_id_omitted_specific_disable_bc_id(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=[], skip_checks=["BC_CKV_1"])
        check = TestCheck('CKV_999', 'BC_CKV_999')
        self.assertTrue(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_id_external(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=[], skip_checks=["CKV_1"])
        run_filter.notify_external_check("CKV_EXT_999")
        check = TestCheck('CKV_EXT_999')
        self.assertTrue(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_id_external2(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=["CKV_1"], skip_checks=["CKV_2"])
        run_filter.notify_external_check("CKV_EXT_999")
        check = TestCheck('CKV_EXT_999')
        self.assertFalse(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_id_external3(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=["CKV_EXT_999"], skip_checks=[])
        run_filter.notify_external_check("CKV_EXT_999")
        check = TestCheck('CKV_EXT_999')
        self.assertTrue(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_id_external4(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=["CKV_1"], skip_checks=["CKV_2"], all_external=True)
        run_filter.notify_external_check("CKV_EXT_999")
        check = TestCheck('CKV_EXT_999')
        self.assertTrue(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_id_external_disabled(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=[], skip_checks=["CKV_1", "CKV_EXT_999"])
        run_filter.notify_external_check("CKV_EXT_999")
        check = TestCheck('CKV_EXT_999')
        self.assertFalse(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_id_external_custom(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=["K8S_EXT_999"], skip_checks=[])
        run_filter.notify_external_check("K8S_EXT_999")
        check = TestCheck('K8S_EXT_999')
        self.assertTrue(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    def test_run_by_id_external_custom_disabled(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=[], skip_checks=["K8S_EXT_999"])
        run_filter.notify_external_check("K8S_EXT_999")
        check = TestCheck('K8S_EXT_999')
        self.assertFalse(instance._should_run_scan(check, {}, run_filter, CheckType.KUBERNETES))

    # Namespace filtering

    def test_namespace_allow_default(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=["default"], skip_checks=[])
        config = {"metadata": {"namespace": "not_matched"}}
        check = TestCheck('CKV_1')
        self.assertFalse(instance._should_run_scan(check, config, run_filter, CheckType.KUBERNETES))

    def test_namespace_deny_default(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=[], skip_checks=["default"])
        config = {"metadata": {"namespace": "not_matched"}}
        check = TestCheck('CKV_1')
        self.assertTrue(instance._should_run_scan(check, config, run_filter, CheckType.KUBERNETES))

    def test_namespace_allow_specific(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=["matched"], skip_checks=[])
        config = {"metadata": {"namespace": "matched"}}
        check = TestCheck('CKV_1')
        self.assertTrue(instance._should_run_scan(check, config, run_filter, CheckType.KUBERNETES))

    def test_namespace_deny_specific(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=[], skip_checks=["matched"])
        config = {"metadata": {"namespace": "matched"}}
        check = TestCheck('CKV_1')
        self.assertFalse(instance._should_run_scan(check, config, run_filter, CheckType.KUBERNETES))

    def test_namespace_allow_specific_other(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=["something_else"], skip_checks=[])
        config = {"metadata": {"namespace": "not_matched"}}
        check = TestCheck('CKV_1')
        self.assertFalse(instance._should_run_scan(check, config, run_filter, CheckType.KUBERNETES))

    def test_namespace_deny_specific_other(self):
        instance = Registry(report_type=CheckType.KUBERNETES)
        run_filter = RunnerFilter(checks=[], skip_checks=["something_else"])
        config = {"metadata": {"namespace": "not_matched"}}
        check = TestCheck('CKV_1')
        self.assertTrue(instance._should_run_scan(check, config, run_filter, CheckType.KUBERNETES))


if __name__ == '__main__':
    unittest.main()
