import os
import pathlib
import yaml

from checkov.sast.checks_infra.check_parser.parser_v02 import SastCheckParserV02

cur_dir = pathlib.Path(__file__).parent.resolve()
policy_dir = os.path.join(cur_dir / 'checks' / 'v02')
parser = SastCheckParserV02()

def test_metadata_parsing():
    with open(os.path.join(policy_dir, 'python_simple_pattern.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1',
            'message': 'module setting superuser port',
            'severity': 'INFO',
            'languages': ['python'],
            'metadata': {
                'name': 'superuser port',
                'cwe': 'CWE-289: Authentication Bypass by Alternate Name',
                'owasp': 'OWASP 1: some owasp'
            },
            'pattern': 'set_port($ARG)'
        }


def test_multiline_pattern_parsing():
    with open(os.path.join(policy_dir, 'python_multiline_pattern.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1',
            'message': 'module setting superuser port',
            'severity': 'INFO',
            'languages': ['python'],
            'metadata': {
                'name': 'superuser port',
                'cwe': 'CWE-289: Authentication Bypass by Alternate Name',
                'owasp': 'OWASP 1: some owasp'
            },
            'pattern': 'def $FUNC(...):\n  ...\n  return'
        }


def test_pattern_not_parsing():
    with open(os.path.join(policy_dir, 'python_pattern_not.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1',
            'message': 'module setting superuser port',
            'severity': 'INFO',
            'languages': ['python'],
            'metadata': {
                'name': 'superuser port',
                'cwe': 'CWE-289: Authentication Bypass by Alternate Name',
                'owasp': 'OWASP 1: some owasp'
            },
            'patterns': [
                {'pattern-not': 'db_query(call())'},
                {'pattern': 'db_query($ARG)'}
            ]

        }


def test_pattern_either_1_parsing():
    with open(os.path.join(policy_dir, 'python_simple_or_1.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1',
            'message': 'some guidelines',
            'severity': 'INFO',
            'languages': ['python'],
            'metadata': {
                'name': 'check name'
            },
            'pattern-either': [
                {'pattern': 'set_port_1($ARG)'},
                {'pattern': 'set_port_2($ARG)'}]
        }

def test_pattern_either_2_parsing():
    with open(os.path.join(policy_dir, 'python_simple_or_2.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1',
            'message': 'some guidelines',
            'severity': 'INFO',
            'languages': ['python'],
            'metadata': {
                'name': 'check name'
            },
            'pattern-either': [
                {'pattern': 'set_port_1($ARG)'},
                {'pattern': 'set_port_2($ARG)'}]
        }


def test_explicit_patterns_parsing():
    with open(os.path.join(policy_dir, 'python_simple_and.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1', 'message': 'some guidelines', 'severity': 'INFO', 'languages': ['python'], 'metadata': {
                'name': 'check name'},
            'patterns': [
                {'pattern': 'set_port_1($ARG)'},
                {'pattern-regex': 'ABC'}]
        }


def test_pattern_not_regex_parsing():
    with open(os.path.join(policy_dir, 'python_simple_not_regex.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1', 'message': 'some guidelines', 'severity': 'INFO', 'languages': ['python'], 'metadata': {
                'name': 'check name'},
            'patterns': [
                {'pattern-not-regex': '^.*(RSA)/.*'},
                {'pattern': 'set_port($ARG)'}
            ]
        }


def test_pattern_inside_parsing():
    with open(os.path.join(policy_dir, 'python_simple_within.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1', 'message': 'some guidelines', 'severity': 'INFO', 'languages': ['python'], 'metadata': {
                'name': 'check name'},
            'patterns': [
                {'pattern-inside': 'danger(set_port(1))'},
                {'pattern': 'set_port(1)'}]
        }


def test_pattern_not_inside_parsing():
    with open(os.path.join(policy_dir, 'python_simple_not_within.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1', 'message': 'some guidelines', 'severity': 'INFO', 'languages': ['python'], 'metadata': {
                'name': 'check name'},
            'patterns': [
                {'pattern-not-inside': 'danger(set_port(1))'},
                {'pattern': 'set_port(1)'}]
        }


def test_metavariable_pattern_parsing():
    with open(os.path.join(policy_dir, 'python_simple_metavar_pattern.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1', 'message': 'some guidelines', 'severity': 'INFO', 'languages': ['python'], 'metadata': {
                'name': 'check name'},
            'patterns': [
                {'metavariable-pattern': {
                    'metavariable': '$ARG',
                    'pattern': 'os.getcwd()'
                    }},
                {'pattern': 'os.system($ARG)'}
            ]
        }


def test_metavariable_regex_parsing():
    with open(os.path.join(policy_dir, 'python_simple_metavar_regex.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1', 'message': 'some guidelines', 'severity': 'INFO', 'languages': ['python'], 'metadata': {
                'name': 'check name'},
            'patterns': [
                {'metavariable-regex': {
                    'metavariable': '$ARG',
                    'regex': '(os.exec|subprocess.run)'
                    }
                },
                {'pattern': 'hello($ARG)'}
            ]
        }


def test_metavariable_less_than_comparison_parsing():
    with open(os.path.join(policy_dir, 'python_simple_metavar_comparison.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1', 'message': 'some guidelines', 'severity': 'INFO', 'languages': ['python'], 'metadata': {
                'name': 'check name'},
            'patterns': [
                {'metavariable-comparison': {
                    'metavariable': '$ARG',
                    'comparison': '$ARG < 20 && ARG >=5'
                    }
                },
                {'pattern': 'equal($ARG)'}
            ]
        }


def test_basic_taint_mode_parsing_1():
    with open(os.path.join(policy_dir, 'python_taint_1.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1', 'mode': 'taint', 'message': 'some guidelines', 'severity': 'INFO', 'languages': ['python'],
            'metadata': {'name': 'check name'},
            'pattern-sources': [{'pattern': 'get_user_input(...)'}],
            'pattern-sinks': [{'pattern': 'html_output(...)'}]
        }

def test_taint_mode_parsing_1():
    with open(os.path.join(policy_dir, 'python_taint_1.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1', 'mode': 'taint', 'message': 'some guidelines', 'severity': 'INFO', 'languages': ['python'],
            'metadata': {'name': 'check name'},
            'pattern-sources': [{'pattern': 'get_user_input(...)'}],
            'pattern-sinks': [{'pattern': 'html_output(...)'}]
        }


def test_taint_mode_parsing_2():
    with open(os.path.join(policy_dir, 'python_taint_2.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1', 'mode': 'taint', 'message': 'some guidelines', 'severity': 'INFO', 'languages': ['python'],
            'metadata': {'name': 'check name'},
            'pattern-sources': [
                {'patterns': [
                    {'pattern-inside': '@javax.ws.rs.Path("...")\n$TYPE $FUNC(..., $VAR, ...) {\n  ...\n}\n'},
                    {'pattern': '$VAR'}
                ]
                 }
            ],
            'pattern-sinks': [{'pattern': 'return ...;'}],
        }

def test_taint_mode_parsing_3():
    with open(os.path.join(policy_dir, 'python_taint_3.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1', 'message': 'some guidelines', 'languages': ['python'], 'severity': 'INFO',
            'metadata': {'name': 'check name'}, 'mode': 'taint',
            'pattern-sources': [{'patterns': [
                {'pattern-inside': '@javax.ws.rs.Path("...")\n$TYPE $FUNC(..., $VAR, ...) {\n  ...\n}\n'},
                {'pattern': '$VAR'}]}],
            'pattern-sinks': [{'pattern': 'return ...;'}],
            'pattern-sanitizers': [
                {'pattern': 'org.apache.commons.text.StringEscapeUtils.unescapeJava(...);'},
                {'patterns': [
                    {'pattern-inside': '$STR.replaceAll("$REPLACE_CHAR", "$REPLACER");\n...\n'},
                    {'metavariable-regex': {'metavariable': '$REPLACER', 'regex': '.*^(CRLF).*'}},
                    {'metavariable-regex': {'metavariable': '$REPLACE_CHAR', 'regex': '(*CRLF)'}},
                    {'pattern': '$STR'}]}],
            'pattern-propagators': [{'pattern': '$SET.add(...)'}]}


def test_complex_policy_parsing_1():
    with open(os.path.join(policy_dir, 'python_complex_policy_1.yaml'), "r") as f:
        raw_check = yaml.safe_load(f)
        parsed_check = parser.parse_raw_check_to_semgrep(raw_check)
        assert parsed_check == {
            'id': 'CKV_SAST_1', 'message': 'some guidelines', 'languages': ['python'], 'severity': 'INFO',
            'metadata': {'name': 'check name'}, 'pattern-either': [
                {'patterns': [{'pattern-not-inside': '$VAR = ssl\n...\n$VAR.check_hostname = True\n'},
                              {'pattern': '$VAR = ssl'}]},
                {'patterns': [{'pattern-not-inside': '$VAR = ssl\n...\n$VAR.check_hostname = True\n'},
                              {'pattern': '$VAR = ssl'}]},
                {'pattern-either': [{'pattern': '$VAR = ssl\n...\n$VAR.check_hostname1 = False\n'},
                                    {'pattern': '$VAR = ssl\n...\n$VAR.check_hostname2 = False'}]}]}

def test_manually_bql_to_semgrep_parsing():
    """
    This test is not really a full test by itself, just a util for manual testing
    It can be used for manually reviewing the parsed results of our bql to semgrep parser
    Usage instructions:
    1. Fill the bql_policies_dir with a path to a directory with bql yaml policies
    2. Uncomment the rest of the test and make it run
    3. Check the parsed rules file './parsed_semgrep_rules.yaml' to review the parsed results
    """
    # bql_policies_dir = ''  # absolute path to a directory that contains bql policy yaml files
    #
    # registry = Registry(checks_dir=bql_policies_dir)
    # registry.load_rules(['all'], None)
    # registry.temp_semgrep_rules_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'parsed_semgrep_rules.yaml')
    # registry.create_temp_rules_file()
