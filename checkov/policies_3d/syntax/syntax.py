from __future__ import annotations
import abc
from typing import Any

from checkov.common.output.record import Record
from checkov.sca_image.models import ReportCVE


class Predicate:
    def __init__(self):
        self.is_true = False

    @abc.abstractmethod
    def __eq__(self, other: Predicate):
        raise NotImplemented()

    @abc.abstractmethod
    def __hash__(self):
        raise NotImplemented()

class IACPredicate(Predicate):
    def __init__(self, record: Record):
        super().__init__()
        self.record = record

    @abc.abstractmethod
    def __call__(self):
        raise NotImplemented()

class CVEPredicate(Predicate):
    def __init__(self, cve_report: ReportCVE | dict[str, Any]):
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

    def __eq__(self, other: ViolationIdEquals) -> bool:
        return self.violation_id == other.violation_id and self.record.bc_check_id == other.record.bc_check_id

    def __hash__(self):
        return hash(('violation_id', self.violation_id, 'bc_check_id', self.record.bc_check_id))


class RiskFactorCVEContains(CVEPredicate):
    def __init__(self, risk_factors: list[str], cve_report: dict[str, Any]):
        super().__init__(cve_report)
        self.risk_factors = [rf.lower() for rf in risk_factors]
        report_risk_factors = cve_report.get('riskFactors', []) or []
        if isinstance(report_risk_factors, str):
            report_risk_factors = [report_risk_factors]

        self.cve_report['riskFactors'] = [rf.lower() for rf in report_risk_factors]

    def __call__(self) -> bool:
        self.is_true = all(rf in self.cve_report['riskFactors'] for rf in self.risk_factors)

        if not self.is_true:
            for rf in self.cve_report['riskFactors']:
                self.is_true = all(rf.startswith(predicate_rf) for predicate_rf in self.risk_factors)
                if self.is_true:
                    break

        return self.is_true

    def __eq__(self, other: RiskFactorCVEContains) -> bool:
        return set(self.risk_factors) == set(other.risk_factors) and self.cve_report['cveId'] == other.cve_report['cveId']

    def __hash__(self):
        return hash(('risk_factors', tuple(self.risk_factors), 'cveId', self.cve_report['cveId']))



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
