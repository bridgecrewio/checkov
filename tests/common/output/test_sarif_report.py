import unittest
import json
import jsonschema
import urllib.request

from checkov.common.models.enums import CheckResult
from checkov.common.output.report import Report
from checkov.common.output.record import Record


class TestSarifReport(unittest.TestCase):
    def test_valid_passing_valid_testcases(self):
        record1 = Record(
            check_id="CKV_AWS_21",
            check_name="Some Check",
            check_result={"result": CheckResult.FAILED},
            code_block=None,
            file_path="./s3.tf",
            file_line_range=[1, 3],
            resource="aws_s3_bucket.operations",
            evaluations=None,
            check_class=None,
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
        )
        record1.set_guideline("https://docs.bridgecrew.io/docs/s3_16-enable-versioning")

        record2 = Record(
            check_id="CKV_AWS_3",
            check_name="Ensure all data stored in the EBS is securely encrypted",
            check_result={"result": CheckResult.FAILED},
            code_block=None,
            file_path="./ec2.tf",
            file_line_range=[1, 3],
            resource="aws_ebs_volume.web_host_storage",
            evaluations=None,
            check_class=None,
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
        )
        record2.set_guideline("https://docs.bridgecrew.io/docs/general_7")

        r = Report("terraform")
        r.add_record(record=record1)
        r.add_record(record=record2)
        json_structure = r.get_sarif_json("")

        self.assertEqual(
            None,
            jsonschema.validate(instance=json_structure, schema=get_sarif_schema()),
        )

        json_structure["runs"][0]["tool"]["driver"]["version"] = "9.9.9"  # override the version

        self.assertDictEqual(
            json_structure,
            {
                "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
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
                                        "help": {"text": '"Some Check\nResource: aws_s3_bucket.operations"'},
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
                                            "text": '"Ensure all data stored in the EBS is securely encrypted\nResource: aws_ebs_volume.web_host_storage"'
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
                                            "artifactLocation": {"uri": "./s3.tf"},
                                            "region": {"startLine": 1, "endLine": 3},
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
                                            "artifactLocation": {"uri": "./ec2.tf"},
                                            "region": {"startLine": 1, "endLine": 3},
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
        record1 = Record(
            check_id="CKV_AWS_21",
            check_name="Some Check",
            check_result={"result": CheckResult.FAILED},
            code_block=None,
            file_path="./s3.tf",
            file_line_range=[1, 3],
            resource="aws_s3_bucket.operations",
            evaluations=None,
            check_class=None,
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
        )
        record1.set_guideline("")

        record2 = Record(
            check_id="CKV_AWS_111",
            check_name="Ensure IAM policies does not allow write access without constraints",
            check_result={"result": CheckResult.FAILED},
            code_block=None,
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
            code_block=None,
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
            code_block=None,
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
            code_block=None,
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
            code_block=None,
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
            code_block=None,
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
            code_block=None,
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
            code_block=None,
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
            code_block=None,
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
            code_block=None,
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
        json_structure = r.get_sarif_json("")
        print(json.dumps(json_structure))
        self.assertEqual(
            None,
            jsonschema.validate(instance=json_structure, schema=get_sarif_schema()),
        )
        self.assertFalse(are_duplicates_in_sarif_rules(json_structure))
        self.assertTrue(are_rule_indexes_correct_in_results(json_structure))
        self.assertTrue(are_rules_without_help_uri_correct(json_structure))


def get_sarif_schema():
    file_name, headers = urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Documents/CommitteeSpecifications/2.1.0/sarif-schema-2.1.0.json"
    )
    with open(file_name, "r") as file:
        schema = json.load(file)
    return schema


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
