from . conftest import run_validator_for_test_file


def test_file_with_class_attribute():
    errors = run_validator_for_test_file('class_attribute_fail.py')
    assert len(errors) == 1


def test_file_with_class_const():
    errors = run_validator_for_test_file('class_const_pass.py')
    assert len(errors) == 0


def test_file_with_class_special_attributes():
    errors = run_validator_for_test_file('class_special_attributes_pass.py')
    assert len(errors) == 0


def test_dataclass_skip():
    errors = run_validator_for_test_file('dataclass_skip.py')
    assert len(errors) == 0


def test_typing_class_skip():
    errors = run_validator_for_test_file('typing_class_skip.py')
    assert len(errors) == 0
