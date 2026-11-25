import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner

RESOURCES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "count_index_fallback")


class TestCountIndexFallback(unittest.TestCase):
    def test_plain_text_mention_does_not_link_to_counted_resource(self) -> None:
        # https://github.com/bridgecrewio/checkov/issues/7765
        # A description and a validation error_message mention a counted resource and a local by name.
        # The count/for_each fallback added in #7736 used to link those mentions to widget[0], which
        # broke how var.target_image was rendered into kubernetes_deployment_v1.target.
        report = Runner().run(
            root_folder=RESOURCES_DIR,
            runner_filter=RunnerFilter(
                framework=["terraform"],
                checks=["CKV_K8S_14", "CKV_K8S_15", "CKV_K8S_43"],
                var_files=[os.path.join(RESOURCES_DIR, "opt-in.tfvars")],
            ),
        )

        failed = [(c.check_id, c.resource) for c in report.failed_checks]
        self.assertEqual(failed, [])
        passed = {(c.check_id, c.resource) for c in report.passed_checks}
        self.assertEqual(
            passed,
            {
                ("CKV_K8S_14", "kubernetes_deployment_v1.target[0]"),
                ("CKV_K8S_15", "kubernetes_deployment_v1.target[0]"),
                ("CKV_K8S_43", "kubernetes_deployment_v1.target[0]"),
            },
        )


if __name__ == "__main__":
    unittest.main()
