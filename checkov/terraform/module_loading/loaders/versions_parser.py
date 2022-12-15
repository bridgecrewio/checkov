import re
from typing import List, Dict, Optional

from checkov.common.packaging import version

VERSION_REGEX = re.compile(r"^(?P<operator>=|!=|>=|>|<=|<|~>)?\s*(?P<version>[\d.]+-?\w*)$")


class VersionConstraint:
    """
    A class representing a module version. Enables comparing versions.
    """

    def __init__(self, constraint_parts: Dict[str, Optional[str]]) -> None:
        """
        :param constraint_parts: a dictionary representing a version constraint: {"version": "v1.2.3", "operator": ">="}
        """
        self.version = version.parse(constraint_parts.get("version") or "")
        self.operator = constraint_parts.get("operator") or "="

    def get_max_version_for_most_specific_segment(self) -> version.Version:
        return version.parse(f"{self.version.major + 1}.0.0")

    def versions_matching(self, other_version_str: str) -> bool:
        other_version = version.parse(other_version_str)
        res = {
            "=": lambda other: other == self.version,
            "!=": lambda other: other != self.version,
            ">": lambda other: other > self.version,
            ">=": lambda other: other >= self.version,
            "<": lambda other: other < self.version,
            "<=": lambda other: other <= self.version,
            "~>": lambda other: self.version <= other < self.get_max_version_for_most_specific_segment(),
        }[self.operator](other_version)
        return res

    def __str__(self) -> str:
        return f"{self.operator}{self.version}"


def get_version_constraints(raw_version: str) -> List[VersionConstraint]:
    """
    :param raw_version: A string representation of a version, e.g: "~> v1.2.3"
    :return: VersionConstraint instance
    """
    raw_version = raw_version.replace(" ", "")
    raw_version_constraints = raw_version.split(",")
    version_constraints = []
    for constraint in raw_version_constraints:
        match = re.search(VERSION_REGEX, constraint)
        if match:
            constraint_parts = match.groupdict()
            version_constraints.append(VersionConstraint(constraint_parts))
    return version_constraints


def order_versions_in_descending_order(versions_strings: List[str]) -> List[str]:
    """
    :param versions_strings: array of string versions: ["v1.2.3", "v1.2.4"...]
    :return: A sorted array of versions in descending order
    """
    for iter_num in range(len(versions_strings) - 1, 0, -1):
        for idx in range(iter_num):
            if version.parse(versions_strings[idx]) < version.parse(versions_strings[idx + 1]):
                temp = versions_strings[idx]
                versions_strings[idx] = versions_strings[idx + 1]
                versions_strings[idx + 1] = temp
    return versions_strings
