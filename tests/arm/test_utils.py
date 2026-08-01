from pathlib import Path

from checkov.arm.utils import get_files_definitions, extract_resource_name_from_reference_func, \
    extract_resource_name_from_resource_id_func


def test_get_files_definitions_with_parsing_error():
    # given
    file_path = Path(__file__).parent / "parser/examples/json/with_comments.json"

    # when
    definitions, definitions_raw, parsing_errors = get_files_definitions([str(file_path)])

    # then
    assert definitions == {}
    assert definitions_raw == {}
    assert len(parsing_errors) == 1
    assert parsing_errors[0].endswith("parser/examples/json/with_comments.json")


def test_extract_resource_name_from_reference_func():
    test_cases = ["reference('storageAccountName')",
                  "reference('myStorage').primaryEndpoints",
                  "reference('myStorage', '2022-09-01', 'Full').location",
                  "reference(resourceId('storageResourceGroup', 'Microsoft.Storage/storageAccounts', "
                  "'storageAccountName')), '2022-09-01')",
                  "reference(resourceId('Microsoft.Network/publicIPAddresses', 'ipAddressName'))"]

    expected = ["storageAccountName", "myStorage", "myStorage", "storageAccountName", "ipAddressName"]

    for i, test_case in enumerate(test_cases):
        assert extract_resource_name_from_reference_func(test_case) == expected[i]


def test_extract_resource_name_from_reference_func_resource_id_substring_without_call():
    # 'resourceId' appears as a substring of the resource name here without
    # being followed by '(', so this must not be treated as a nested
    # resourceId(...) call - it used to raise an IndexError.
    test_case = "reference('resourceIdentifier').primaryEndpoints"

    assert extract_resource_name_from_reference_func(test_case) == "resourceIdentifier"


def test_extract_resource_name_from_resource_id_func():
    test_cases = ["resourceId('Microsoft.Network/virtualNetworks/', virtualNetworkName)",
                  "resourceId('Microsoft.Network/virtualNetworks/subnets', 'myVNet', 'mySubnet')"]

    expected = ["virtualNetworkName", "myVNet"]

    for i, test_case in enumerate(test_cases):
        assert extract_resource_name_from_resource_id_func(test_case) == expected[i]


def test_extract_resource_name_from_resource_id_func_single_arg():
    # a resourceId() call with no comma-separated arguments (malformed or an
    # unsupported single-argument form) used to raise an IndexError instead
    # of degrading gracefully.
    test_case = "resourceId('Microsoft.Storage/storageAccounts/myStorageAccount')"

    assert extract_resource_name_from_resource_id_func(test_case) == \
        "resourceId(Microsoft.Storage/storageAccounts/myStorageAccount)"
