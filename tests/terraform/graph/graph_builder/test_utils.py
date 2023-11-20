import pytest

from checkov.terraform.graph_builder.utils import join_double_quote_surrounded_dot_split


@pytest.mark.parametrize(
    "input_parts,expected_parts",
    [
        (
            ["google_project_iam_binding", 'role["roles/logging', 'admin"]'],
            ["google_project_iam_binding", 'role["roles/logging.admin"]'],
        ),
        (
            ["module", "google_project_iam_binding", 'role["roles/logging', 'admin"]'],
            ["module", "google_project_iam_binding", 'role["roles/logging.admin"]'],
        ),
        (
            [
                "module",
                "google_project_iam_binding",
                'role["roles/logging',
                'admin"]',
                "module",
                "google_project_iam_binding",
                'role["roles/logging',
                'admin"]',
            ],
            [
                "module",
                "google_project_iam_binding",
                'role["roles/logging.admin"]',
                "module",
                "google_project_iam_binding",
                'role["roles/logging.admin"]',
            ],
        ),
    ],
    ids=["resource", "module_resource", "complex"],
)
def test_join_double_quote_surrounded_dot_split(input_parts, expected_parts):
    assert join_double_quote_surrounded_dot_split(str_parts=input_parts) == expected_parts
