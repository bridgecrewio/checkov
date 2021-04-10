import unittest

from dockerfile_parse import DockerfileParser

from checkov.common.models.enums import CheckResult
from checkov.dockerfile.checks.RootUser import check
from checkov.dockerfile.parser import dfp_group_by_instructions


class TestUserExists(unittest.TestCase):
    def test_failure(self):
        dfp = DockerfileParser()

        dfp.content = """
        FROM base
        USER root
        """

        conf = dfp_group_by_instructions(dfp)[0]
        scan_result = check.scan_entity_conf(conf)

        self.assertEqual(CheckResult.FAILED, scan_result[0])
        self.assertEqual("root", scan_result[1]["value"])

    def test_success(self):
        dfp = DockerfileParser()

        dfp.content = """
        FROM base
        USER root
        COPY test.sh /test.sh
        USER checkov
        """

        conf = dfp_group_by_instructions(dfp)[0]
        scan_result = check.scan_entity_conf(conf)

        self.assertEqual(CheckResult.PASSED, scan_result[0])
        self.assertEqual("checkov", scan_result[1]["value"])
