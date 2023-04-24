from __future__ import annotations
import abc
from typing import Any

from checkov.policies_3d.syntax.syntax import Predicate


class CVEPredicate(Predicate):
    def __init__(self, cve_report: dict[str, Any]) -> None:
        super().__init__()
        self.cve_report = cve_report

    @abc.abstractmethod
    def __call__(self) -> bool:
        raise NotImplementedError()


class RiskFactorCVEContains(CVEPredicate):
    def __init__(self, risk_factors: list[str], cve_report: dict[str, Any]) -> None:
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RiskFactorCVEContains):
            return False

        return set(self.risk_factors) == set(other.risk_factors) and self.cve_report['cveId'] == other.cve_report['cveId']

    def __hash__(self) -> Any:
        return hash(('risk_factors', tuple(self.risk_factors), 'cveId', self.cve_report['cveId']))
