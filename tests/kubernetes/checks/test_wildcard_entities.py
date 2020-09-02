import os
import unittest

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check
from checkov.kubernetes.registry import registry
from checkov.kubernetes.runner import Runner
from checkov.runner_filter import RunnerFilter


class KubernetesCheck(BaseK8Check):

    def __init__(self):
        name = "Kubernetes test"
        id = "CKV_T_1"
        supported_kind = ['container?', 'Pod*Policy']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf):
        return CheckResult.PASSED

    def get_resource_id(self, conf):
        return f'{conf["kind"]}'


class TestWildcardEntities(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        check = KubernetesCheck()

        test_files_dir = current_dir + "/example_WildcardEntities"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        registry.wildcard_checks['container?'].remove(check)
        registry.wildcard_checks['Pod*Policy'].remove(check)

        self.assertEqual(summary['passed'], 2)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)


if __name__ == '__main__':
    unittest.main()
