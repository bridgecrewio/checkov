import os
import unittest
from unittest import mock

from checkov.kubernetes.base_registry import Registry
from checkov.runner_filter import RunnerFilter


class TestRunnerFilter(unittest.TestCase):
    def test_run_by_id_default(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=[], skip_checks=[])
        self.assertTrue(instance._should_run_scan("CKV_1", {}, run_filter))

    def test_run_by_id_specific_enable(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=["CKV_1"], skip_checks=[])
        self.assertTrue(instance._should_run_scan("CKV_1", {}, run_filter))

    def test_run_by_id_omitted_specific_enable(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=["CKV_1"], skip_checks=[])
        self.assertFalse(instance._should_run_scan("CKV_999", {}, run_filter))

    def test_run_by_id_specific_disable(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=[], skip_checks=["CKV_1"])
        self.assertFalse(instance._should_run_scan("CKV_1", {}, run_filter))

    def test_run_by_id_omitted_specific_disable(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=[], skip_checks=["CKV_1"])
        self.assertTrue(instance._should_run_scan("CKV_999", {}, run_filter))

    def test_run_by_id_external(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=[], skip_checks=["CKV_1"])
        run_filter.notify_external_check("CKV_EXT_999")
        self.assertTrue(instance._should_run_scan("CKV_EXT_999", {}, run_filter))

    def test_run_by_id_external2(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=["CKV_1"], skip_checks=["CKV_2"])
        run_filter.notify_external_check("CKV_EXT_999")
        self.assertTrue(instance._should_run_scan("CKV_EXT_999", {}, run_filter))

    def test_run_by_id_external3(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=["CKV_EXT_999"], skip_checks=[])
        run_filter.notify_external_check("CKV_EXT_999")
        self.assertTrue(instance._should_run_scan("CKV_EXT_999", {}, run_filter))

    def test_run_by_id_external_disabled(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=[], skip_checks=["CKV_1", "CKV_EXT_999"])
        run_filter.notify_external_check("CKV_EXT_999")
        self.assertFalse(instance._should_run_scan("CKV_EXT_999", {}, run_filter))

    def test_run_by_id_specific_disable_AND_enable(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=["CKV_1"], skip_checks=["CKV_1"])
        self.assertTrue(instance._should_run_scan("CKV_1", {}, run_filter))

    # Namespace filtering

    def test_namespace_allow_default(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=["default"], skip_checks=[])
        config = {"metadata": {"namespace": "not_matched"}}
        self.assertFalse(instance._should_run_scan("CKV_1", config, run_filter))

    def test_namespace_deny_default(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=[], skip_checks=["default"])
        config = {"metadata": {"namespace": "not_matched"}}
        self.assertTrue(instance._should_run_scan("CKV_1", config, run_filter))

    def test_namespace_allow_specific(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=["matched"], skip_checks=[])
        config = {"metadata": {"namespace": "matched"}}
        self.assertTrue(instance._should_run_scan("CKV_1", config, run_filter))

    def test_namespace_deny_specific(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=[], skip_checks=["matched"])
        config = {"metadata": {"namespace": "matched"}}
        self.assertFalse(instance._should_run_scan("CKV_1", config, run_filter))

    def test_namespace_allow_specific_other(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=["something_else"], skip_checks=[])
        config = {"metadata": {"namespace": "not_matched"}}
        self.assertFalse(instance._should_run_scan("CKV_1", config, run_filter))

    def test_namespace_deny_specific_other(self):
        instance = Registry()
        run_filter = RunnerFilter(checks=[], skip_checks=["something_else"])
        config = {"metadata": {"namespace": "not_matched"}}
        self.assertTrue(instance._should_run_scan("CKV_1", config, run_filter))


if __name__ == "__main__":
    unittest.main()
