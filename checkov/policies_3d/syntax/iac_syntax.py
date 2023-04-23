from __future__ import annotations
import abc

from checkov.common.output.record import Record
from checkov.policies_3d.syntax.syntax import Predicate
from typing import Any


class IACPredicate(Predicate):
    def __init__(self, record: Record) -> None:
        super().__init__()
        self.record = record

    @abc.abstractmethod
    def __call__(self) -> bool:
        raise NotImplementedError()


class ViolationIdEquals(IACPredicate):
    def __init__(self, record: Record, violation_id: str) -> None:
        super().__init__(record)
        self.violation_id = violation_id

    def __call__(self) -> bool:
        self.is_true = isinstance(self.violation_id, str) and self.record.bc_check_id == self.violation_id
        return self.is_true

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ViolationIdEquals):
            return False

        return self.violation_id == other.violation_id and self.record.bc_check_id == other.record.bc_check_id

    def __hash__(self) -> Any:
        return hash(('violation_id', self.violation_id, 'bc_check_id', self.record.bc_check_id))
