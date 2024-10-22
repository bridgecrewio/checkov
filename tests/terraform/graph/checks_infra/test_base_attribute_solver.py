from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


def test_get_cached_jsonpath_statement(mocker: MockerFixture):
    # given
    BaseAttributeSolver.jsonpath_parsed_statement_cache = {}  # reset cache
    statement = "policy.Statement[?(@.Effect == Allow)].Action[*]"
    solver_1 = BaseAttributeSolver(
        resource_types=["aws_iam_policy"],
        attribute=statement,
        value="iam:*",
        is_jsonpath_check=True,
    )
    solver_2 = BaseAttributeSolver(
        resource_types=["aws_iam_policy"],
        attribute=statement,
        value="iam:*",
        is_jsonpath_check=True,
    )
    jsonpath_parse_mock = MagicMock()

    assert len(BaseAttributeSolver.jsonpath_parsed_statement_cache) == 0

    # when
    solver_1._get_cached_jsonpath_statement(statement=statement)
    assert len(BaseAttributeSolver.jsonpath_parsed_statement_cache) == 1

    # patch jsonpath_ng.parse to be able to check it was really not called again and the cache was properly used
    mocker.patch("checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver.parse", side_effect=jsonpath_parse_mock)
    solver_2._get_cached_jsonpath_statement(statement=statement)

    # then
    assert len(BaseAttributeSolver.jsonpath_parsed_statement_cache) == 1
    jsonpath_parse_mock.assert_not_called()  # jsonpath_ng.parse shouldn't have been called again
