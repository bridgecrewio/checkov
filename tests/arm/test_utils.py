from pathlib import Path

from checkov.arm.utils import get_files_definitions, extract_resource_name_from_reference_func


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
