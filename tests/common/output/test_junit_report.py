import argparse
import unittest
import xml
import xml.etree.ElementTree as ET
from pathlib import Path

from checkov.common.models.enums import CheckResult
from checkov.common.output.report import Report
from checkov.common.output.record import Record
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner as TerrafomrRunner


class TestJunitReport(unittest.TestCase):
    def test_valid_passing_valid_testcases(self):
        record1 = Record(
            check_id="CKV_AWS_21",
            check_name="Some Check",
            check_result={"result": CheckResult.FAILED},
            code_block=[],
            file_path="./s3.tf",
            file_line_range=[1, 3],
            resource="aws_s3_bucket.operations",
            evaluations=None,
            check_class="",
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
        )
        record2 = Record(
            check_id="CKV_AWS_3",
            check_name="Ensure all data stored in the EBS is securely encrypted",
            check_result={"result": CheckResult.FAILED},
            code_block=[],
            file_path="./ec2.tf",
            file_line_range=[1, 3],
            resource="aws_ebs_volume.web_host_storage",
            evaluations=None,
            check_class="",
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
        )

        r = Report("terraform")
        r.add_record(record=record1)
        r.add_record(record=record2)
        ts = r.get_test_suite()
        xml_string = r.get_junit_xml_string([ts])
        root = ET.fromstring(xml_string)
        self.assertEqual(root.attrib["errors"], "0")

    def test_get_junit_xml_string_with_terraform(self):
        # given
        test_file = Path(__file__).parent / "fixtures/main.tf"
        checks = ["CKV_AWS_18", "CKV_AWS_19", "CKV_AWS_21"]  # 1 pass, 1 fail, 1 skip
        config = argparse.Namespace(file="fixtures/main.tf", framework=["terraform"])
        report = TerrafomrRunner().run(
            root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=checks)
        )

        # remove guideline from failed checks, if they were fetched before
        for check in report.failed_checks:
            check.guideline = None

        # then
        properties = Report.create_test_suite_properties_block(config=config)
        test_suite = report.get_test_suite(properties=properties)
        xml_string = Report.get_junit_xml_string([test_suite])

        # then
        assert (
            xml.dom.minidom.parseString(xml_string).toprettyxml()
            == xml.dom.minidom.parseString(
                "".join(
                    [
                        '<?xml version="1.0" ?>\n',
                        '<testsuites disabled="0" errors="0" failures="1" tests="2" time="0.0">\n',
                        '\t<testsuite disabled="0" errors="0" failures="1" name="terraform scan" skipped="1" tests="2" time="0">\n',
                        "\t\t<properties>\n",
                        '\t\t\t<property name="file" value="fixtures/main.tf"/>\n',
                        '\t\t\t<property name="framework" value="[\'terraform\']"/>\n',
                        "\t\t</properties>\n",
                        '\t\t<testcase name="[NONE][CKV_AWS_18] Ensure the S3 bucket has access logging enabled" classname="/main.tf.aws_s3_bucket.destination" file="/main.tf">\n',
                        '\t\t\t<failure type="failure" message="Ensure the S3 bucket has access logging enabled">\n',
                        "Resource: aws_s3_bucket.destination\n",
                        "File: /main.tf: 1-8\n",
                        "Guideline: None\n",
                        "\n",
                        "\t\t1 | resource &quot;aws_s3_bucket&quot; &quot;destination&quot; {\n",
                        "\t\t2 |   # checkov:skip=CKV_AWS_19: no encryption needed\n",
                        "\t\t3 |   bucket = &quot;tf-test-bucket-destination-12345&quot;\n",
                        "\t\t4 |   acl = var.acl\n",
                        "\t\t5 |   versioning {\n",
                        "\t\t6 |     enabled = var.is_enabled\n",
                        "\t\t7 |   }\n",
                        "\t\t8 | }</failure>\n",
                        "\t\t</testcase>\n",
                        '\t\t<testcase name="[NONE][CKV_AWS_19] Ensure all data stored in the S3 bucket is securely encrypted at rest" classname="/main.tf.aws_s3_bucket.destination" file="/main.tf">\n',
                        '\t\t\t<skipped type="skipped" message=" no encryption needed"/>\n',
                        "\t\t</testcase>\n",
                        "\t</testsuite>\n",
                        "</testsuites>\n",
                    ]
                )
            ).toprettyxml()
        )


if __name__ == "__main__":
    unittest.main()
