import time
import unittest
from pathlib import Path

from detect_secrets.util.code_snippet import CodeSnippet
from detect_secrets.util.filetype import FileType

from checkov.runner_filter import RunnerFilter
from checkov.secrets.plugins.entropy_keyword_combinator import EntropyKeywordCombinator
from checkov.secrets.plugins.entropy_keyword_combinator import REGEX_VALUE_KEYWORD_BY_FILETYPE
from checkov.secrets.plugins.entropy_keyword_combinator import REGEX_VALUE_SECRET_BY_FILETYPE
from checkov.secrets.runner import Runner
from tests.secrets.utils_for_test import _filter_reports_for_incident_ids


class TestCombinatorPluginMultilineYml(unittest.TestCase):
    def setUp(self) -> None:
        self.plugin = EntropyKeywordCombinator()

    def test_keyword_in_value_pair(self):
        # first line is keyword, next line (underneath) is password
        context = CodeSnippet(
            snippet=[
                'name: "TEST_SOMETHING"',
                'value: "not-a-real-password"',
                'name: "TEST_PASSWORD_1"',
                'value: "Zmlyc3Rfc2VjcmV0X2hlcmVfd2hvYV9tdWx0aWxsaW5lX3Nob3VsZF93b3JrXzE=="',
                'name: "TEST_PASSWORD_2"',
                'value: "Zmlyc3Rfc2VjcmV0MjIyMjIyX2hlcmVfd2hvYV9tdWx0aWxsaW5lX3Nob3VsZF93b3JrXzI"',
                'name: "TEST_PASSWORD_3"',
                'value: "Z2FlYnJzZGhqa2p1aGdmZHN3cXdnaHluanVraWxvaWtqdWh5Z3RyZmVkd3NlcnR5dWk4bw"',
                'name: "TEST_PASSWORD_4"',
                'value: "Z2FlYnJzZGhqa2p1aGdmZHN3cXdnaHluanVraWxvaWtqdWh5Z3RyZmVkd3NlcnR5dWk4bw"',
                'name: "TEST_PASSWORD_BASE64_LONG_1"'
            ],
            start_line=112,
            target_index=5
        )
        raw_context = CodeSnippet(
            snippet=[
                '        - name: TEST_SOMETHING\n',
                '          value: not-a-real-password\n',
                '        - name: TEST_PASSWORD_1\n',
                '          value: Zmlyc3Rfc2VjcmV0X2hlcmVfd2hvYV9tdWx0aWxsaW5lX3Nob3VsZF93b3JrXzE==\n',
                '        - name: TEST_PASSWORD_2\n',
                '          value: Zmlyc3Rfc2VjcmV0MjIyMjIyX2hlcmVfd2hvYV9tdWx0aWxsaW5lX3Nob3VsZF93b3JrXzI\n',
                '        - name: TEST_PASSWORD_3\n',
                '          value: Z2FlYnJzZGhqa2p1aGdmZHN3cXdnaHluanVraWxvaWtqdWh5Z3RyZmVkd3NlcnR5dWk4bw\n',
                '        - name: TEST_PASSWORD_4\n',
                '          value: Z2FlYnJzZGhqa2p1aGdmZHN3cXdnaHluanVraWxvaWtqdWh5Z3RyZmVkd3NlcnR5dWk4bw\n',
                '        - name: TEST_PASSWORD_LONG\n'
            ],
            start_line=112,
            target_index=5
        )
        res = self.plugin.analyze_line(
            filename="test.yml",
            line='value: "Zmlyc3Rfc2VjcmV0MjIyMjIyX2hlcmVfd2hvYV9tdWx0aWxsaW5lX3Nob3VsZF93b3JrXzI"',
            line_number=118,
            context=context,
            raw_context=raw_context
        )
        expected_secret_value = 'Zmlyc3Rfc2VjcmV0MjIyMjIyX2hlcmVfd2hvYV9tdWx0aWxsaW5lX3Nob3VsZF93b3JrXzI'
        assert res
        po_secret = res.pop()
        assert expected_secret_value == po_secret.secret_value
        assert po_secret.is_multiline is True

    def test_keyword_in_value_pair2(self):
        # first line is password, next line underneath is keyword
        context = CodeSnippet(
            snippet=[
                '',
                '',
                '',
                '',
                '',
                'value: "Zo5Zhexnf9TUggdn+zBKGEkmUUvuKzVN+/fKPaMBA4zVyef4irH5H5YfwoC4IqAX0DNoMD12yIF67nIdIMg13atW4WM33eNMfXlE"',
                'name: "TEST_PASSWORD_1"',
                'name1: "TEST_PASSWORD_2"',
                'value1: "1Vab3xejyUlh89P6tUJNXgO4t07DzmomF4tPBwTbwt+sjXHg3G0MPMRpH/I2ho4gS5H3AKJkvJZj87V7/Qnp/rHdbMVYK1F0BX35"',
                'name: "TEST_PASSWORD_3"',
                'value: "PtpfIZR+zZGPUWUYvLojqylVeEg63CBYN0FpGJ4yuH+9YxZZe8Uq7drEoTSfL64kElPEnVJk+H7SZr+wBoxN5qDWsbDmmUS2H76h"'
            ],
            start_line=5,
            target_index=5
        )
        raw_context = CodeSnippet(
            snippet=[
                '#\n',
                 '#\n',
                 'spec:\n',
                 '  - name: SOME_NAME\n',
                 '    value: some_value\n',
                 '    value: Zo5Zhexnf9TUggdn+zBKGEkmUUvuKzVN+/fKPaMBA4zVyef4irH5H5YfwoC4IqAX0DNoMD12yIF67nIdIMg13atW4WM33eNMfXlE\n',
                 '    name: TEST_PASSWORD_1\n',
                 '  - name1: TEST_PASSWORD_2\n',
                 '    value1: 1Vab3xejyUlh89P6tUJNXgO4t07DzmomF4tPBwTbwt+sjXHg3G0MPMRpH/I2ho4gS5H3AKJkvJZj87V7/Qnp/rHdbMVYK1F0BX35\n',
                 '    name: TEST_PASSWORD_3\n',
                 '    value: PtpfIZR+zZGPUWUYvLojqylVeEg63CBYN0FpGJ4yuH+9YxZZe8Uq7drEoTSfL64kElPEnVJk+H7SZr+wBoxN5qDWsbDmmUS2H76h\n'
            ],
            start_line=5,
            target_index=5
        )
        res = self.plugin.analyze_line(
            filename="test.yml",
            line='value: "Zo5Zhexnf9TUggdn+zBKGEkmUUvuKzVN+/fKPaMBA4zVyef4irH5H5YfwoC4IqAX0DNoMD12yIF67nIdIMg13atW4WM33eNMfXlE"',
            line_number=11,
            context=context,
            raw_context=raw_context
        )

        expected_secret_value = 'Zo5Zhexnf9TUggdn+zBKGEkmUUvuKzVN+/fKPaMBA4zVyef4irH5H5YfwoC4IqAX0DNoMD12yIF67nIdIMg13atW4WM33eNMfXlE'
        assert res
        po_secret = res.pop()
        assert expected_secret_value == po_secret.secret_value
        assert po_secret.is_multiline is True

    def test_keyword_in_value_pair_long_password(self):
        # first line is keyword, next line (underneath) is a long multiline password
        context = CodeSnippet(
            snippet=[
                'name: "TEST_PASSWORD_3"',
                'value: "PtpfIZR+zZGPUWUYvLojqylVeEg63CBYN0FpGJ4yuH+9YxZZe8Uq7drEoTSfL64kElPEnVJk+H7SZr+wBoxN5qDWsbDmmUS2H76h"',
                'name: "TEST_PASSWORD_4"',
                'value: "emDJTiv6H/hP6I8Tmr5+kUdpBIQDrXMwFO7AkmbwROf3rM6uNToJlIJW7H5ApfPmSGU0oWBwflV6Cd9pPu5nEvgxt4YMHZ0SQ85z"',
                'name: "TEST_PASSWORD_LONG_1"',
                'value: "m9+1ONt6FdpnByhlaKDwZ/jjA5gaPzrKY9q5G8cr6kjn092ogigwEOGGryjDqq/NkX1DnKGGG7iduJUJ48+Rv0tgpdVAxwLQuiszRnssmi2ck/Zf1iDFlNQtiE8rvXE6OTCsb6mrpyItLOVnEwsRSpggyRa3KLSuiguiZsK5KyXQ6BsiAclpLvz6QFBQoQkZNxownQrqgLwVwkK1gW0/EEm0m1ylz20ZeLgYO6tRSvKDW0lrgAI7g60F7/eJGv1UqQlxK58T+7u1UX/K11Q69e9jJE+LkQ932eY37U70oVbBVchHwSFKUoffernEaG9XP1tyEpIptPqVpcS2BMpktoR1p1yyWuxC5GsPc2RlPQzEbs3n5lPPnC/uEVu7/cJENSw5+9DzigiHYPz1Cq/p5HedIl5ysn2U2VFgHWekGBYin6ytfmF2Sx+hYqeRd6RcxyU434CXspWQqc330sp9q7vwPQHNecBrvG2Iy7mqVSvaJDnkZ8AN"',
                'name: "TEST_PASSWORD_no_password"',
                'value: "RandomP@ssw0rd"'
            ],
            start_line=7,
            target_index=5
        )
        raw_context = CodeSnippet(
            snippet=[
                '  - name: TEST_PASSWORD_3\n',
                '    value: PtpfIZR+zZGPUWUYvLojqylVeEg63CBYN0FpGJ4yuH+9YxZZe8Uq7drEoTSfL64kElPEnVJk+H7SZr+wBoxN5qDWsbDmmUS2H76h\n',
                '  - name: TEST_PASSWORD_4\n',
                '    value: emDJTiv6H/hP6I8Tmr5+kUdpBIQDrXMwFO7AkmbwROf3rM6uNToJlIJW7H5ApfPmSGU0oWBwflV6Cd9pPu5nEvgxt4YMHZ0SQ85z\n',
                '  - name: TEST_PASSWORD_LONG_1\n',
                '    value: m9+1ONt6FdpnByhlaKDwZ/jjA5gaPzrKY9q5G8cr6kjn092ogigwEOGGryjDqq/NkX1DnKGGG7iduJUJ48+Rv0tgpdVAxwLQuiszRnssmi2ck/Zf1iDFlNQtiE8rvXE6OTCsb6mrpyItLOVnEwsRSpggyRa3KLSuiguiZsK5KyXQ6BsiAclpLvz6QFBQoQkZNxownQrqgLwVwkK1gW0/EEm0m1ylz20ZeLgYO6tRSvKDW0lrgAI7g60F7/eJGv1UqQlxK58T+7u1UX/K11Q69e9jJE+LkQ932eY37U70oVbBVchHwSFKUoffernEaG9XP1tyEpIptPqVpcS2BMpktoR1p1yyWuxC5GsPc2RlPQzEbs3n5lPPnC/uEVu7/cJENSw5+9DzigiHYPz1Cq/p5HedIl5ysn2U2VFgHWekGBYin6ytfmF2Sx+hYqeRd6RcxyU434CXspWQqc330sp9q7vwPQHNecBrvG2Iy7mqVSvaJDnkZ8AN\n',
                '  - name: TEST_PASSWORD_no_password\n',
                '    value: RandomP@ssw0rd\n'
            ],
            start_line=112,
            target_index=5
        )
        res = self.plugin.analyze_line(
            filename="test.yml",
            line='value: "Zmlyc3Rfc2VjcmV0MjIyMjIyX2hlcmVfd2hvYV9tdWx0aWxsaW5lX3Nob3VsZF93b3JrXzI"',
            line_number=118,
            context=context,
            raw_context=raw_context
        )
        expected_secret_value = 'm9+1ONt6FdpnByhlaKDwZ/jjA5gaPzrKY9q5G8cr6kjn092ogigwEOGGryjDqq/NkX1DnKGGG7iduJUJ48+Rv0tgpdVAxwLQuiszRnssmi2ck/Zf1iDFlNQtiE8rvXE6OTCsb6mrpyItLOVnEwsRSpggyRa3KLSuiguiZsK5KyXQ6BsiAclpLvz6QFBQoQkZNxownQrqgLwVwkK1gW0/EEm0m1ylz20ZeLgYO6tRSvKDW0lrgAI7g60F7/eJGv1UqQlxK58T+7u1UX/K11Q69e9jJE+LkQ932eY37U70oVbBVchHwSFKUoffernEaG9XP1tyEpIptPqVpcS2BMpktoR1p1yyWuxC5GsPc2RlPQzEbs3n5lPPnC/uEVu7/cJENSw5+9DzigiHYPz1Cq/p5HedIl5ysn2U2VFgHWekGBYin6ytfmF2Sx+hYqeRd6RcxyU434CXspWQqc330sp9q7vwPQHNecBrvG2Iy7mqVSvaJDnkZ8AN'
        assert res
        po_secret = res.pop()
        assert expected_secret_value == po_secret.secret_value
        assert po_secret.is_multiline is True

    def test_multiline_keyword_password_report(self):
        test_file_path = Path(__file__).parent / "yml_multiline/test-multiline-secrets.yml"

        report = Runner().run(
            root_folder=None, files=[str(test_file_path)], runner_filter=RunnerFilter(framework=['secrets'])
        )
        self.assertEqual(len(report.failed_checks), 5)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])

    def test_non_multiline_pair_time_limit_creating_report(self):
        # given
        test_files = [str(Path(__file__).parent / "yml_multiline/pomerium_compose.yml")]
        runner = Runner()
        runner_filter = RunnerFilter(framework=['secrets'])

        # when
        start_time = time.time()
        report = runner.run(root_folder=None, files=test_files, runner_filter=runner_filter)
        end_time = time.time()

        # then
        assert end_time-start_time < 1  # assert the time limit is not too long for parsing long lines.
        interesting_failed_checks = _filter_reports_for_incident_ids(report.failed_checks,
                                                                     ["CKV_SECRET_4", "CKV_SECRET_6", "CKV_SECRET_13"])
        self.assertEqual(len(interesting_failed_checks), 4)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])

    def test_regex_keyword_in_value(self):
        # the regex only finds the relevant part from the keyword that matches,
        # the whole keyword is not found by the current regex.

        examples = [
            # (line, keyword)
            (
                "        - name: TEST_PASSWORD_1\n",
                "PASSWORD",
            ),
            (
                "          name: TEST_PASSWORD_1\n",
                "PASSWORD",
            )
        ]

        keyword_value_regex_to_group = REGEX_VALUE_KEYWORD_BY_FILETYPE.get(FileType.YAML)
        value_regex, group_number = list(keyword_value_regex_to_group.items())[0]
        for line, secret in examples:
            match = value_regex.search(line).group(group_number)
            assert match == secret

    def test_regex_secret_in_value(self):
        examples = [
            # (line, secret)
            (
                "         - value: Zmlyc3Rfc2VjcmV0X2hlcmVfd2hvYV9tdWx0aWxsaW5lX3Nob3VsZF93b3JrXzE==\n",
                "Zmlyc3Rfc2VjcmV0X2hlcmVfd2hvYV9tdWx0aWxsaW5lX3Nob3VsZF93b3JrXzE==\n",
            ),
            (
                "           value: Zmlyc3Rfc2VjcmV0X2hlcmVfd2hvYV9tdWx0aWxsaW5lX3Nob3VsZF93b3JrXzE==\n",
                "Zmlyc3Rfc2VjcmV0X2hlcmVfd2hvYV9tdWx0aWxsaW5lX3Nob3VsZF93b3JrXzE==\n",
            ),
        ]

        secret_value_regex_to_group = REGEX_VALUE_SECRET_BY_FILETYPE.get(FileType.YAML)
        value_regex, group_number = list(secret_value_regex_to_group.items())[0]
        for line, secret in examples:
            match = value_regex.search(line).group(group_number)
            assert match == secret
