from __future__ import annotations
import abc
from typing import Any


class Predicate:
    def __init__(self) -> None:
        self.is_true = False

    @abc.abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def __hash__(self) -> Any:
        raise NotImplementedError()


class Predicament:
    def __init__(self, logical_op: str, predicates: list[Predicate] | None = None,
                 predicaments: list[Predicament] | None = None) -> None:
        self.predicates = predicates or []
        self.predicaments = predicaments or []
        self.logical_op = logical_op.lower()

    def __call__(self) -> bool:
        """
        Calls all direct and indirect predicates.

        Implementation note: using a list comprehension in any/all guarantees that all predicates will be computed
        by avoiding a short-circuit evaluation.
        """
        if self.logical_op == 'or':
            sub_predicaments_result = False
            if self.predicaments:
                sub_predicaments_result = any([predicament() for predicament in self.predicaments])

            return any([predicate() for predicate in self.predicates]) or sub_predicaments_result

        sub_predicaments_result = True
        if self.predicaments:
            sub_predicaments_result = all(predicament() for predicament in self.predicaments)

        return all([predicate() for predicate in self.predicates]) and sub_predicaments_result

    def get_all_children_predicates(self) -> set[Predicate]:
        predicates = set()
        for sub_predicament in self.predicaments:
            predicates.update(sub_predicament.get_all_children_predicates())

        predicates.update(set(self.predicates))
        return predicates
