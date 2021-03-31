import unittest

from dockerfile_parse import DockerfileParser

from checkov.common.models.enums import CheckResult
from checkov.dockerfile.checks.AddExists import check
from checkov.dockerfile.parser import dfp_group_by_instructions


class TestAddExists(unittest.TestCase):

    def test_failure(self):
        dfp = DockerfileParser()
        dfp.content = """\
        From  base
        LABEL foo="bar baz"
        ADD http://example.com/package.zip /temp
        USER  me"""
        conf = dfp_group_by_instructions(dfp)[0]
        scan_result = check.scan_entity_conf(conf['ADD'])

        self.assertEqual((CheckResult.FAILED), scan_result[0])

