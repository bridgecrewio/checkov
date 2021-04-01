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
    NOT_EXISTS = 'not_exists'
    CONTAINS = 'contains'
    NOT_CONTAINS = 'not_contains'
    ENDING_WITH = 'ending_with'
    NOT_ENDING_WITH = 'not_ending_with'
    EQUALS = 'equals'
    NOT_EQUALS = 'not_equals'
    STARTING_WITH = 'starting_with'
    NOT_STARTING_WITH = 'not_starting_with'
    WITHIN = 'within'
    AND = 'and'
    OR = 'or'
