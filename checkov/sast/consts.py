from enum import Enum
from typing import List, Any, Set

from semgrep.constants import RuleSeverity
from checkov.common.graph.checks_infra.enums import Operators


class SastLanguages(Enum):
    @classmethod
    def list(cls) -> List[Any]:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def set(cls) -> Set["SastLanguages"]:
        return set(cls)

    PYTHON = 'python'
    JAVA = 'java'
    JAVASCRIPT = 'javascript'
    TYPESCRIPT = 'typescript'


class SastEngines(str, Enum):
    def __str__(self) -> str:
        return self.value

    SEMGREP = 'semgrep'
    PRISMA = 'prisma'


class SemgrepAttribute(str, Enum):
    def __str__(self) -> str:
        return self.value

    ID = 'id'
    MESSAGE = 'message'
    SEVERITY = 'severity'
    CWE = 'cwe'
    OWASP = 'owasp'
    LANGUAGES = 'languages'
    PATTERNS = 'patterns'
    PATTERN = 'pattern'
    PATTERN_EITHER = 'pattern-either'
    PATTERN_INSIDE = 'pattern-inside'
    PATTERN_NOT_INSIDE = 'pattern-not-inside'
    PATTERN_NOT = 'pattern-not'
    PATTERN_REGEX = 'pattern-regex'
    PATTERN_NOT_REGEX = 'pattern-not-regex'
    METAVARIABLE = 'metavariable'
    METAVARIABLE_PATTERN = 'metavariable-pattern'
    METAVARIABLE_REGEX = 'metavariable-regex'
    METAVARIABLE_COMPARISON = 'metavariable-comparison'
    COMPARISON = 'comparison'
    REGEX = 'regex'
    PATTERN_SOURCES = 'pattern-sources'
    PATTERN_SINKS = 'pattern-sinks'
    PATTERN_SANITIZERS = 'pattern-sanitizers'
    PATTERN_PROPAGATORS = 'pattern-propagators'


class BqlVersion(str, Enum):
    def __str__(self) -> str:
        return self.value

    V0_1 = '0.1'
    V0_2 = '0.2'


def get_bql_version_from_string(version_str: str) -> str:
    for version in BqlVersion:
        if version.value == version_str:
            return version
    return ''


class BqlV1ConditionType(str, Enum):
    def __str__(self) -> str:
        return self.value

    PATTERN = "pattern"
    OR = 'or'
    AND = 'and'
    PATTERN_SOURCE = 'pattern_source'
    PATTERN_SINK = 'pattern_sink'
    PATTERN_SANITIZER = 'pattern_sanitizer'
    PATTERN_PROPAGATOR = 'pattern_propagator'
    FILTER = 'filter'
    VARIABLE = "variable"


class BqlV2ConditionType(str, Enum):
    def __str__(self) -> str:
        return self.value

    OR = 'or'
    AND = 'and'
    PATTERN = "pattern"
    PATTERNS = 'patterns'
    REGEX = 'regex'
    CONDITIONS = 'conditions'
    METAVARIABLE = 'metavariable'
    NOT_PATTERN = 'not_pattern'
    NOT_REGEX = 'not_regex'
    WITHIN = 'within'
    NOT_WITHIN = 'not_within'
    SOURCE = 'source'
    SOURCES = 'sources'
    SINK = 'sink'
    SINKS = 'sinks'
    SANITIZER = 'sanitizer'
    SANITIZERS = 'sanitizers'
    PROPAGATOR = 'propagator'
    PROPAGATORS = 'propagators'
    COMPARISON = 'comparison'


BQLV2_KEY_TO_SEMGREP_ATTR = {
    str(BqlV2ConditionType.PATTERN): str(SemgrepAttribute.PATTERN),
    str(BqlV2ConditionType.SOURCE): str(SemgrepAttribute.PATTERN),
    str(BqlV2ConditionType.SINK): str(SemgrepAttribute.PATTERN),
    str(BqlV2ConditionType.SANITIZER): str(SemgrepAttribute.PATTERN),
    str(BqlV2ConditionType.PROPAGATOR): str(SemgrepAttribute.PATTERN),
    str(BqlV2ConditionType.REGEX): str(SemgrepAttribute.PATTERN_REGEX),
    str(BqlV2ConditionType.NOT_PATTERN): str(SemgrepAttribute.PATTERN_NOT),
    str(BqlV2ConditionType.NOT_REGEX): str(SemgrepAttribute.PATTERN_NOT_REGEX),
    str(BqlV2ConditionType.WITHIN): str(SemgrepAttribute.PATTERN_INSIDE),
    str(BqlV2ConditionType.NOT_WITHIN): str(SemgrepAttribute.PATTERN_NOT_INSIDE),
}

