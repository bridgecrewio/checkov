from dataclasses import dataclass
from typing import Optional


class Severity:
    __slots__ = ("level", "name")

    def __init__(self, name: str, level: int) -> None:
        self.name = name
        self.level = level


@dataclass
class BcSeverities:
    NONE = 'NONE'
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'
    MODERATE = 'MODERATE'
    IMPORTANT = 'IMPORTANT'


Severities = {
    BcSeverities.NONE: Severity(BcSeverities.NONE, 0),
    BcSeverities.LOW: Severity(BcSeverities.LOW, 1),
    BcSeverities.MEDIUM: Severity(BcSeverities.MEDIUM, 2),
    BcSeverities.MODERATE: Severity(BcSeverities.MEDIUM, 2),
    BcSeverities.HIGH: Severity(BcSeverities.HIGH, 3),
    BcSeverities.IMPORTANT: Severity(BcSeverities.HIGH, 3),
    BcSeverities.CRITICAL: Severity(BcSeverities.CRITICAL, 4),
}


def get_severity(severity: Optional[str]) -> Optional[Severity]:
    if not severity:
        return None
    return Severities.get(severity.upper())
