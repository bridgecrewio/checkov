import unittest

from dockerfile_parse import DockerfileParser

from checkov.common.models.enums import CheckResult
from checkov.dockerfile.checks.UpdateNotAlone import check
from checkov.dockerfile.parser import dfp_group_by_instructions


class TestUpdateNotAlone(unittest.TestCase):

    def test_failure(self):
        dfp = DockerfileParser()
        dfp.content = """\
        RUN apk update
        """
        conf = dfp_group_by_instructions(dfp)[0]
        scan_result = check.scan_entity_conf(conf['RUN'])
        self.assertEqual(CheckResult.FAILED, scan_result[0])

    def test_success(self):
        dfp = DockerfileParser()
        dfp.content = """\
        RUN apt-get update \
            && apt-get install -y --no-install-recommends foo \
            && echo gooo
        RUN apk update \
            && apk add --no-cache suuu looo
        RUN apk --update add moo
        """
        conf = dfp_group_by_instructions(dfp)[0]
        scan_result = check.scan_entity_conf(conf['RUN'])

        self.assertEqual(CheckResult.PASSED, scan_result[0])