BQLV2_METAVAR_KEY_TO_SEMGREP_ATTR = {
    str(BqlV2ConditionType.PATTERN): str(SemgrepAttribute.METAVARIABLE_PATTERN),
    str(BqlV2ConditionType.PATTERNS): str(SemgrepAttribute.METAVARIABLE_PATTERN),
    str(BqlV2ConditionType.REGEX): str(SemgrepAttribute.METAVARIABLE_REGEX),
    str(BqlV2ConditionType.COMPARISON): str(SemgrepAttribute.METAVARIABLE_COMPARISON)
}

PATTERN_OPERATOR_TO_SEMGREP_ATTR = {
    Operators.EQUALS: SemgrepAttribute.PATTERN.value,
    Operators.NOT_EQUALS: SemgrepAttribute.PATTERN_NOT.value,
    Operators.REGEX_MATCH: SemgrepAttribute.PATTERN_REGEX.value,
    Operators.NOT_REGEX_MATCH: SemgrepAttribute.PATTERN_NOT_REGEX.value
}

VARIABLE_OPERATOR_TO_SEMGREP_ATTR = {
    Operators.REGEX_MATCH: SemgrepAttribute.METAVARIABLE_REGEX.value,
    Operators.PATTERN_MATCH: SemgrepAttribute.METAVARIABLE_PATTERN.value,
    Operators.EQUALS: SemgrepAttribute.METAVARIABLE_COMPARISON.value,
    Operators.NOT_EQUALS: SemgrepAttribute.METAVARIABLE_COMPARISON.value,
    Operators.GREATER_THAN: SemgrepAttribute.METAVARIABLE_COMPARISON.value,
    Operators.GREATER_THAN_OR_EQUAL: SemgrepAttribute.METAVARIABLE_COMPARISON.value,
    Operators.LESS_THAN: SemgrepAttribute.METAVARIABLE_COMPARISON.value,
    Operators.LESS_THAN_OR_EQUAL: SemgrepAttribute.METAVARIABLE_COMPARISON.value
}

FILTER_OPERATOR_TO_SEMGREP_ATTR = {
    Operators.WITHIN: SemgrepAttribute.PATTERN_INSIDE.value,
    Operators.NOT_WITHIN: SemgrepAttribute.PATTERN_NOT_INSIDE.value,
}

SUPPORT_FILE_EXT = {
    SastLanguages.PYTHON: ['py'],
    SastLanguages.JAVA: ['java'],
    SastLanguages.JAVASCRIPT: ['js'],
    SastLanguages.TYPESCRIPT: ['ts'],
}

FILE_EXT_TO_SAST_LANG = {
    'py': SastLanguages.PYTHON,
    'java': SastLanguages.JAVA,
    'js': SastLanguages.JAVASCRIPT,
    'ts': SastLanguages.TYPESCRIPT,
}

COMPARISON_VALUES = [
    Operators.EQUALS,
    Operators.NOT_EQUALS,
    Operators.GREATER_THAN,
    Operators.GREATER_THAN_OR_EQUAL,
    Operators.LESS_THAN,
    Operators.LESS_THAN_OR_EQUAL
]

COMPARISON_VALUE_TO_SYMBOL = {
    Operators.EQUALS: '==',
    Operators.NOT_EQUALS: '!=',
    Operators.GREATER_THAN: '>',
    Operators.GREATER_THAN_OR_EQUAL: '>=',
    Operators.LESS_THAN: '<',
    Operators.LESS_THAN_OR_EQUAL: '<='
}

SEMGREP_SEVERITY_TO_CHECKOV_SEVERITY = {
    RuleSeverity.ERROR: 'HIGH',
    RuleSeverity.WARNING: 'MEDIUM',
    RuleSeverity.INFO: 'LOW',
}

CHECKOV_SEVERITY_TO_SEMGREP_SEVERITY = {
    'HIGH': RuleSeverity.ERROR.value,
    'MEDIUM': RuleSeverity.WARNING.value,
    'LOW': RuleSeverity.INFO.value,
}
