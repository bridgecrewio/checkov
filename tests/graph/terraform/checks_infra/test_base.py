import os
from unittest import TestCase

from checkov.terraform.checks_infra.checks_parser import NXGraphCheckParser
from checkov.terraform.checks_infra.registry import Registry
from checkov.terraform.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestBaseSolver(TestCase):
    checks_dir = ""

    def setUp(self):
        self.source = "Terraform"
        self.registry = Registry(parser=NXGraphCheckParser(), checks_dir=self.checks_dir)
        self.registry.load_checks()
        self.runner = Runner(external_registries=[self.registry])

    def run_test(self, root_folder, expected_results, check_id):
        root_folder = os.path.realpath(os.path.join(self.checks_dir, root_folder))
        report = self.runner.run(root_folder=root_folder, runner_filter=RunnerFilter(checks=[check_id]))
        verification_results = verify_report(report=report, expected_results=expected_results)
        self.assertIsNone(verification_results, verification_results)


def verify_report(report, expected_results):
    for check_id in expected_results:
        found = False
        for resource in expected_results[check_id]['should_pass']:
            for record in report.passed_checks:
                if record.check_id == check_id and record.resource == resource:
                    found = True
                    break
            if not found:
                return f"expected resource {resource} to pass in check {check_id}"
        found = False
        for resource in expected_results[check_id]['should_fail']:
            for record in report.failed_checks:
                if record.check_id == check_id and record.resource == resource:
                    found = True
                    break
            if not found:
                return f"expected resource {resource} to fail in check {check_id}"

    return None
