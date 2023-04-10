from __future__ import annotations
import abc


class Predicate:
    def __init__(self):
        self.is_true = False

    @abc.abstractmethod
    def __eq__(self, other: Predicate):
        raise NotImplemented()

    @abc.abstractmethod
    def __hash__(self):
        raise NotImplemented()


class Predicament:
    def __init__(self, logical_op: str, predicates: list[Predicate] | None = None,
                 predicaments: list[Predicament] | None = None):
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

    def get_all_children_predicates(self) -> list[Predicate]:
        predicates = []
        for sub_predicament in self.predicaments:
            predicates.extend(sub_predicament.get_all_children_predicates())
            # for predicate in sub_predicament.predicates:
            #         predicates.append(predicate)

        predicates.extend(self.predicates)
        return predicates
