import os
import unittest
from pathlib import Path

from detect_secrets.util.code_snippet import CodeSnippet
from detect_secrets.util.filetype import FileType

from checkov.runner_filter import RunnerFilter
from checkov.secrets.plugins.entropy_keyword_combinator import EntropyKeywordCombinator
from checkov.secrets.plugins.entropy_keyword_combinator import REGEX_VALUE_KEYWORD_BY_FILETYPE
from checkov.secrets.plugins.entropy_keyword_combinator import REGEX_VALUE_SECRET_BY_FILETYPE
from checkov.secrets.runner import Runner


class TestCombinatorPlugin(unittest.TestCase):
    def setUp(self) -> None:
        self.plugin = EntropyKeywordCombinator()

    def test_positive_value(self):
        result = self.plugin.analyze_line("mock.tf", 'api_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMAAAKEY"', 5)
        self.assertEqual(1, len(result))
        secret = result.pop()
        self.assertEqual("Base64 High Entropy String", secret.type)
        self.assertEqual("c00f1a6e4b20aa64691d50781b810756d6254b8e", secret.secret_hash)

    def test_negative_keyword_value(self):
        result = self.plugin.analyze_line("mock.tf", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMAAAKEY", 5)
        self.assertEqual(0, len(result))

    def test_negative_entropy_value(self):
        result = self.plugin.analyze_line("mock.tf", "api_key = var.api_key", 5)
        self.assertEqual(0, len(result))

    def test_popular_kubernetes_manifest_password(self):
        result = self.plugin.analyze_line("mock.yaml", 'pwd: "correcthorsebatterystaple"', 5)
        self.assertEqual(1, len(result))
        secret = result.pop()
        self.assertEqual("Base64 High Entropy String", secret.type)
        self.assertEqual("bfd3617727eab0e800e62a776c76381defbc4145", secret.secret_hash)

    def test_no_false_positive_py(self):
        # combinator plugin should ignore source code files
        result = self.plugin.analyze_line("main.py", 'api_key = "7T)G#dl5}c=T>kf$G3Bon^!R?kzF00"', 1)
        self.assertEqual(0, len(result))

    def test_no_false_positive_yml_1(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_name = "secret-no-false-positive.yml"
        valid_file_path = current_dir + f"/resources/cfn/{file_name}"
        with open(file=valid_file_path) as f:
            for i, line in enumerate(f.readlines()):
                result = self.plugin.analyze_line(file_name, line, i)
                self.assertEqual(0, len(result))

    def test_are_lines_same_indentation_yml(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_name = "secret.yml"
        valid_file_path = current_dir + f"/resources/cfn/{file_name}"

        result = {0: True, 1: False, 2: False, 3: False, 4: False, 5: True, 6: False, 7: True,
                  8: True, 9: True, 10: True, 11: False, 12: False, 13: False, 14: False, 15: False,
                  16: True, 17: False, 18: False, 19: True, 20: True, 21: True}
        with open(file=valid_file_path) as f:
            lines = f.readlines()
            # assert len(result) == len(lines)-1
            for i in range(len(lines)-1):
                result[i] = self.plugin.lines_same_indentation(lines[i], lines[i+1])

        assert result

    def test_line_is_comment_yml(self):
        examples = [
            (True,  "# comment"),
            (True,  "     # also comment"),
            (True,  "// nice comment here"),
            (True,  "//and nice comment here2"),
            (True,  "      // commenting with checkov and having fun"),
            (False, "var: a  //this is not a comment"),
            (False, "var: not a comment # comment"),
            (False, "  - var: a"),
            (False, "var: "),
        ]

        for ans, line in examples:
            assert ans == self.plugin.line_is_comment(line)

    def test_keyword_in_value_pair_yml(self):
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
        assert expected_secret_value == res.pop().secret_value

    def test_keyword_in_value_pair_yml2(self):
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
        assert expected_secret_value == res.pop().secret_value

    def test_keyword_in_value_pair_long_password_yml(self):
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
        assert expected_secret_value == res.pop().secret_value

    def test_multiline_keyword_password_report(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_name = "test-multiline-secrets.yml"
        valid_file_path = current_dir + f"/yml_multiline/{file_name}"

        runner = Runner()
        report = runner.run(root_folder=None, files=[valid_file_path], runner_filter=RunnerFilter(framework=['secrets']))
        self.assertEqual(len(report.failed_checks), 5)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])

    def test_non_multiline_keyword_password_report(self):
        # given
        test_file_path = Path(__file__).parent / "yml_multiline/pomerium_compose.yml"

        # when
        report = Runner().run(
            root_folder=None, files=[str(test_file_path)], runner_filter=RunnerFilter(framework=['secrets'])
        )

        # then
        self.assertEqual(len(report.failed_checks), 4)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])

    def test_regex_keyword_in_value_yml(self):
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
        value_regex, group_number = keyword_value_regex_to_group.popitem()
        for line, secret in examples:
            match = value_regex.search(line).group(group_number)
            assert match == secret

    def test_regex_secret_in_value_yml(self):
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
        value_regex, group_number = secret_value_regex_to_group.popitem()
        for line, secret in examples:
            match = value_regex.search(line).group(group_number)
            assert match == secret
