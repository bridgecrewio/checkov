import unittest

from dockerfile_parse import DockerfileParser

from checkov.common.models.enums import CheckResult
from checkov.dockerfile.checks.ReferenceLatestTag import check
from checkov.dockerfile.parser import dfp_group_by_instructions


class TestMaintainerExists(unittest.TestCase):
    def test_failure_default_version_tag(self):
        dfp = DockerfileParser()

        dfp.content = """
        FROM alpine
        """

        conf = dfp_group_by_instructions(dfp)[0]
        scan_result = check.scan_entity_conf(conf)

        self.assertEqual(CheckResult.FAILED, scan_result[0])
        self.assertEqual("alpine", scan_result[1]["value"])

    def test_failure_latest_version_tag(self):
        dfp = DockerfileParser()

        dfp.content = """
        FROM alpine:latest
        """

        conf = dfp_group_by_instructions(dfp)[0]
        scan_result = check.scan_entity_conf(conf)

        self.assertEqual(CheckResult.FAILED, scan_result[0])
        self.assertEqual("alpine:latest", scan_result[1]["value"])

    def test_success(self):
        dfp = DockerfileParser()

        dfp.content = """
        FROM alpine:3
        """

        conf = dfp_group_by_instructions(dfp)[0]
        scan_result = check.scan_entity_conf(conf)

        self.assertEqual((CheckResult.PASSED, None), scan_result)

    def test_success_multi_stage(self):
        dfp = DockerfileParser()

        dfp.content = """
        FROM alpine:3 as base
        COPY test.sh /test.sh
        
        FROM base
        LABEL maintainer=checkov
        """

        conf = dfp_group_by_instructions(dfp)[0]
        scan_result = check.scan_entity_conf(conf)

        self.assertEqual((CheckResult.PASSED, None), scan_result)
