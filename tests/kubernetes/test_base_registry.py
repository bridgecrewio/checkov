import os
import unittest
from unittest import mock

from checkov.kubernetes.base_registry import Registry
from checkov.runner_filter import RunnerFilter


class TestRunnerFilter(unittest.TestCase):

    def test_run_by_id_default(self):
        instance = Registry()
        self.assertTrue(instance._should_run_scan("CKV_1", {}, [], []))

    def test_run_by_id_specific_enable(self):
        instance = Registry()
        self.assertTrue(instance._should_run_scan("CKV_1", {}, ["CKV_1"], []))

    def test_run_by_id_omitted_specific_enable(self):
        instance = Registry()
        self.assertFalse(instance._should_run_scan("CKV_999", {}, ["CKV_1"], []))

    def test_run_by_id_specific_disable(self):
        instance = Registry()
        self.assertFalse(instance._should_run_scan("CKV_1", {}, [], ["CKV_1"]))

    def test_run_by_id_omitted_specific_disable(self):
        instance = Registry()
        self.assertTrue(instance._should_run_scan("CKV_999", {}, [], ["CKV_1"]))

    def test_run_by_id_external(self):
        instance = Registry()
        self.assertTrue(instance._should_run_scan("CKV_EXT_999", {}, [], ["CKV_1"]))

    def test_run_by_id_external2(self):
        instance = Registry()
        self.assertTrue(instance._should_run_scan("CKV_EXT_999", {}, ["CKV_1"], ["CKV_2"]))

    def test_run_by_id_external3(self):
        instance = Registry()
        self.assertTrue(instance._should_run_scan("CKV_EXT_999", {}, ["CKV_EXT_999"], []))

    def test_run_by_id_external_disabled(self):
        instance = Registry()
        self.assertFalse(instance._should_run_scan("CKV_EXT_999", {}, [], ["CKV_1", "CKV_EXT_999"]))

    def test_run_by_id_specific_disable_AND_enable(self):
        instance = Registry()
        self.assertTrue(instance._should_run_scan("CKV_1", {}, ["CKV_1"], ["CKV_1"]))

    # Namespace filtering

    def test_namespace_allow_default(self):
        instance = Registry()
        config = {"metadata": {"namespace": "not_matched"}}
        # TODO: Maybe this case SHOULD run? Matching old state (false) for now. - @robeden
        self.assertFalse(instance._should_run_scan("CKV_1", config, ["default"], []))

    def test_namespace_deny_default(self):
        instance = Registry()
        config = {"metadata": {"namespace": "not_matched"}}
        # TODO: Maybe this case SHOULDN'T run? Matching old state (true) for now. - @robeden
        self.assertTrue(instance._should_run_scan("CKV_1", config, [], ["default"]))

    def test_namespace_allow_specific(self):
        instance = Registry()
        config = {"metadata": {"namespace": "matched"}}
        self.assertTrue(instance._should_run_scan("CKV_1", config, ["matched"], []))

    def test_namespace_deny_specific(self):
        instance = Registry()
        config = {"metadata": {"namespace": "matched"}}
        self.assertFalse(instance._should_run_scan("CKV_1", config, [], ["matched"]))

    def test_namespace_allow_specific_other(self):
        instance = Registry()
        config = {"metadata": {"namespace": "not_matched"}}
        self.assertFalse(instance._should_run_scan("CKV_1", config, ["something_else"], []))

    def test_namespace_deny_specific_other(self):
        instance = Registry()
        config = {"metadata": {"namespace": "not_matched"}}
        self.assertTrue(instance._should_run_scan("CKV_1", config, [], ["something_else"]))


if __name__ == '__main__':
    unittest.main()
