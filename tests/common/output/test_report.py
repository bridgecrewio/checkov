from checkov.common.output.report import Report


def test_from_reduced_json(json_reduced_report):
    # Act
    report = Report.from_reduced_json(json_reduced_report, 'mock_check_type')

    # Assert
    assert len(report.failed_checks) == 1
    assert len(report.passed_checks) == 1

    failed_check = report.failed_checks[0]
    passed_check = report.passed_checks[0]

    assert failed_check.check_id == 'CKV_GHA_2'
    assert failed_check.check_name == 'Ensure ACTIONS_ALLOW_UNSECURE_COMMANDS isn\u0027t true on environment variables'
    assert failed_check.check_result == {
        "result": "FAILED",
        "results_configuration": {}
    }
    assert failed_check.resource == 'jobs(container-test-job)'
    assert failed_check.file_path == '/.github/workflows/image_no_violation.yml'
    assert failed_check.file_line_range == [7, 7]
    assert failed_check.file_abs_path == '/tmp/checkov/elturgeman6/elturgeman/supplygoat1/main/src/.github/workflows/image_no_violation.yml'
    assert failed_check.code_block == [
        [
            7,
            "    runs-on: ubuntu-latest\n"
        ],
    ]
    assert failed_check.bc_check_id == 'BC_REPO_GITHUB_ACTION_1'

    assert passed_check.check_id == 'CKV_GHA_1'
    assert passed_check.check_name == 'Ensure ACTIONS_ALLOW_UNSECURE_COMMANDS isn\u0027t true on environment variables'
    assert passed_check.check_result == {
        "result": "PASSED",
        "results_configuration": {}
    }
    assert passed_check.resource == 'jobs(container-test-job)'
    assert passed_check.file_path == '/.github/workflows/image_no_violation.yml'
    assert passed_check.file_line_range == [7, 7]
    assert passed_check.file_abs_path == '/tmp/checkov/elturgeman6/elturgeman/supplygoat1/main/src/.github/workflows/image_no_violation.yml'
    assert passed_check.code_block == [
        [
            7,
            "    runs-on: ubuntu-latest\n"
        ],
    ]
    assert passed_check.bc_check_id == 'BC_REPO_GITHUB_ACTION_1'


def test_get_plan_resource_raw_id_1():
    resource_id = Report.get_plan_resource_raw_id("module.vnet[0].azurerm_subnet.subnet_for_each['snet-commonservices']")
    assert resource_id == 'azurerm_subnet.subnet_for_each'


def test_get_plan_resource_raw_id_2():
    resource_id = Report.get_plan_resource_raw_id("module.vnet[0].azurerm_subnet.subnet_for_each[1]")
    assert resource_id == 'azurerm_subnet.subnet_for_each'


def test_get_plan_resource_raw_id_3():
    resource_id = Report.get_plan_resource_raw_id("module.vnet[0].azurerm_subnet.subnet_for_each")
    assert resource_id == 'azurerm_subnet.subnet_for_each'


def test_get_plan_resource_raw_id_4():
    resource_id = Report.get_plan_resource_raw_id("module.vnet.azurerm_subnet.subnet_for_each")
    assert resource_id == 'azurerm_subnet.subnet_for_each'


def test_get_plan_resource_raw_id_5():
    resource_id = Report.get_plan_resource_raw_id("aws_route53_zone.example[\"example.com\"]")
    assert resource_id == 'aws_route53_zone.example'


def test_get_plan_resource_raw_id_6():
    resource_id = Report.get_plan_resource_raw_id("module.sg[\"bad_example\"].aws_security_group.bad")
    assert resource_id == 'aws_security_group.bad'


def test_get_plan_resource_raw_id_7():
    resource_id = Report.get_plan_resource_raw_id("type.name")
    assert resource_id == 'type.name'
