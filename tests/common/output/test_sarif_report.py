from __future__ import annotations

import unittest
import json
from typing import Any

import jsonschema
import urllib.request

from checkov.common.models.enums import CheckResult
from checkov.common.output.report import Report
from checkov.common.output.record import Record
from checkov.common.output.sarif import Sarif


class TestSarifReport(unittest.TestCase):
    def test_valid_passing_valid_testcases(self):
        # given
        record1 = get_ckv_aws_21_record()
        record1.set_guideline("https://docs.bridgecrew.io/docs/s3_16-enable-versioning")

        record2 = Record(
            check_id="CKV_AWS_3",
            check_name="Ensure all data stored in the EBS is securely encrypted",
            check_result={"result": CheckResult.FAILED},
            code_block=[
                (5, 'resource aws_ebs_volume "web_host_storage" {\n'),
                (6, '  availability_zone = "us-west-2a"\n'),
                (7, "}\n"),
            ],
            file_path="./ec2.tf",
            file_line_range=[5, 7],
            resource="aws_ebs_volume.web_host_storage",
            evaluations=None,
            check_class=None,
            file_abs_path="/path to/ec2.tf",  # spaces should be handled correctly
            entity_tags={"tag1": "value1"},
        )
        record2.set_guideline("https://docs.bridgecrew.io/docs/general_7")

        r = Report("terraform")
        r.add_record(record=record1)
        r.add_record(record=record2)

        #  when
        sarif = Sarif(reports=[r], tool="")

        # then
        self.assertEqual(
            None,
            jsonschema.validate(instance=sarif.json, schema=get_sarif_schema()),
        )

        sarif.json["runs"][0]["tool"]["driver"]["version"] = "9.9.9"  # override the version

        self.assertDictEqual(
            sarif.json,
            {
                "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
                "version": "2.1.0",
                "runs": [
                    {
                        "tool": {
                            "driver": {
                                "name": "Bridgecrew",
                                "version": "9.9.9",
                                "informationUri": "https://docs.bridgecrew.io",
                                "rules": [
                                    {
                                        "id": "CKV_AWS_21",
                                        "name": "Some Check",
                                        "shortDescription": {"text": "Some Check"},
                                        "fullDescription": {"text": "Some Check"},
                                        "help": {"text": "Some Check\nResource: aws_s3_bucket.operations"},
                                        "helpUri": "https://docs.bridgecrew.io/docs/s3_16-enable-versioning",
                                        "defaultConfiguration": {"level": "error"},
                                    },
                                    {
                                        "id": "CKV_AWS_3",
                                        "name": "Ensure all data stored in the EBS is securely encrypted",
                                        "shortDescription": {
                                            "text": "Ensure all data stored in the EBS is securely encrypted"
                                        },
                                        "fullDescription": {
                                            "text": "Ensure all data stored in the EBS is securely encrypted"
                                        },
                                        "help": {
                                            "text": "Ensure all data stored in the EBS is securely encrypted\nResource: aws_ebs_volume.web_host_storage"
                                        },
                                        "helpUri": "https://docs.bridgecrew.io/docs/general_7",
                                        "defaultConfiguration": {"level": "error"},
                                    },
                                ],
                                "organization": "bridgecrew",
                            }
                        },
                        "results": [
                            {
                                "ruleId": "CKV_AWS_21",
                                "ruleIndex": 0,
                                "level": "error",
                                "attachments": [],
                                "message": {"text": "Some Check"},
                                "locations": [
                                    {
                                        "physicalLocation": {
                                            "artifactLocation": {"uri": "s3.tf"},
                                            "region": {
                                                "startLine": 1,
                                                "endLine": 3,
                                                "snippet": {
                                                    "text": 'resource aws_s3_bucket "operations" {\n  bucket = "example"\n}\n'
                                                },
                                            },
                                        }
                                    }
                                ],
                            },
                            {
                                "ruleId": "CKV_AWS_3",
                                "ruleIndex": 1,
                                "level": "error",
                                "attachments": [],
                                "message": {"text": "Ensure all data stored in the EBS is securely encrypted"},
                                "locations": [
                                    {
                                        "physicalLocation": {
                                            "artifactLocation": {"uri": "path%20to/ec2.tf"},
                                            "region": {
                                                "startLine": 5,
                                                "endLine": 7,
                                                "snippet": {
                                                    "text": 'resource aws_ebs_volume "web_host_storage" {\n  availability_zone = "us-west-2a"\n}\n'
                                                },
                                            },
                                        }
                                    }
                                ],
                            },
                        ],
                    }
                ],
            },
        )

    def test_multiple_instances_of_same_rule_do_not_break_schema(self):
        record1 = get_ckv_aws_21_record()
        record1.set_guideline("")

        record2 = Record(
            check_id="CKV_AWS_111",
            check_name="Ensure IAM policies does not allow write access without constraints",
            check_result={"result": CheckResult.FAILED},
            code_block=[(1, "some code")],
            file_path="./ec2.tf",
            file_line_range=[22, 25],
            resource="aws_ebs_volume.web_host_storage",
            evaluations=None,
            check_class=None,
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
        )
        record2.set_guideline("")

        record3 = Record(
            check_id="CKV2_AWS_3",
            check_name="Ensure GuardDuty is enabled to specific org/region",
            check_result={"result": CheckResult.FAILED},
            code_block=[(1, "some code")],
            file_path="./ec2.tf",
            file_line_range=[1, 3],
            resource="aws_ebs_volume.web_host_storage",
            evaluations=None,
            check_class=None,
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
        )
        record3.set_guideline("")

        record4 = Record(
            check_id="CKV2_AWS_3",
            check_name="Ensure GuardDuty is enabled to specific org/region",
            check_result={"result": CheckResult.FAILED},
            code_block=[(1, "some code")],
            file_path="./org.tf",
            file_line_range=[7, 10],
            resource="aws_ebs_volume.web_host_storage",
            evaluations=None,
            check_class=None,
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
        )
        record4.set_guideline("")

        record5 = Record(
            check_id="CKV2_AWS_3",
            check_name="Ensure GuardDuty is enabled to specific org/region",
            check_result={"result": CheckResult.FAILED},
            code_block=[(1, "some code")],
            file_path="./org.tf",
            file_line_range=[15, 20],
            resource="aws_ebs_volume.web_host_storage",
            evaluations=None,
            check_class=None,
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
        )
        record5.set_guideline("")

        record6 = Record(
            check_id="CKV2_AWS_3",
            check_name="Ensure GuardDuty is enabled to specific org/region",
            check_result={"result": CheckResult.FAILED},
            code_block=[(1, "some code")],
            file_path="./org.tf",
            file_line_range=[25, 28],
            resource="aws_ebs_volume.web_host_storage",
            evaluations=None,
            check_class=None,
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
        )
        record6.set_guideline("")

        record7 = Record(
            check_id="CKV_AWS_107",
            check_name="Ensure IAM policies does not allow credentials exposure",
            check_result={"result": CheckResult.FAILED},
            code_block=[(1, "some code")],
            file_path="./ec2.tf",
            file_line_range=[30, 35],
            resource="aws_ebs_volume.web_host_storage",
            evaluations=None,
            check_class=None,
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
        )
        record7.set_guideline("")

        record8 = Record(
            check_id="CKV_AWS_110",
            check_name="Ensure IAM policies does not allow privilege escalation",
            check_result={"result": CheckResult.FAILED},
            code_block=[(1, "some code")],
            file_path="./ec2.tf",
            file_line_range=[30, 35],
            resource="aws_ebs_volume.web_host_storage",
            evaluations=None,
            check_class=None,
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
        )
        record8.set_guideline("")

        record9 = Record(
            check_id="CKV_AWS_110",
            check_name="Ensure IAM policies does not allow privilege escalation",
            check_result={"result": CheckResult.FAILED},
            code_block=[(1, "some code")],
            file_path="./ec2.tf",
            file_line_range=[38, 40],
            resource="aws_ebs_volume.web_host_storage",
            evaluations=None,
            check_class=None,
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
        )
        record9.set_guideline("")

        # Record with non-empty guideline
        record10 = Record(
            check_id="CKV_AWS_23",
            check_name="Some Check",
            check_result={"result": CheckResult.FAILED},
            code_block=[(1, "some code")],
            file_path="./s3.tf",
            file_line_range=[1, 3],
            resource="aws_s3_bucket.operations",
            evaluations=None,
            check_class=None,
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
        )
        record10.set_guideline("https://example.com")

        # Record without guideline
        record11 = Record(
            check_id="CKV_AWS_24",
            check_name="Some Check",
            check_result={"result": CheckResult.FAILED},
            code_block=[(1, "some code")],
            file_path="./s3.tf",
            file_line_range=[1, 3],
            resource="aws_s3_bucket.operations",
            evaluations=None,
            check_class=None,
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
        )
        # No guideline here

        r = Report("terraform")
        r.add_record(record=record1)
        r.add_record(record=record2)
        r.add_record(record=record3)
        r.add_record(record=record4)
        r.add_record(record=record5)
        r.add_record(record=record6)
        r.add_record(record=record7)
        r.add_record(record=record8)
        r.add_record(record=record9)
        r.add_record(record=record10)
        r.add_record(record=record11)

        sarif = Sarif(reports=[r], tool="")

        self.assertEqual(
            None,
            jsonschema.validate(instance=sarif.json, schema=get_sarif_schema()),
        )
        self.assertFalse(are_duplicates_in_sarif_rules(sarif.json))
        self.assertTrue(are_rule_indexes_correct_in_results(sarif.json))
        self.assertTrue(are_rules_without_help_uri_correct(sarif.json))

    def test_non_url_guideline_link(self):
        # given
        record1 = get_ckv_aws_21_record()
        record1.set_guideline("some random text")

        r = Report("terraform")
        r.add_record(record=record1)

        #  when
        sarif = Sarif(reports=[r], tool="")

        # then
        self.assertEqual(
            None,
            jsonschema.validate(instance=sarif.json, schema=get_sarif_schema()),
        )

        sarif.json["runs"][0]["tool"]["driver"]["version"] = "9.9.9"  # override the version

        # sarif.json["runs"][0]["tool"]["driver"]["rules"][0] shouldn't include key "helpUri"
        self.assertDictEqual(
            sarif.json,
            {
                "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
                "version": "2.1.0",
                "runs": [
                    {
                        "tool": {
                            "driver": {
                                "name": "Bridgecrew",
                                "version": "9.9.9",
                                "informationUri": "https://docs.bridgecrew.io",
                                "rules": [
                                    {
                                        "id": "CKV_AWS_21",
                                        "name": "Some Check",
                                        "shortDescription": {"text": "Some Check"},
                                        "fullDescription": {"text": "Some Check"},
                                        "help": {"text": "Some Check\nResource: aws_s3_bucket.operations"},
                                        "defaultConfiguration": {"level": "error"},
                                    }
                                ],
                                "organization": "bridgecrew",
                            }
                        },
                        "results": [
                            {
                                "ruleId": "CKV_AWS_21",
                                "ruleIndex": 0,
                                "level": "error",
                                "attachments": [],
                                "message": {"text": "Some Check"},
                                "locations": [
                                    {
                                        "physicalLocation": {
                                            "artifactLocation": {"uri": "s3.tf"},
                                            "region": {
                                                "startLine": 1,
                                                "endLine": 3,
                                                "snippet": {
                                                    "text": 'resource aws_s3_bucket "operations" {\n  bucket = "example"\n}\n'
                                                },
                                            },
                                        }
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
        )


def get_sarif_schema() -> dict[str, Any]:
    file_name, headers = urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json"
    )
    with open(file_name, "r") as file:
        schema = json.load(file)
    return schema


def get_ckv_aws_21_record() -> Record:
    return Record(
        check_id="CKV_AWS_21",
        check_name="Some Check",
        check_result={"result": CheckResult.FAILED},
        code_block=[
            (1, 'resource aws_s3_bucket "operations" {\n'),
            (2, '  bucket = "example"\n'),
            (3, "}\n"),
        ],
        file_path="./s3.tf",
        file_line_range=[1, 3],
        resource="aws_s3_bucket.operations",
        evaluations=None,
        check_class=None,
        file_abs_path="./s3.tf",
        entity_tags={"tag1": "value1"},
    )

def are_duplicates_in_sarif_rules(sarif_json) -> bool:
    rules = sarif_json["runs"][0]["tool"]["driver"]["rules"]
    ruleset = set()
    for rule in rules:
        ruleset.add(rule["id"])

    return len(rules) != len(ruleset)


def are_rule_indexes_correct_in_results(sarif_json) -> bool:
    rules = sarif_json["runs"][0]["tool"]["driver"]["rules"]
    results = sarif_json["runs"][0]["results"]
    for rule in rules:
        for result in results:
            if result["ruleId"] == rule["id"]:
                if result["ruleIndex"] != rules.index(rule) or result["ruleIndex"] > len(rules):
                    return False
    return True


def are_rules_without_help_uri_correct(sarif_json) -> bool:
    rules = sarif_json["runs"][0]["tool"]["driver"]["rules"]
    results = sarif_json["runs"][0]["results"]
    for rule in rules:
        if "helpUri" in rule:
            if rule["helpUri"] is None or rule["helpUri"] == "":
                return False
    return True


if __name__ == "__main__":
    unittest.main()
