import os
import unittest
from unittest import mock

from checkov.runner_filter import RunnerFilter


class TestRunnerFilter(unittest.TestCase):

    # Expected pseudo-code for when checks should run:
    #    if has_check_flag_specified():
    #        checks_to_run = checks_specifically_included
    #    else:
    #        checks_to_run = all_built_in_checks
    #    if has_checks_dir_specified():
    #       checks_to_run += checks_from_external_dir
    #    for skipped_check in skip_check_flags():
    #        checks_to_run.remove(skipped_check)

    def test_should_run_default(self):
        instance = RunnerFilter()
        self.assertTrue(instance.should_run_check("CHECK_1"))

    def test_should_run_specific_enable(self):
        instance = RunnerFilter(checks=["CHECK_1"])
        self.assertTrue(instance.should_run_check("CHECK_1"))

    def test_should_run_omitted_specific_enable(self):
        instance = RunnerFilter(checks=["CHECK_1"])
        self.assertFalse(instance.should_run_check("CHECK_999"))

    def test_should_run_specific_disable(self):
        instance = RunnerFilter(skip_checks=["CHECK_1"])
        self.assertFalse(instance.should_run_check("CHECK_1"))

    def test_should_run_omitted_specific_disable(self):
        instance = RunnerFilter(skip_checks=["CHECK_1"])
        self.assertTrue(instance.should_run_check("CHECK_999"))

    def test_should_run_external(self):
        instance = RunnerFilter(skip_checks=["CHECK_1"])
        instance.notify_external_check("EXT_CHECK_999")
        self.assertTrue(instance.should_run_check("EXT_CHECK_999"))

    def test_should_run_external2(self):
        instance = RunnerFilter(checks=["CHECK_1"], skip_checks=["CHECK_2"])
        instance.notify_external_check("EXT_CHECK_999")
        self.assertTrue(instance.should_run_check("EXT_CHECK_999"))

    def test_should_run_external3(self):
        instance = RunnerFilter(checks=["EXT_CHECK_999"])
        instance.notify_external_check("EXT_CHECK_999")
        self.assertTrue(instance.should_run_check("EXT_CHECK_999"))

    def test_should_run_external_disabled(self):
        instance = RunnerFilter(skip_checks=["CHECK_1", "EXT_CHECK_999"])
        instance.notify_external_check("EXT_CHECK_999")
        self.assertFalse(instance.should_run_check("EXT_CHECK_999"))

    def test_should_run_specific_disable_AND_enable(self):
        instance = RunnerFilter(checks=["CHECK_1"], skip_checks=["CHECK_1"])
        self.assertTrue(instance.should_run_check("CHECK_1"))


if __name__ == '__main__':
    unittest.main()
