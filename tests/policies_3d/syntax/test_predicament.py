from checkov.common.output.record import Record
from checkov.policies_3d.syntax.iac_syntax import ViolationIdEquals
import pytest

from checkov.policies_3d.syntax.syntax import Predicament


@pytest.fixture
def record_1() -> Record:
    _check_id = 'CHECK_ID_1'
    return Record(
        bc_check_id=_check_id,
        check_id=_check_id,
        check_name='mock',
        check_result={'result': 'failed'},
        code_block=[],
        file_path='',
        file_line_range=[],
        resource='',
        check_class='',
        file_abs_path='',
        evaluations={}
    )

@pytest.fixture
def record_2() -> Record:
    _check_id = 'CHECK_ID_2'
    return Record(
        bc_check_id=_check_id,
        check_id=_check_id,
        check_name='mock',
        check_result={'result': 'failed'},
        code_block=[],
        file_path='',
        file_line_range=[],
        resource='',
        check_class='',
        file_abs_path='',
        evaluations={}
    )

def test_get_all_children_predicates(record_1):
    # Arrange
    p1 = ViolationIdEquals(record_1, 'CHECK_ID')
    predicament = Predicament(
        logical_op='and',
        predicates=[p1]
    )

    # Act
    predicates = predicament.get_all_children_predicates()

    # Assert
    assert predicates == {p1}


def test_get_all_children_predicates_with_nested_predicaments(record_1, record_2):
    # Arrange
    p1 = ViolationIdEquals(record_1, 'CHECK_ID_1')
    p2 = ViolationIdEquals(record_2, 'CHECK_ID_2')
    predicament = Predicament(
        logical_op='and',
        predicates=[p1, p2]
    )

    # Act
    predicates = predicament.get_all_children_predicates()

    # Assert
    assert predicates == {p1, p2}


def test_and_predicament_true(record_1, record_2):
    # Arrange
    p1 = ViolationIdEquals(record_1, 'CHECK_ID_1')
    p2 = ViolationIdEquals(record_2, 'CHECK_ID_2')
    predicament = Predicament(
        logical_op='and',
        predicates=[p1, p2]
    )

    # Act
    res = predicament()

    # Assert
    assert res
    assert all(predicate.is_true for predicate in predicament.predicates)

def test_and_predicament_false(record_1, record_2):
    # Arrange
    p1 = ViolationIdEquals(record_1, 'NOT_CHECK_ID_1')
    p2 = ViolationIdEquals(record_2, 'CHECK_ID_2')
    predicament = Predicament(
        logical_op='and',
        predicates=[p1, p2]
    )

    # Act
    res = predicament()

    # Assert
    assert not res
    assert not predicament.predicates[0].is_true
    assert predicament.predicates[1].is_true

def test_or_predicament_true(record_1, record_2):
    # Arrange
    p1 = ViolationIdEquals(record_1, 'NOT_CHECK_ID_1')
    p2 = ViolationIdEquals(record_2, 'CHECK_ID_2')
    predicament = Predicament(
        logical_op='or',
        predicates=[p1, p2]
    )

    # Act
    res = predicament()

    # Assert
    assert res
    assert not predicament.predicates[0].is_true
    assert predicament.predicates[1].is_true

def test_or_predicament_false(record_1, record_2):
    # Arrange
    p1 = ViolationIdEquals(record_1, 'NOT_CHECK_ID_1')
    p2 = ViolationIdEquals(record_2, 'NOT_CHECK_ID_2')
    predicament = Predicament(
        logical_op='or',
        predicates=[p1, p2]
    )

    # Act
    res = predicament()

    # Assert
    assert not res
    assert not predicament.predicates[0].is_true
    assert not predicament.predicates[1].is_true

def test_and_predicament_nested_or_predicament_true(record_1, record_2):
    # Arrange
    p1 = ViolationIdEquals(record_1, 'CHECK_ID_1')
    p2 = ViolationIdEquals(record_2, 'NOT_CHECK_ID_2')
    sub_predicament = Predicament(
        logical_op='or',
        predicates=[p1, p2]
    )
    predicament = Predicament(
        logical_op='and',
        predicates=[p1],
        predicaments=[sub_predicament]
    )

    # Act
    res = predicament()

    # Assert
    assert res
    assert predicament.predicates[0].is_true
    assert predicament.predicaments[0].predicates[0].is_true
    assert not predicament.predicaments[0].predicates[1].is_true


def test_and_predicament_nested_or_predicament_false(record_1, record_2):
    # Arrange
    p1 = ViolationIdEquals(record_1, 'NOT_CHECK_ID_1')
    p2 = ViolationIdEquals(record_2, 'CHECK_ID_2')
    sub_predicament = Predicament(
        logical_op='or',
        predicates=[p1, p2]
    )
    predicament = Predicament(
        logical_op='and',
        predicates=[p1],
        predicaments=[sub_predicament]
    )

    # Act
    res = predicament()

    # Assert
    assert not res
    assert not predicament.predicates[0].is_true
    assert not predicament.predicaments[0].predicates[0].is_true
    assert predicament.predicaments[0].predicates[1].is_true