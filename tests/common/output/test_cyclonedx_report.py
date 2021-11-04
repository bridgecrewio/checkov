import unittest
from os.path import dirname, join

from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.runner_filter import RunnerFilter
from checkov.terraform.plan_runner import Runner as tf_plan_runner
from checkov.terraform.runner import Runner as tf_graph_runner


class TestCycloneDxReport(unittest.TestCase):

    def test_valid_cyclonedx_bom(self):
        runners = (tf_graph_runner(), tf_plan_runner(),)
        registry = RunnerRegistry("", RunnerFilter(), *runners)
        scan_reports = registry.run(files=[
            join(dirname(__file__), 'fixtures/main.tf')
        ])

        self.assertEqual(len(scan_reports), 2)
        r = scan_reports[0]

        cyclonedx_bom = r.get_cyclonedx_bom()
        # outputter = get_instance(bom=cyclonedx_bom)
        # outputter.output_to_file(filename='/tmp/test.xml', allow_overwrite=True)
        self.assertEqual(len(cyclonedx_bom.get_components()), 1)
        first_component = cyclonedx_bom.get_components()[0]
        self.assertEqual(len(first_component.get_vulnerabilities()), 5)


if __name__ == '__main__':
    unittest.main()
