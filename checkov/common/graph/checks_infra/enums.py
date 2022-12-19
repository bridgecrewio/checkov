from enum import Enum


class SolverType(str, Enum):
    # A solver is a class that resolves YAML syntax into a graph query
    # It can have the following types:
    ATTRIBUTE = "ATTRIBUTE"
    # An attribute query, i.e. id equals 3

    COMPLEX = "COMPLEX"
    # A combination of queries, i.e. <SOME_QUERY> AND <ANOTHER_QUERY>

    CONNECTION = "CONNECTION"
    # A connection between two entities, i.e. ec2 instance connected to security group

    # TODO: merge with COMPLEX
    COMPLEX_CONNECTION = "COMPLEX_CONNECTION"
    # A combination of CONNECTION solver and any other solver

    FILTER = "FILTER"
    # Filters results according to specific value / type, i.e. resource type is aws_s3_bucket


class Operators:
    ANY = 'any'
    EXISTS = 'exists'
    ONE_EXISTS = 'one_exists'
    NOT_EXISTS = 'not_exists'
    CONTAINS = 'contains'
    NOT_CONTAINS = 'not_contains'
    ENDING_WITH = 'ending_with'
    NOT_ENDING_WITH = 'not_ending_with'
    EQUALS = 'equals'
    NOT_EQUALS = 'not_equals'
    REGEX_MATCH = 'regex_match'
    NOT_REGEX_MATCH = 'not_regex_match'
    GREATER_THAN = 'greater_than'
    GREATER_THAN_OR_EQUAL = 'greater_than_or_equal'
    LESS_THAN = 'less_than'
    LESS_THAN_OR_EQUAL = 'less_than_or_equal'
    STARTING_WITH = 'starting_with'
    NOT_STARTING_WITH = 'not_starting_with'
    SUBSET = 'subset'
    NOT_SUBSET = 'not_subset'
    WITHIN = 'within'
    NOT_WITHIN = 'not_within'
    AND = 'and'
    OR = 'or'
    NOT = 'not'
    JSONPATH_EQUALS = 'jsonpath_equals'
    JSONPATH_NOT_EQUALS = 'jsonpath_not_equals'
    JSONPATH_EXISTS = 'jsonpath_exists'
    JSONPATH_NOT_EXISTS = 'jsonpath_not_exists'
    IS_EMPTY = 'is_empty'
    IS_NOT_EMPTY = 'is_not_empty'
    LENGTH_EQUALS = 'length_equals'
    LENGTH_NOT_EQUALS = 'length_not_equals'
    LENGTH_GREATER_THAN = 'length_greater_than'
    LENGTH_GREATER_THAN_OR_EQUAL = 'length_greater_than_or_equal'
    LENGTH_LESS_THAN = 'length_less_than'
    LENGTH_LESS_THAN_OR_EQUAL = 'length_less_than_or_equal'
    IS_TRUE = 'is_true'
    IS_FALSE = 'is_false'
    INTERSECTS = 'intersects'
    NOT_INTERSECTS = 'not_intersects'
    EQUALS_IGNORE_CASE = 'equals_ignore_case'
    NOT_EQUALS_IGNORE_CASE = 'not_equals_ignore_case'
    RANGE_INCLUDES = 'range_includes'
    RANGE_NOT_INCLUDES = 'range_not_includes'
    NUMBER_OF_WORDS_EQUALS = 'number_of_words_equals'
    NUMBER_OF_WORDS_NOT_EQUALS = 'number_of_words_not_equals'
    NUMBER_OF_WORDS_GREATER_THAN = 'number_of_words_greater_than'
    NUMBER_OF_WORDS_GREATER_THAN_OR_EQUAL = 'number_of_words_greater_than_or_equal'
    NUMBER_OF_WORDS_LESS_THAN = 'number_of_words_less_than'
    NUMBER_OF_WORDS_LESS_THAN_OR_EQUAL = 'number_of_words_less_than_or_equal'
