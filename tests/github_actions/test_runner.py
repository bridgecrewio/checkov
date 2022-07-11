import os
import unittest
from pathlib import Path

from checkov.github_actions.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRunnerValid(unittest.TestCase):
    def test_runner(self):
        # given
        test_dir = Path(__file__).parent / "resources"
        checks = ["CKV_GHA_1", "CKV_GHA_2"]

        # when
        report = Runner().run(
            root_folder=str(test_dir), runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        self.assertEqual(len(report.failed_checks), 9)
        self.assertEqual(len(report.parsing_errors), 0)
        self.assertEqual(len(report.passed_checks), 41)
        self.assertEqual(len(report.skipped_checks), 0)

    def test_runner_on_suspectcurl(self):
        # given
        file_dir = ["./resources/.github/workflows/suspectcurl.yaml"]
        checks = ["CKV_GHA_1", "CKV_GHA_3"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert report.failed_checks[0].jobs[0] == {
            'prep': {'__startline__': 15, '__endline__': 19},
            'build': {'__startline__': 21, '__endline__': 33}}

        assert report.failed_checks[0].triggers[0] == {'push', 'workflow_dispatch'}
        assert report.failed_checks[0].workflow_name == 'CI'

    def test_runner_on_shell_injection(self):
        # given
        file_dir = [
            "./resources/.github/workflows/shell_injection.yaml"]
        checks = ["CKV_GHA_1", "CKV_GHA_3"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert report.passed_checks[0].jobs[0] == {
            'job1': {'__startline__': 6, '__endline__': 14},
            'job2': {'__startline__': 15, '__endline__': 19},
            'unsecure-steps': {'__startline__': 20, '__endline__': 64}}

        assert report.passed_checks[0].triggers[0] == {'issues'}
        assert report.passed_checks[0].workflow_name == 'unsec33ure-worfklow'

    def test_runner_on_netcatreverseshell(self):
        # given
        file_dir = [
            "./resources/.github/workflows/netcatreverseshell.yaml"]
        checks = ["CKV_GHA_1", "CKV_GHA_3"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert report.passed_checks[0].jobs[0] == {
            'prep': {'__startline__': 15, '__endline__': 19},
            'build': {'__startline__': 21, '__endline__': 33}}

        assert report.passed_checks[0].triggers[0] == {'workflow_dispatch', 'push'}
        assert report.passed_checks[0].workflow_name == 'REVERSESHELL'

    def test_runner_on_unsecure_command(self):
        # given
        file_dir = [
            "./resources/.github/workflows/unsecure_command.yaml"]
        checks = ["CKV_GHA_1", "CKV_GHA_3"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert report.passed_checks[0].jobs[0] == {
            'job2': {'__startline__': 7, '__endline__': 15},
            'job3': {'__startline__': 16, '__endline__': 21}}

        assert report.passed_checks[0].triggers[0] == {'pull_request'}
        assert report.passed_checks[0].workflow_name == 'unsecure-worfklow'

    def test_runner_on_supply_chain(self):
        # given
        file_dir = [
            "./resources/.github/workflows/supply_chain.yaml"]
        checks = ["CKV_GHA_1", "CKV_GHA_3"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert report.failed_checks[0].jobs[0] == \
               {"bridgecrew": {"__startline__": 8, "__endline__": 20},
                "bridgecrew2": {"__startline__": 21, "__endline__": 33}
                }

        assert report.failed_checks[0].triggers[0] == {"workflow_dispatch", "schedule"}
        assert report.failed_checks[0].workflow_name == 'Supply Chain'

    def test_runner_on_build(self):
        # given
        file_dir = ["../../.github/workflows/build.yml"]
        checks = ["CKV_GHA_1", "CKV_GHA_3"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert report.failed_checks[0].jobs[0] == \
               {'integration-tests': {'__startline__': 25, '__endline__': 70},
                'prisma-tests': {'__startline__': 71, '__endline__': 97},
                'unit-tests': {'__startline__': 98, '__endline__': 120},
                'bump-version': {'__startline__': 121, '__endline__': 219},
                'publish-checkov-dockerhub': {'__startline__': 220, '__endline__': 240},
                'publish-checkov-k8s-dockerhub': {'__startline__': 241, '__endline__': 262},
                'publish-checkov-admissioncontroller-dockerhub': {'__startline__': 263, '__endline__': 300},
                'publish-checkov-pyston-dockerhub': {'__startline__': 301, '__endline__': 322},
                'update-bridgecrew-projects': {'__startline__': 323, '__endline__': 332}}

        assert report.failed_checks[0].triggers[0] == {'workflow_dispatch', 'push'}
        assert report.failed_checks[0].workflow_name == 'build'

    def test_runner_on_codeql_analysis(self):
        # given
        file_dir = ["../../.github/workflows/codeql-analysis.yml"]
        checks = ["CKV_GHA_1", "CKV_GHA_3"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert report.passed_checks[0].jobs[0] == \
               {'Analyze': {'__startline__': 27, '__endline__': 63}}

        assert report.passed_checks[0].triggers[0] == {'push', 'schedule', 'pull_request', 'workflow_dispatch'}
        assert report.passed_checks[0].workflow_name == 'CodeQL'


if __name__ == "__main__":
    unittest.main()
