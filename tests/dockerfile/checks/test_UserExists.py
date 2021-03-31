import unittest

from dockerfile_parse import DockerfileParser

from checkov.common.models.enums import CheckResult
from checkov.dockerfile.checks.UserExists import check
from checkov.dockerfile.parser import dfp_group_by_instructions


class TestUserExists(unittest.TestCase):

    def test_failure(self):
        dfp = DockerfileParser()
        dfp.content = """\
        From  base
        LABEL foo="bar baz"
        """
        conf = dfp_group_by_instructions(dfp)[0]
        scan_result = check.scan_entity_conf(conf)
        self.assertEqual((CheckResult.FAILED,None), scan_result)

    def test_success(self):
        dfp = DockerfileParser()
        dfp.content = """\
        From  base
        LABEL foo="bar baz"
        USER  me
        HEALTHCHECK CMD curl --fail http://localhost:3000 || exit 1 
        """
        conf = dfp_group_by_instructions(dfp)[0]
        scan_result = check.scan_entity_conf(conf)
        self.assertEqual(CheckResult.PASSED, scan_result[0])
