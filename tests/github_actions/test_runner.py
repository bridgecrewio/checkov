import tempfile
import unittest
from pathlib import Path

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.github_actions.runner import Runner
from checkov.runner_filter import RunnerFilter
from checkov.github_actions.checks.registry import registry

# Minimal workflow from #7786: workflow_dispatch with an input fails CKV_GHA_7
WORKFLOW_YAML = """name: ci
on:
  workflow_dispatch:
    inputs:
      foo:
        description: an input
        required: false
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "${{ github.event.inputs.foo }}"
"""


class TestRunnerValid(unittest.TestCase):

    def test_registry_has_type(self):
        self.assertEqual(registry.report_type, CheckType.GITHUB_ACTIONS)

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
        # the resources dir intentionally holds 3 schema-invalid workflows
        # (bad_format, empty_jobs, nested_jobs), which are reported as
        # parsing errors instead of dropped silently
        self.assertEqual(len(report.parsing_errors), 3)
        self.assertEqual(len(report.passed_checks), 157)
        self.assertEqual(len(report.skipped_checks), 0)

    def test_runner_scans_workflow_with_cache_mode(self):
        # regression test for #7786: a workflow using the cache-mode key
        # must be scanned instead of silently skipped
        with tempfile.TemporaryDirectory() as tmp_dir:
            workflow_dir = Path(tmp_dir) / ".github" / "workflows"
            workflow_dir.mkdir(parents=True)
            workflow_file = workflow_dir / "ci.yml"
            workflow_file.write_text(WORKFLOW_YAML.replace("name: ci", "name: ci\ncache-mode: read"))

            # when
            report = Runner().run(
                root_folder=tmp_dir, runner_filter=RunnerFilter(framework=["github_actions"])
            )

        # then
        self.assertEqual(len(report.parsing_errors), 0)
        self.assertEqual(len(report.passed_checks), 11)
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.failed_checks[0].check_id, "CKV_GHA_7")

    def test_runner_reports_schema_invalid_workflow(self):
        # a workflow file that fails schema validation is reported as a
        # parsing error instead of dropped silently
        with tempfile.TemporaryDirectory() as tmp_dir:
            workflow_dir = Path(tmp_dir) / ".github" / "workflows"
            workflow_dir.mkdir(parents=True)
            workflow_file = workflow_dir / "ci.yml"
            workflow_file.write_text(WORKFLOW_YAML.replace("name: ci", "name: ci\ncache-mode: bogus"))

            # when
            report = Runner().run(
                root_folder=tmp_dir, runner_filter=RunnerFilter(framework=["github_actions"])
            )

        # then
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(report.parsing_errors, [str(workflow_file)])

    def test_runner_multi_file(self):
        # given
        file_path = Path(__file__).parent / "gha/.github/workflows/multi_file.yaml"
        file_dir = [str(file_path)]
        filter = RunnerFilter(framework=['github_actions'])

        # when
        report = Runner().run(files=file_dir, runner_filter=filter)

        # then
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        # the first document has an empty jobs mapping, so the file fails
        # schema validation and is reported as a parsing error instead of
        # dropped silently
        self.assertEqual(len(report.parsing_errors), 1)

    def test_runner_honors_enforcement_rules(self):
        # given
        test_dir = Path(__file__).parent / "resources"
        filter = RunnerFilter(framework=['github_actions'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.GITHUB_ACTIONS: Severities[BcSeverities.OFF]}

        # when
        report = Runner().run(
            root_folder=str(test_dir), runner_filter=filter
        )

        # then
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        # the resources dir intentionally holds 3 schema-invalid workflows,
        # which are reported as parsing errors instead of dropped silently
        self.assertEqual(len(report.parsing_errors), 3)

    def test_runner_on_suspectcurl(self):
        # given
        file_path = Path(__file__).parent / "resources/.github/workflows/suspectcurl.yaml"
        file_dir = [str(file_path)]
        checks = ["CKV_GHA_1", "CKV_GHA_3"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert report.failed_checks[0].job[0] == 'prep'
        assert report.failed_checks[0].triggers[0] == {'push', 'workflow_dispatch'}
        assert report.failed_checks[0].workflow_name == 'CI'

        assert report.failed_checks[1].job[0] == 'build'
        assert report.failed_checks[1].triggers[0] == {'push', 'workflow_dispatch'}
        assert report.failed_checks[1].workflow_name == 'CI'

    def test_runner_on_bad_jobs(self):
        # given
        file_path = Path(__file__).parent / "resources/.github/workflows/nested_jobs.yaml"
        file_dir = [str(file_path)]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"])
        )

        # then
        assert len(report.passed_checks) + len(report.failed_checks) == 0

    def test_runner_on_shell_injection(self):
        # given
        file_path = Path(__file__).parent / "resources/.github/workflows/shell_injection.yaml"
        file_dir = [str(file_path)]
        checks = ["CKV_GHA_1", "CKV_GHA_3"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert report.passed_checks[0].job[0] == 'unsecure-job'
        assert report.passed_checks[0].triggers[0] == {'issues'}
        assert report.passed_checks[0].workflow_name == 'unsec33ure-worfklow'

        assert report.passed_checks[1].job[0] == 'secure-job'
        assert report.passed_checks[1].triggers[0] == {'issues'}
        assert report.passed_checks[1].workflow_name == 'unsec33ure-worfklow'

        assert report.passed_checks[2].job[0] == 'unsecure-steps'
        assert report.passed_checks[2].triggers[0] == {'issues'}
        assert report.passed_checks[2].workflow_name == 'unsec33ure-worfklow'

    def test_runner_on_netcatreverseshell(self):
        # given
        file_path = Path(__file__).parent / "resources/.github/workflows/netcatreverseshell.yaml"
        file_dir = [str(file_path)]
        checks = ["CKV_GHA_1", "CKV_GHA_3"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert report.passed_checks[0].job[0] == 'prep'
        assert report.passed_checks[0].triggers[0] == {'workflow_dispatch', 'push'}
        assert report.passed_checks[0].workflow_name == 'REVERSESHELL'

        assert report.passed_checks[1].job[0] == 'build'
        assert report.passed_checks[1].triggers[0] == {'workflow_dispatch', 'push'}
        assert report.passed_checks[1].workflow_name == 'REVERSESHELL'

    def test_runner_on_unsecure_command(self):
        # given
        file_path = Path(__file__).parent / "resources/.github/workflows/unsecure_command.yaml"
        file_dir = [str(file_path)]

        checks = ["CKV_GHA_1", "CKV_GHA_3"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert report.failed_checks[0].job[0] == 'unsecure-job'
        assert report.failed_checks[0].triggers[0] == {'pull_request'}
        assert report.failed_checks[0].workflow_name == 'unsecure-worfklow'

        assert report.passed_checks[2].job[0] == 'secure-job'
        assert report.passed_checks[2].triggers[0] == {'pull_request'}
        assert report.passed_checks[2].workflow_name == 'unsecure-worfklow'

    def test_runner_on_non_empty_workflow_dispatch(self):
        # given
        file_path = Path(__file__).parent / "resources/.github/workflows/workflow_dispatch.yaml"
        file_dir = [str(file_path)]

        checks = ["CKV_GHA_7"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert report.failed_checks[0].job[0] == ''
        assert report.failed_checks[0].triggers[0] == {'workflow_dispatch'}
        assert report.failed_checks[0].workflow_name == ''

    def test_runner_on_list_typed_workflow_dispatch(self):
        # given
        file_path = Path(__file__).parent / "resources/.github/workflows/list_workflow_dispatch.yml"
        file_dir = [str(file_path)]

        checks = ["CKV_GHA_7"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert len(report.failed_checks) == 0

    def test_runner_on_supply_chain(self):
        # given
        file_path = Path(__file__).parent / "resources/.github/workflows/supply_chain.yaml"
        file_dir = [str(file_path)]
        checks = ["CKV_GHA_1", "CKV_GHA_3"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert report.failed_checks[0].job[0] == "bridgecrew"
        assert report.failed_checks[0].triggers[0] == {"workflow_dispatch", "schedule"}
        assert report.failed_checks[0].workflow_name == 'Supply Chain'

        assert report.passed_checks[1].job[0] == "bridgecrew2"
        assert report.passed_checks[1].triggers[0] == {"workflow_dispatch", "schedule"}
        assert report.passed_checks[1].workflow_name == 'Supply Chain'

    def test_runner_on_build(self):
        # given
        file_path = Path(__file__).parent.parent.parent / ".github/workflows/build.yml"
        file_dir = [str(file_path)]
        checks = ["CKV_GHA_1", "CKV_GHA_3"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert report.failed_checks[0].job[0] == 'update-bridgecrew-projects'
        assert report.failed_checks[0].triggers[0] == {'workflow_dispatch', 'push'}
        assert report.failed_checks[0].workflow_name == 'build'

        assert report.passed_checks[6].job[0] == "publish-checkov-dockerhub"
        assert report.passed_checks[6].triggers[0] == {'workflow_dispatch', 'push'}
        assert report.passed_checks[6].workflow_name == 'build'

    def test_runner_on_codeql_analysis(self):
        # given
        file_path = Path(__file__).parent.parent.parent / ".github/workflows/codeql-analysis.yml"
        file_dir = [str(file_path)]
        checks = ["CKV_GHA_1", "CKV_GHA_3"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert report.passed_checks[0].job[0] == "analyze"
        assert report.passed_checks[0].triggers[0] == {'push', 'schedule', 'pull_request', 'workflow_dispatch'}
        assert report.passed_checks[0].workflow_name == 'CodeQL'

    def test_runner_on_suspectcurl(self):
        # given
        file_path = Path(__file__).parent / "resources/.github/workflows/empty_jobs.yaml"
        file_dir = [str(file_path)]
        checks = ["CKV_GHA_6", "CKV_GHA_5"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert len(report.failed_checks) == 0
        assert len(report.passed_checks) == 0
        assert len(report.skipped_checks) == 0
        # empty_jobs.yaml is schema-invalid, so it is reported as a parsing
        # error instead of dropped silently
        assert len(report.parsing_errors) == 1

    def test_runner_on_permissions(self):
        # given
        file_path = Path(__file__).parent / "gha/.github/workflows/failed.yaml"
        file_dir = [str(file_path)]
        checks = ["CKV2_GHA_1"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert len(report.failed_checks) == 1
        assert report.failed_checks[0].file_line_range == [7, 8]
        assert len(report.passed_checks) == 0
        assert len(report.skipped_checks) == 0
        assert len(report.parsing_errors) == 0

    def test_runner_on_workflows_dispatch(self):
        # given
        file_path = Path(__file__).parent / "gha/.github/workflows/bad_workflows_dispatch.yaml"
        file_dir = [str(file_path)]
        checks = ["CKV_GHA_7"]

        # when
        report = Runner().run(
            files=file_dir, runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        assert len(report.failed_checks) == 1
        assert len(report.passed_checks) == 0
        assert len(report.skipped_checks) == 0
        assert len(report.parsing_errors) == 0


if __name__ == "__main__":
    unittest.main()
