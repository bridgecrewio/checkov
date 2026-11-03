import os
import unittest
from unittest import mock

from checkov.common.models.enums import CheckResult
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.terraform.checks.resource.gcp.GoogleComputeIPForward import check as negative_value_check
from checkov.terraform.checks.resource.kubernetes.LivenessProbe import check as liveness_probe
from checkov.terraform.checks.resource.kubernetes.ReadonlyRootFilesystem import check as readonly_root_fs
from checkov.terraform.parser_functions import expand_dynamic_values_completely, handle_dynamic_values

FLAG = "CHECKOV_IDEMPOTENT_DYNAMIC_BLOCKS"


def deployment_with_unrendered_dynamic_container() -> dict:
    """The rendered shape of gcp-configuration tf/modules/app deployment.tf: dynamic "init_container" and
    "container" blocks whose for_each (locals built with a for expression) were not rendered, each holding nested
    dynamic blocks. handle_dynamic_values only recurses into the FIRST element of a list of blocks, so the nested
    dynamic blocks of the second entry ("container") are never visited before the entry is copied: the first
    expansion yields a container without liveness_probe / security_context. Expanding the copied container's nested
    blocks happens on the next call, which also appends another copy."""
    def with_nested(prefix: str) -> dict:
        return {
            "name": [f'lookup({prefix}.value,"name")'],
            "dynamic": [{"liveness_probe": {"content": [{"period_seconds": [10]}],
                                            "for_each": [f'lookup({prefix}.value,"liveness_probe",{{}})']}},
                        {"security_context": {"content": [{"read_only_root_filesystem": [True]}],
                                              "for_each": [f'lookup({prefix}.value,"security_context",false)']}}],
        }

    dynamic_blocks = [
        {"init_container": {"content": [with_nested("init_container")], "for_each": ["local.init_containers_by_name"]}},
        {"container": {"content": [with_nested("container")], "for_each": ["local.containers_by_name"]}},
    ]
    return {"spec": [{"template": [{"spec": [{"dynamic": dynamic_blocks}]}]}]}


def expansion_shape(conf: dict) -> list[tuple[bool, bool]]:
    containers = conf["spec"][0]["template"][0]["spec"][0].get("container") or []
    return [(bool(c.get("liveness_probe")), bool(c.get("security_context"))) for c in containers]


class TestUpstreamDynamicBlockMutation(unittest.TestCase):
    def test_upstream_expansion_grows_and_completes_with_each_call(self):
        conf = deployment_with_unrendered_dynamic_container()
        handle_dynamic_values(conf)
        self.assertEqual(expansion_shape(conf), [(False, False)])
        handle_dynamic_values(conf)
        self.assertEqual(expansion_shape(conf), [(True, True), (False, False)])

    @mock.patch.dict(os.environ, {FLAG: "false"})
    def test_upstream_result_depends_on_the_checks_run_before(self):
        alone = deployment_with_unrendered_dynamic_container()
        self.assertEqual(liveness_probe.scan_entity_conf(alone, "kubernetes_deployment"), CheckResult.FAILED)

        after_another_check = deployment_with_unrendered_dynamic_container()
        readonly_root_fs.scan_entity_conf(after_another_check, "kubernetes_deployment")
        self.assertEqual(liveness_probe.scan_entity_conf(after_another_check, "kubernetes_deployment"),
                         CheckResult.PASSED)


class TestIdempotentDynamicBlocks(unittest.TestCase):
    @mock.patch.dict(os.environ, {FLAG: "true"})
    def test_result_does_not_depend_on_the_checks_run_before(self):
        alone = deployment_with_unrendered_dynamic_container()
        after_another_check = deployment_with_unrendered_dynamic_container()
        readonly_root_fs.scan_entity_conf(after_another_check, "kubernetes_deployment")

        self.assertEqual(liveness_probe.scan_entity_conf(alone, "kubernetes_deployment"),
                         liveness_probe.scan_entity_conf(after_another_check, "kubernetes_deployment"))

    def test_one_complete_expansion_without_extra_copies(self):
        conf = deployment_with_unrendered_dynamic_container()
        expand_dynamic_values_completely(conf)
        self.assertEqual(expansion_shape(conf), [(True, True)])

    @mock.patch.dict(os.environ, {FLAG: "true"})
    def test_nested_blocks_of_a_later_dynamic_entry_are_seen(self):
        conf = deployment_with_unrendered_dynamic_container()
        self.assertEqual(liveness_probe.scan_entity_conf(conf, "kubernetes_deployment"), CheckResult.PASSED)

    @mock.patch.dict(os.environ, {FLAG: "true"})
    def test_rendered_config_without_dynamic_blocks_gives_upstream_result(self):
        rendered = {"spec": [{"template": [{"spec": [{"container": [{"name": ["c"]}]}]}]}]}
        flagged = liveness_probe.scan_entity_conf(pickle_deepcopy(rendered), "kubernetes_deployment")
        with mock.patch.dict(os.environ, {FLAG: "false"}):
            upstream = liveness_probe.scan_entity_conf(pickle_deepcopy(rendered), "kubernetes_deployment")
        self.assertEqual(flagged, upstream)
        self.assertEqual(flagged, CheckResult.FAILED)

    @mock.patch.dict(os.environ, {FLAG: "true"})
    def test_shared_config_is_not_modified(self):
        conf = deployment_with_unrendered_dynamic_container()
        before = pickle_deepcopy(conf)
        readonly_root_fs.scan_entity_conf(conf, "kubernetes_deployment")
        liveness_probe.scan_entity_conf(conf, "kubernetes_deployment")
        self.assertEqual(conf, before)

    def test_value_checks_expand_once(self):
        def copies_seen_by_value_check() -> int:
            conf = {"can_ip_forward": [False], "dynamic": [{"network_interface": {"content": {"network": ["n"]}}}]}
            seen = []
            with mock.patch.object(type(negative_value_check), "get_inspected_key",
                                   side_effect=lambda: seen.append(1) or "can_ip_forward", create=True), \
                    mock.patch("dpath.search", side_effect=lambda c, k: seen.append(len(c.get("network_interface", [])))
                               or {}):
                negative_value_check.scan_entity_conf(conf, "google_compute_instance")
            return max(n for n in seen)

        with mock.patch.dict(os.environ, {FLAG: "false"}):
            self.assertEqual(copies_seen_by_value_check(), 2)
        with mock.patch.dict(os.environ, {FLAG: "true"}):
            self.assertEqual(copies_seen_by_value_check(), 1)

    @mock.patch.dict(os.environ, {FLAG: "true"})
    def test_value_check_result_matches_upstream_on_rendered_config(self):
        rendered = {"can_ip_forward": [True]}
        flagged = negative_value_check.scan_entity_conf(pickle_deepcopy(rendered), "google_compute_instance")
        with mock.patch.dict(os.environ, {FLAG: "false"}):
            upstream = negative_value_check.scan_entity_conf(pickle_deepcopy(rendered), "google_compute_instance")
        self.assertEqual(flagged, upstream)
        self.assertEqual(flagged, CheckResult.FAILED)


if __name__ == "__main__":
    unittest.main()
