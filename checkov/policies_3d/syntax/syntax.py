from __future__ import annotations
import abc

from checkov.common.output.record import Record
from checkov.sca_image.models import ReportCVE


class Predicate:
    # To be used only for types
    def __init__(self):
        self.is_true = False

class IACPredicate(Predicate):
    def __init__(self, record: Record):
        super().__init__()
        self.record = record

    @abc.abstractmethod
    def __call__(self):
        raise NotImplemented()

class CVEPredicate(Predicate):
    def __init__(self, cve_report: ReportCVE):
        super().__init__()
        self.cve_report = cve_report

    @abc.abstractmethod
    def __call__(self) -> bool:
        raise NotImplemented()

class SecretsPredicate(Predicate):
    def __init__(self, record: Record):
        super().__init__()
        self.record = record
    @abc.abstractmethod
    def __call__(self):
        raise NotImplemented()


class ViolationIdEquals(IACPredicate):
    def __init__(self, record: Record, violation_id: str):
        super().__init__(record)
        self.violation_id = violation_id

    def __call__(self) -> bool:
        self.is_true =  isinstance(self.violation_id, str) and self.record.bc_check_id == self.violation_id
        return self.is_true


class RiskFactorCVEContains(CVEPredicate):
    def __init__(self, risk_factors: list[str], cve_report: ReportCVE):
        super().__init__(cve_report)
        self.risk_factors = [rf.lower() for rf in risk_factors]
        self.cve_report.riskFactors = [rf.lower() for rf in cve_report.riskFactors]

    def __call__(self) -> bool:
        self.is_true = all(rf in self.cve_report.riskFactors for rf in self.risk_factors)
        return self.is_true



class Predicament:
    def __init__(self, logical_op: str, predicates: list[Predicate] | None = None,
                 predicaments: list[Predicament] | None = None):
        self.predicates = predicates or []
        self.predicaments = predicaments or []
        self.logical_op = logical_op.lower()

    def __call__(self) -> bool:
        if self.logical_op == 'or':
            return any(predicate() for predicate in self.predicates) or \
                any(predicament() for predicament in self.predicaments)

        return all(predicate() for predicate in self.predicates) and \
            any(predicament() for predicament in self.predicaments)

    def get_all_children_predicates(self) -> list[Predicate]:
        predicates = []
        for sub_predicament in self.predicaments:
            for predicate in sub_predicament.predicates:
                    predicates.append(predicate)

        predicates.extend(self.predicates)
        return predicates
