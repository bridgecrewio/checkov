import re
from packaging import version
VERSION_REGEX = re.compile(r'^(?P<operator>=|!=|>=|>|<=|<|~>)*(?P<version>.+)$')


class VersionConstraint:
    def __init__(self, constraint_parts):
        self.version = version.parse(constraint_parts.get('version', ''))
        self.operator = constraint_parts.get('operator')
        if not self.operator:
            self.operator = '='

    def special_op(self, other):
        return self.version == other.version

    def get_max_version_for_most_specific_segment(self):
        return version.parse(f'{self.version.major+1}.0.0')

    def versions_matching(self, other):
        other = version.parse(other)
        res = {
            '=': lambda other_version: other_version == self.version,
            '!=': lambda other_version: other_version != self.version,
            '>': lambda other_version: other_version > self.version,
            '>=': lambda other_version: other_version >= self.version,
            '<': lambda other_version: other_version < self.version,
            '<=': lambda other_version: other_version <= self.version,
            '~>': lambda other_version: self.version <= other_version < self.get_max_version_for_most_specific_segment()
        }[self.operator](other)
        return res


def get_version_constraints(raw_version):
    raw_version = raw_version.replace(' ', '')
    raw_version_constraints = raw_version.split(',')
    version_constraints = []
    for constraint in raw_version_constraints:
        constraint_parts = re.search(VERSION_REGEX, constraint).groupdict()
        version_constraints.append(VersionConstraint(constraint_parts))
    return version_constraints


def order_versions_by_size(versions_strings):
    for iter_num in range(len(versions_strings) - 1, 0, -1):
        for idx in range(iter_num):
            if version.parse(versions_strings[idx]) < version.parse(versions_strings[idx + 1]):
                temp = versions_strings[idx]
                versions_strings[idx] = versions_strings[idx + 1]
                versions_strings[idx + 1] = temp
    return versions_strings




