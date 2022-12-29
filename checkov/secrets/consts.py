from enum import Enum


class ValidationStatus(Enum):
    Privileged = 'Privileged'
    Valid = 'Valid'
    Invalid = 'Invalid'
    Unknown = 'Unknown'
