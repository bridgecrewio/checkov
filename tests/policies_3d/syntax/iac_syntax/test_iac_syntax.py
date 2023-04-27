import pytest

from checkov.common.output.record import Record
from checkov.policies_3d.syntax.iac_syntax import ViolationIdEquals


@pytest.fixture
def record() -> Record:
    _check_id = 'CHECK_ID'
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

def test_violation_id_equals_predicate_true(record: Record):
    # Arrange
    check_id = 'CHECK_ID'
    predicate = ViolationIdEquals(record, check_id)

    # Act
    predicate()

    # Assert
    assert predicate.is_true


def test_violation_id_equals_predicate_false(record: Record):
    # Arrange
    check_id = 'NOT_A_CHECK_ID'
    predicate = ViolationIdEquals(record, check_id)

    # Act
    predicate()

    # Assert
    assert not predicate.is_true


def test_violation_id_equals_predicate_false_equality(record: Record):
    # Arrange
    check_id_1 = 'CHECK_ID_1'
    check_id_2 = 'CHECK_ID_2'
    p1 = ViolationIdEquals(record, check_id_1)
    p2 = ViolationIdEquals(record, check_id_2)

    # Assert
    assert p1 != p2

def test_violation_id_equals_predicate_true_equality(record: Record):
    # Arrange
    check_id = 'CHECK_ID'
    p1 = ViolationIdEquals(record, check_id)
    p2 = ViolationIdEquals(record, check_id)

    # Assert
    assert p1 == p2

