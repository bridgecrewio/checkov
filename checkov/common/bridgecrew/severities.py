from dataclasses import dataclass
from typing import Optional


class Severity:
    __slots__ = ("level", "name")

    def __init__(self, name: str, level: int) -> None:
        self.name = name
        self.level = level

    def __repr__(self) -> str:
        return self.name


@dataclass
class BcSeverities:
    NONE = 'NONE'
    INFO = 'INFO'
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'
    MODERATE = 'MODERATE'
    IMPORTANT = 'IMPORTANT'
    OFF = 'OFF'


Severities = {
    BcSeverities.NONE: Severity(BcSeverities.NONE, -999),
    BcSeverities.INFO: Severity(BcSeverities.INFO, 1),
    BcSeverities.LOW: Severity(BcSeverities.LOW, 2),
    BcSeverities.MEDIUM: Severity(BcSeverities.MEDIUM, 3),
    BcSeverities.MODERATE: Severity(BcSeverities.MEDIUM, 3),
    BcSeverities.HIGH: Severity(BcSeverities.HIGH, 4),
    BcSeverities.IMPORTANT: Severity(BcSeverities.HIGH, 4),
    BcSeverities.CRITICAL: Severity(BcSeverities.CRITICAL, 5),
    BcSeverities.OFF: Severity(BcSeverities.OFF, 999),
}


def get_severity(severity: Optional[str]) -> Optional[Severity]:
    if not severity:
        return None
    return Severities.get(severity.upper())
