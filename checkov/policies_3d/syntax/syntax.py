from __future__ import annotations
import abc
from checkov.common.output.record import Record


class Predicate:
    def __init__(self, record: Record):
        self.record = record

    @abc.abstractmethod
    def __call__(self) -> bool:
        raise NotImplemented()


class ViolationIdEquals(Predicate):
    def __init__(self, record: Record, violation_id: str):
        super().__init__(record)
        self.violation_id = violation_id
    def __call__(self) -> bool:
        return isinstance(self.violation_id, str) and self.record.bc_check_id == self.violation_id


class Predicament:
    def __init__(self, predicates: list[Predicate], logical_op: str):
        self.predicates = predicates
        self.logical_op = logical_op.lower()

    def __call__(self) -> bool:
        if self.logical_op == 'or':
            return any(predicate() for predicate in self.predicates)

        return all(predicate() for predicate in self.predicates)