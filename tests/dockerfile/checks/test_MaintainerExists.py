import unittest

from dockerfile_parse import DockerfileParser

from checkov.common.models.enums import CheckResult
from checkov.dockerfile.checks.MaintainerExists import check
from checkov.dockerfile.parser import dfp_group_by_instructions


class TestMaintainerExists(unittest.TestCase):
    def test_failure(self):
        dfp = DockerfileParser()

        dfp.content = """
        From  base
        MAINTAINER checkov
        """

        conf = dfp_group_by_instructions(dfp)[0]
        scan_result = check.scan_entity_conf(conf)

        self.assertEqual((CheckResult.FAILED), scan_result[0])

    def test_success(self):
        dfp = DockerfileParser()

        dfp.content = """\
        From  base
        """

        conf = dfp_group_by_instructions(dfp)[0]
        scan_result = check.scan_entity_conf(conf)

        self.assertEqual((CheckResult.PASSED, None), scan_result)
