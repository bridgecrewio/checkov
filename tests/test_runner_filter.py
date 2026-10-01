from typing import Optional, List, Set
from unittest.mock import MagicMock, patch

import pytest

from checkov.main import checkov_runners
from checkov.runner_filter import RunnerFilter


@pytest.mark.parametrize(
    "input_frameworks,input_skip_frameworks,expected_frameworks",
    [
        (["all"], None, {"all", "sast"}),
        (None, None, {"all"}),
        (["terraform"], None, {"terraform"}),
        (["cloudformation", "serverless"], None, {"cloudformation", "serverless"}),
        (["cdk"], None, {"cdk"}),
        (["cdk", "sast"], None, {"cdk", "sast"}),
        (
            ["all"],
            ["terraform", "secrets"],
            {
                "ansible",
                "argo_workflows",
                "arm",
                "azure_pipelines",
                "bicep",
                "cdk",
                "cloudformation",
                "dockerfile",
                "helm",
                "json",
                "yaml",
                "kubernetes",
                "serverless",
                "terraform_json",
                "terraform_plan",
                "github_configuration",
                "github_actions",
                "gitlab_configuration",
                "gitlab_ci",
                "bitbucket_configuration",
                "bitbucket_pipelines",
                "circleci_pipelines",
                "kustomize",
                "sca_package",
                "openapi",
                "sca_image",
                "sast",
                "3d_policy"
            },
        ),
        (["cloudformation", "serverless"], ["serverless", "secrets"], {"cloudformation"}),
    ],
    ids=["all", "none", "terraform", "multiple", "only cdk", "cdk and sast", "all_with_skip", "multiple_with_skip"],
)
def test_runner_filter_constructor_framework(
        input_frameworks: Optional[List[str]], input_skip_frameworks: Optional[List[str]], expected_frameworks: Set[str]
):
    # when
    runner_filter = RunnerFilter(
        framework=input_frameworks,
        runners=checkov_runners,
        skip_framework=input_skip_frameworks,
    )

    # then
    assert set(runner_filter.framework) == expected_frameworks

@patch("checkov.common.checks_infra.registry.get_all_graph_checks_registries")
@patch('checkov.common.checks.base_check_registry.BaseCheckRegistry.get_all_registered_checks')
def test_validate_checks(test_registry, graph_test_registry):
    runner_filter = RunnerFilter(
        checks= ['CKV_T_1', 'CKV_FAKE', 'CKV2_T_2', 'CKV_T*', 'CKV_BC_T_1', 'CKV2_BC_T_2', 'CKV2_BC_FAKE', 'CKV2_T*']
    )
    # Basechecks
    check1 = MagicMock()
    check1.id = 'CKV_T_1'
    check1.bc_id = 'CKV_BC_T_1'

    check2 = MagicMock()
    check2.id = 'CKV_T_2'
    check2.bc_id = 'CKV_BC_T_2'

    # graph checks 
    check3 = MagicMock()
    check3.id = 'CKV2_T_1'
    check3.bc_id = 'CKV2_BC_T_1'

    check4 = MagicMock()
    check4.id = 'CKV2_T_2'
    check4.bc_id = 'CKV2_BC_T_2'

    test_registry.return_value = [check1, check2]
    
    graph_test_registry.checks = [check3, check4]
    graph_test_registry.return_value = [graph_test_registry]
    
    invalid = runner_filter.validate_checks()
    assert invalid == ['CKV_FAKE', 'CKV2_BC_FAKE']

    test_registry.assert_called_once()
    graph_test_registry.assert_called_once() 