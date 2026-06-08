"""
Tests for the fuzzy-prefix inline suppression fix in the Terraform graph runner.

When a custom YAML check has id=CKV_CUSTOM_<uuid>, a skip comment using any
*_CUSTOM_<same-uuid> prefix (e.g. LETTER_CUSTOM_*, APPSEC_CUSTOM_*) must also
suppress the check.  A skip comment with a *_CUSTOM_<different-uuid> must NOT.
"""
import os
import unittest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.runner import Runner

CUSTOM_CHECK_ID = "CKV_CUSTOM_a12f9ef1-1234-5678-1234-1234d0225678"

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TF_DIR = os.path.join(CURRENT_DIR, "resources", "custom_prefix_suppression")
YAML_CHECKS_DIR = os.path.join(CURRENT_DIR, "extra_yaml_checks")


class TestCustomPrefixInlineSuppression(unittest.TestCase):
    """
    Verifies that the *_CUSTOM_<uuid> fuzzy-prefix matching in
    BaseTerraformRunner.get_graph_checks_report() works correctly.

    No bc_id / platform-metadata mapping is needed — these tests exercise
    the pure regex path added to base_runner.py.
    """

    def tearDown(self) -> None:
        # Remove the custom check from the resource registry to avoid polluting other tests
        for entity_checks in resource_registry.checks.values():
            entity_checks[:] = [c for c in entity_checks if c.id != CUSTOM_CHECK_ID]
        for entity_checks in resource_registry.wildcard_checks.values():
            entity_checks[:] = [c for c in entity_checks if c.id != CUSTOM_CHECK_ID]
        # Remove the custom check from the graph registry (always runs even if test raises)
        graph_registry = get_graph_checks_registry(CheckType.TERRAFORM)
        graph_registry.checks[:] = [c for c in graph_registry.checks if CUSTOM_CHECK_ID not in c.id]

    def _run(self) -> "tuple[list, list]":
        """Run the Terraform runner and return (skipped, failed) for CUSTOM_CHECK_ID."""
        runner = Runner(db_connector=NetworkxConnector())
        report = runner.run(
            root_folder=TF_DIR,
            external_checks_dir=[YAML_CHECKS_DIR],
            runner_filter=RunnerFilter(framework=["terraform"], checks=[CUSTOM_CHECK_ID]),
        )
        skipped = [r for r in report.skipped_checks if r.check_id == CUSTOM_CHECK_ID]
        failed = [r for r in report.failed_checks if r.check_id == CUSTOM_CHECK_ID]
        # Clean up graph registry
        runner.graph_registry.checks[:] = [
            c for c in runner.graph_registry.checks if CUSTOM_CHECK_ID not in c.id
        ]
        return skipped, failed

    def test_skip_with_original_ckv_prefix_suppresses_check(self) -> None:
        """
        Regression test: skip comment using the same CKV_CUSTOM_* prefix as check.id works.

        Given:
          - A YAML custom check with id=CKV_CUSTOM_<uuid>
          - aws_db_instance.suppressed_ckv_prefix has # checkov:skip=CKV_CUSTOM_<uuid>
          - No bc_id mapping configured

        Then:
          - aws_db_instance.suppressed_ckv_prefix is in skipped_checks
        """
        skipped, _ = self._run()
        skipped_resources = [r.resource for r in skipped]
        self.assertIn(
            "aws_db_instance.suppressed_ckv_prefix",
            skipped_resources,
            f"Expected suppressed_ckv_prefix to be skipped; skipped={skipped_resources}",
        )

    def test_skip_with_alternate_prefix_suppresses_check(self) -> None:
        """
        New behaviour: skip comment using a different prefix (LETTER_CUSTOM_*) but the same UUID
        as check.id (CKV_CUSTOM_*) correctly suppresses the check.

        Given:
          - A YAML custom check with id=CKV_CUSTOM_<uuid>
          - aws_db_instance.suppressed_appsec_prefix has # checkov:skip=LETTER_CUSTOM_<uuid>
          - No bc_id mapping configured

        Then:
          - aws_db_instance.suppressed_appsec_prefix is in skipped_checks
        """
        skipped, _ = self._run()
        skipped_resources = [r.resource for r in skipped]
        self.assertIn(
            "aws_db_instance.suppressed_appsec_prefix",
            skipped_resources,
            f"Expected suppressed_appsec_prefix to be skipped; skipped={skipped_resources}",
        )

    def test_skip_with_wrong_uuid_does_not_suppress(self) -> None:
        """
        Safety test: skip comment using *_CUSTOM_<different-uuid> does NOT suppress the check.

        Given:
          - A YAML custom check with id=CKV_CUSTOM_<uuid-A>
          - aws_db_instance.wrong_uuid_skip has # checkov:skip=CKV_CUSTOM_<uuid-B>
          - No bc_id mapping configured

        Then:
          - aws_db_instance.wrong_uuid_skip is NOT in skipped_checks
          - aws_db_instance.wrong_uuid_skip IS in failed_checks
        """
        skipped, failed = self._run()
        skipped_resources = [r.resource for r in skipped]
        failed_resources = [r.resource for r in failed]
        self.assertNotIn(
            "aws_db_instance.wrong_uuid_skip",
            skipped_resources,
            f"wrong_uuid_skip must NOT be suppressed; skipped={skipped_resources}",
        )
        self.assertIn(
            "aws_db_instance.wrong_uuid_skip",
            failed_resources,
            f"wrong_uuid_skip must appear in failed_checks; failed={failed_resources}",
        )


if __name__ == "__main__":
    unittest.main()
