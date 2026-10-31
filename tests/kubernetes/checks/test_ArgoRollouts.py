import os
import unittest
from collections import defaultdict

from checkov.kubernetes.image_referencer.provider.k8s import SUPPORTED_K8S_IMAGE_RESOURCE_TYPES
from checkov.kubernetes.runner import Runner
from checkov.runner_filter import RunnerFilter

EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "example_ArgoRollouts")

# Pod spec checks that fail when there is no pod spec to inspect
POD_SPEC_CHECKS = ["CKV_K8S_23", "CKV_K8S_29", "CKV_K8S_31", "CKV_K8S_38", "CKV_K8S_40"]


class TestArgoRollouts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        report = Runner().run(root_folder=EXAMPLES_DIR, runner_filter=RunnerFilter(framework=["kubernetes"]))
        cls.failed = defaultdict(set)
        cls.passed = defaultdict(set)
        for record in report.failed_checks:
            cls.failed[record.resource].add(record.check_id)
        for record in report.passed_checks:
            cls.passed[record.resource].add(record.check_id)
        cls.parsing_errors = report.get_summary()["parsing_errors"]

    def test_no_parsing_errors(self):
        self.assertEqual(self.parsing_errors, 0)

    def test_rollout_gets_the_same_findings_as_the_equivalent_deployment(self):
        self.assertTrue(self.failed["Deployment.web.insecure"])
        self.assertEqual(self.failed["Rollout.web.insecure"], self.failed["Deployment.web.insecure"])

    def test_pod_template_checks_apply_to_rollouts(self):
        # CKV_K8S_16 privileged, CKV_K8S_20 allowPrivilegeEscalation, CKV_K8S_22 readOnlyRootFilesystem,
        # CKV_K8S_29 pod securityContext, CKV_K8S_37 capabilities
        for check_id in ["CKV_K8S_16", "CKV_K8S_20", "CKV_K8S_22", "CKV_K8S_29", "CKV_K8S_37"]:
            with self.subTest(check_id=check_id):
                self.assertIn(check_id, self.failed["Rollout.web.insecure"])
                self.assertIn(check_id, self.passed["Rollout.web.hardened"])

    def test_workload_ref_rollout_is_not_flagged_for_a_missing_pod_spec(self):
        for check_id in POD_SPEC_CHECKS:
            with self.subTest(check_id=check_id):
                self.assertNotIn(check_id, self.failed["Rollout.web.workload-ref"])
                self.assertNotIn(check_id, self.passed["Rollout.web.workload-ref"])

    def test_images_are_extracted_from_the_rollout_template(self):
        rollout = {
            "kind": "Rollout",
            "spec": {"template": {"spec": {
                "initContainers": [{"name": "init", "image": "example.com/init:1"}],
                "containers": [{"name": "app", "image": "example.com/app:1"}],
            }}},
        }
        images = SUPPORTED_K8S_IMAGE_RESOURCE_TYPES["Rollout"](rollout)
        self.assertEqual(sorted(images), ["example.com/app:1", "example.com/init:1"])


if __name__ == "__main__":
    unittest.main()
