import os
import unittest
from unittest import mock

from checkov.common.graph.graph_builder.deterministic import DEDUP_COMPAT_ENV, IDEMPOTENT_DYNAMIC_BLOCKS_ENV, \
    dedup_compat_enabled, idempotent_dynamic_blocks_enabled
from checkov.terraform.diff_scan import scan
from checkov.terraform.diff_scan.inputs import config_fingerprint


class TestFindingsFixDefaults(unittest.TestCase):
    @mock.patch.dict(os.environ, {}, clear=True)
    def test_every_diff_scan_mode_enables_both_fixes(self):
        scan.enable_flags()
        self.assertTrue(idempotent_dynamic_blocks_enabled())
        self.assertTrue(dedup_compat_enabled())

    @mock.patch.dict(os.environ, {IDEMPOTENT_DYNAMIC_BLOCKS_ENV: "false", DEDUP_COMPAT_ENV: "false"}, clear=True)
    def test_explicit_opt_out_is_kept(self):
        scan.enable_flags()
        self.assertFalse(idempotent_dynamic_blocks_enabled())
        self.assertFalse(dedup_compat_enabled())

    def test_opting_out_changes_the_result_fingerprint(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            scan.enable_flags()
            default = config_fingerprint({})
        with mock.patch.dict(os.environ, {IDEMPOTENT_DYNAMIC_BLOCKS_ENV: "false"}, clear=True):
            scan.enable_flags()
            opted_out = config_fingerprint({})
        self.assertNotEqual(default, opted_out)


if __name__ == "__main__":
    unittest.main()
