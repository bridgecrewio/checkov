import os
import unittest

from checkov.cloudformation import cfn_utils
from checkov.cloudformation.parser import parse
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRunnerValid(unittest.TestCase):
    def test_record_relative_path_with_relative_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path)

        runner = Runner()
        checks_allowlist = ["CKV_AWS_20"]
        report = runner.run(
            root_folder=dir_rel_path,
            external_checks_dir=None,
            runner_filter=RunnerFilter(
                framework="cloudformation", checks=checks_allowlist
            ),
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(
            len(all_checks) > 0
        )  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(
                record.repo_file_path, f"/{dir_rel_path}{record.file_path}"
            )

    def test_record_relative_path_with_abs_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources")

        dir_rel_path = os.path.relpath(scan_dir_path)

        dir_abs_path = os.path.abspath(scan_dir_path)

        runner = Runner()
        checks_allowlist = ["CKV_AWS_20"]
        report = runner.run(
            root_folder=dir_abs_path,
            external_checks_dir=None,
            runner_filter=RunnerFilter(
                framework="cloudformation", checks=checks_allowlist
            ),
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(
            len(all_checks) > 0
        )  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(
                record.repo_file_path, f"/{dir_rel_path}{record.file_path}"
            )

    def test_record_relative_path_with_relative_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "success.json")

        # this is the relative path to the file to scan (what would actually get passed to the -f arg)
        file_rel_path = os.path.relpath(scan_file_path)

        runner = Runner()
        checks_allowlist = ["CKV_AWS_20"]
        report = runner.run(
            root_folder=None,
            external_checks_dir=None,
            files=[file_rel_path],
            runner_filter=RunnerFilter(
                framework="cloudformation", checks=checks_allowlist
            ),
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(
            len(all_checks) > 0
        )  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f"/{file_rel_path}")

    def test_record_relative_path_with_abs_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "success.json")

        file_rel_path = os.path.relpath(scan_file_path)
        file_abs_path = os.path.abspath(scan_file_path)

        runner = Runner()
        checks_allowlist = ["CKV_AWS_20"]
        report = runner.run(
            root_folder=None,
            external_checks_dir=None,
            files=[file_abs_path],
            runner_filter=RunnerFilter(
                framework="cloudformation", checks=checks_allowlist
            ),
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(
            len(all_checks) > 0
        )  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f"/{file_rel_path}")

    def test_get_tags(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "tags.yaml")

        definitions, _ = parse(scan_file_path)

        resource_name = "DataBucket"
        resource = definitions["Resources"][resource_name]
        entity = {resource_name: resource}
        entity_tags = cfn_utils.get_resource_tags(entity)

        self.assertEqual(len(entity_tags), 4)
        tags = {
            "Simple": "Value",
            "Name": "${AWS::AccountId}-data",
            "Environment": "long-form-sub-${account}",
            "Account": "long-form-sub-${account}",
        }

        for name, value in tags.items():
            self.assertEqual(entity_tags[name], value)

        resource_name = "NoTags"
        resource = definitions["Resources"][resource_name]
        entity = {resource_name: resource}
        entity_tags = cfn_utils.get_resource_tags(entity)

        self.assertIsNone(entity_tags)

        "TerraformServerAutoScalingGroup"
        resource_name = "TerraformServerAutoScalingGroup"
        resource = definitions["Resources"][resource_name]
        entity = {resource_name: resource}
        entity_tags = cfn_utils.get_resource_tags(entity)

        self.assertIsNone(entity_tags)

        resource_name = "EKSClusterNodegroup"
        resource = definitions["Resources"][resource_name]
        entity = {resource_name: resource}
        entity_tags = cfn_utils.get_resource_tags(entity)

        self.assertEqual(len(entity_tags), 1)
        tags = {"Name": "{'Ref': 'ClusterName'}-EKS-{'Ref': 'NodeGroupName'}"}

        for name, value in tags.items():
            self.assertEqual(entity_tags[name], value)

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
