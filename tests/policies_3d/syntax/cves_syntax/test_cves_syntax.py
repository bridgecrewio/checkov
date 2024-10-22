import pytest

from checkov.policies_3d.syntax.cves_syntax import RiskFactorCVEContains


@pytest.fixture
def cve_report_string_risk_factors():
    return {
        'cveId': 'cveId',
        'status': 'status',
        'severity': 'severity',
        'packageName': 'packageName',
        'packageVersion': 'packageVersion',
        'link': 'link',
        'publishedDate': 'publishedDate',
        'cvss': 'cvss',
        'vector': 'vector',
        'description': 'description',
        'riskFactors': 'DoS'
    }

@pytest.fixture
def cve_report_list_risk_factors():
    return {
        'cveId': 'cveId',
        'status': 'status',
        'severity': 'severity',
        'packageName': 'packageName',
        'packageVersion': 'packageVersion',
        'link': 'link',
        'publishedDate': 'publishedDate',
        'cvss': 'cvss',
        'vector': 'vector',
        'description': 'description',
        'riskFactors': ['DoS', 'RCE']
    }

@pytest.fixture
def cve_report_list_prefix_risk_factors():
    return {
        'cveId': 'cveId',
        'status': 'status',
        'severity': 'severity',
        'packageName': 'packageName',
        'packageVersion': 'packageVersion',
        'link': 'link',
        'publishedDate': 'publishedDate',
        'cvss': 'cvss',
        'vector': 'vector',
        'description': 'description',
        'riskFactors': ['DoS - High', 'RCE']
    }


def test_risk_factor_cve_contains_normalizes_risk_factors(cve_report_string_risk_factors):
    # Arrange
    risk_factors = ['dos']
    predicate = RiskFactorCVEContains(risk_factors, cve_report_string_risk_factors)

    # Assert
    assert predicate.risk_factors == ['dos']
    assert predicate.cve_report['riskFactors'] == ['dos']


def test_risk_factor_cve_contains_true(cve_report_string_risk_factors):
    # Arrange
    risk_factors = ['dos']
    predicate = RiskFactorCVEContains(risk_factors, cve_report_string_risk_factors)

    # Act
    predicate()

    # Assert
    assert predicate.is_true

def test_risk_factor_cve_contains_false(cve_report_string_risk_factors):
    # Arrange
    risk_factors = ['not a risk factor']
    predicate = RiskFactorCVEContains(risk_factors, cve_report_string_risk_factors)

    # Act
    predicate()

    # Arrange
    assert not predicate.is_true

def test_risk_factor_cve_contains_true_2(cve_report_list_risk_factors):
    # Arrange
    risk_factors = ['dos']
    predicate = RiskFactorCVEContains(risk_factors, cve_report_list_risk_factors)

    # Act
    predicate()

    # Assert
    assert predicate.is_true

def test_risk_factor_cve_contains_true_3(cve_report_list_prefix_risk_factors):
    # Arrange
    risk_factors = ['dos']
    predicate = RiskFactorCVEContains(risk_factors, cve_report_list_prefix_risk_factors)

    # Act
    predicate()

    # Assert
    assert predicate.is_true


def test_risk_factor_cve_contains_false_2(cve_report_list_risk_factors):
    # Arrange
    risk_factors = ['not a risk factor']
    predicate = RiskFactorCVEContains(risk_factors, cve_report_list_risk_factors)

    # Act
    predicate()

    # Arrange
    assert not predicate.is_true


def test_risk_factor_cve_contains_true_equality(cve_report_list_risk_factors):
    # Arrange
    risk_factors = ['Dos']
    p1 = RiskFactorCVEContains(risk_factors, cve_report_list_risk_factors)
    p2 = RiskFactorCVEContains(risk_factors, cve_report_list_risk_factors)

    # Assert
    assert p1 == p2


def test_risk_factor_cve_contains_false_equality(cve_report_list_risk_factors):
    # Arrange
    risk_factors_1 = ['Dos']
    risk_factors_2 = ['RCE']
    p1 = RiskFactorCVEContains(risk_factors_1, cve_report_list_risk_factors)
    p2 = RiskFactorCVEContains(risk_factors_2, cve_report_list_risk_factors)

    # Assert
    assert p1 != p2
