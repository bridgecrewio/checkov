from typing import Dict, Any

import pytest

from checkov.common.bridgecrew.bc_source import SourceType
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration, bc_integration


@pytest.fixture()
def mock_bc_integration() -> BcPlatformIntegration:
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    bc_integration.setup_bridgecrew_credentials(
        repo_id="bridgecrewio/checkov",
        skip_fixes=True,
        skip_download=True,
        source=SourceType("Github", False),
        source_version="1.0",
        repo_branch="master",
    )
    return bc_integration


@pytest.fixture()
def scan_result_success_response() -> Dict[str, Any]:
    return {'outputType': 'Result',
     'outputData': "H4sIAN22X2IC/8WY23LbOBKGX6VLN5tUWRQp"
                   "+SCrZi88drL2VqKkLMUzNZu5gEjIQkwSXAKUrU3l3fdvgDofnNS4MheJKbIJdAP"
                   "/193g10YpC22U1eWs0aNGy2ZFq5SmSq3B3/9WqpSZzK0J7JNtHFGjEMbIBKa2rKT7HT"
                   "+Ie2lw5z9fG3ZWSB6mmNmJztk+F5m7k3wR+b3mO1NZGoWHuBkFbT+mnTw"
                   "/+bcjOjTBOBXmYWP8MDh9sfHZXhprNqZoB+3TIPyBWf6EaayzIlUij"
                   "+WNMZVbvLxK07UnV8rYUo0q6yf62ohLZVUsUvwIYTlR95P6MpOJqrL6R6of6yurrbf+xi5XaS5LMVIpRplvl"
                   "+KNbFzevWm2w+i0eRp13XoZK2xl3KKqJ5mQyikKzoPuEf50g+iYbeKpYYvTIHLrEUNAfqzBoNcJwtbFXa"
                   "/furjsvWt9vMXVp5vebWvQu2zxnRv8u+j1eZhEGsRV1EE2LkttTBNylFTfz+/p1e"
                   "+DwWtaDWDGLtmJpESZTBlzOYG45K1MhZXJh9EXuPNRF1VB4yqPeWy2j3XOC9oSSabyFseo4vrHF1NfrA3x"
                   "TuuHqjDBF8OvXzkB00iOdSnrhThy6/K0vOkWSeQJLqNw9UEUlnFEIsXuGIIeNCIU1gIeSImsxgw8JYlypGw"
                   "pyhk9ylG9BqRLuh6+f0dTJcgvNXs01emUl6fKjRhLqgwwJD2mN6mTW6ByrBe/F7g9lRAtVo5XudbLkt7+Fq"
                   "T1g7stVlOVP/DPibWF6bVa+TQJckg1uNfTFu9RK5FWqLS1papSmYe3wnnP6mtcuPDJKV4+wbUesXZhWT/xoQ"
                   "INaR916dh+81SkWlmCfY3itTAElfLlexcWLSJl0lSGSLCjdSB+5l/+6bav4yyKapQqM5HJFXbeEc1Oh91meD"
                   "KMTnon570w/MNJVZlYY+jnLeHPQROXaTbYOzsOowPsRWEN38kKfGfByffC1wd8nwBfH/Bd74FvCKBiaF5JKgS"
                   "WC9qKdSL3iP+k1vmG/tnRx4nMoUd4D/IEOZwflZ3Qv7S+TyVd5CKdgT5zdIiI0YxrDWaBA1bmCYa7HNy+paKE"
                   "qac6kzHIRw6AMfbdunSxRMgHY7b071LnT1L/fF9fQv0rWr9GCN+v9OMDSo/CZtgZRt3nlb7DclPpmybbSj9vR"
                   "ufd4+M9Uod4uaCgqAbnLPgI6362oniXX7cVHx1Q/HWt+Osdit+UtZuOp19IuvaEpd5Z3nVuzrUr4lhXuSUrHi"
                   "SvWkAXZCplxSiFBEsxxqaQzKAKEkmCxsDQKzsRlpQhdAciZbFD5S6nuYRuZPn58z/Mxks8UEmxMBK9l8gNPMmE"
                   "wwBJ/1OuHKvgoWQZlOY1PeoqTbyXPP4cLscW6itqBOBkxqCvBAgCIDx7ALsY2pVXjB9DL86jeZwBvfqQ4xHaiH"
                   "sxr61snMtHDJJKOGg4NkyDOZKdMxhkBqwOTPjNUt4jdNabn2kt7uD1Jr6LRuinILwi2Jdg+LJ2fgnvCtj7OZ6js"
                   "I9jeNluRt1hdN5DnTnE8U7LdY63TbY4bkfNTqcddvZy3A7QHYHMIGp7nturbeMxQ/Usx9ebHPf3VK51jv1sR+vA"
                   "ekc8x+3VB3CUJlh/oIC6kluFvUnQsrNrMyaNm33c4+bLyyuoO8nA9YyJjk1AAyvGY9SjbMTVK3bkVUwq5D2U0Ad"
                   "W98rp6k6Bkyn/B/WDLsiEjRz9En0/07wsYWOVooDRRZIoDhYwz45IjekVR+IYUuPXvhWWY4EjBy2cIlvPaxDfVC"
                   "JikB1XxupM/Q/bhJIpChw2Yk9xAj2muqiLr0gN8J0gc7AHrnfmI8wRT5VTrm0N8JrnOKz4F/n22nt1Llr6IZ9w6p"
                   "RJQDdIXzAviVOEHx/bgvSxaw90ZY1K3BLxFPMAqdRwaP7Cror/EzveVTJeuOhvNri4dStjzuNrh6MDaaQGcU8Wge"
                   "shd6tcwA9nkd2Wa1lkh8l2N9BFxxCGpyf7jp0os+2g89db3v6eBoBb3o+ASkKiH0vtjmDuQwLVR3z61ecJ74jTs1"
                   "A5Z4vL3ziCHt1kaEiBDZRcQP93IlWJJ2rrxOpHdrU/RkH23wj4wTtR4uwmMtdHaJdHWPj+SAdQjOJeAqU14f4AeC"
                   "Yy5zwFU9TLqYplQMMJoPE1nrmWYl7opT8zoR2RLoldzPsA+D0FTYb+PfjQJzgt2BeVx7pkkghMa56wHns9HD+Fyx"
                   "VLqjf2LaD+h+GbHiLG65mYEcsoFQUtS2uI/e92vrdDX3zj2Ya1/tTzo9V9TYB7cN0B5ZUeHGzIl0Rvsr6fzVrr+y"
                   "p8l4+R7ZCLcic6WOF3Wq5X+G2TnZ263529x9Lw54L51uGzaNZDrhKoupKXEtWsR1UOrfufqwSxflFS3KLjnd5ueu"
                   "anz3q7neGie2cS8HcBin/BL8U8U/AL0XOSX+jt75P82r6+RIV6DoZDXW14oKMNz5rR2TA6fr6j3WG52dFumrjvsG"
                   "sp7dAH12j5wbWz+sG1vfOD6+m3b/8HQd/FwVgXAAA=",
     'compressionMethod': 'gzip'}


@pytest.fixture
def aws_provider_config_with_secrets():
    return {
            '__end_line__': 12,
            '__start_line__': 7,
            'access_key': ['AKIAIOSFODNN7EXAMPLE'],
            'alias': ['plain_text_access_keys_provider'],
            'region': ['us-west-1'],
            'secret_key': ['wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'],
            'CKV_AWS_41_secret_access_key': 'AKIAIOSFODNN7EXAMPLE',
            'CKV_AWS_41_secret_secret_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
            }


@pytest.fixture
def aws_provider_lines_with_secrets():
    return [(7, 'provider "aws" {\n'),
            (8, '  alias      = "plain_text_access_keys_provider"\n'),
            (9, '  region     = "us-west-1"\n'),
            (10, '  access_key = "AKIAIOSFODNN7EXAMPLE"\n'),
            (11, '  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"\n'),
            (12, '}\n')]


@pytest.fixture
def aws_provider_lines_without_secrets():
    return [(7, 'provider "aws" {\n'),
            (8, '  alias      = "plain_text_access_keys_provider"\n'),
            (9, '  region     = "us-west-1"\n'),
            (10, '  access_key = "AKIAI**********"\n'),
            (11, '  secret_key = "wJalrX**********"\n'),
            (12, '}\n')]


@pytest.fixture
def tfplan_resource_config_with_secrets():
    return {
        'content_type': [''],
        'expiration_date': [None],
        'id': ['https://test-123-abcdse-02.vault.azure.net/secrets/test-123-abcdse-02-primary-key/352d0b63ac873c528170cb366b570da5'],
        'key_vault_id': ['/subscriptions/resourceGroups/'],
        'name': ['test-123-abcdse-02-primary-key'],
        'not_before_date': [None],
        'resource_id': ['/subscriptions/resourceGroups/'],
        'resource_versionless_id': ['/subscriptions/resourceGroups/'],
        'tags': [{'__startline__': 45, '__endline__': 45, 'start_line': 44, 'end_line': 44}],
        'timeouts': [None],
        'value': ['IClnjeTb8fgd14LyV9m1qG0xvFfUyQY3qHq/slUIrk5='],
        'version': ['123d0b12ab123c123456ab123e120bc1'],
        'versionless_id': ['https://test-123-abcdse-02.vault.azure.net/secrets/test-123-abcdse-02'],
        '__startline__': [35],
        '__endline__': [50],
        'start_line': [34],
        'end_line': [49],
        '__address__': 'module.test.azurerm_key_vault_secret.te_primary_key["test-123-abcdse-02"]'}


@pytest.fixture
def tfplan_resource_lines_with_secrets():
    return [(35, '                            {\n'),
            (36, '                                "content_type": "",\n'),
            (37, '                                "expiration_date": null,\n'),
            (38, '                                "id": "https://test-123-abcdse-02.vault.azure.net/secrets/test-123-abcdse-02-primary-key/352d0b63ac873c528170cb366b570da5",\n'),
            (39, '                                "key_vault_id": "abcd/subscriptions/123/resourceGroups/abcd",\n'),
            (40, '                                "name": "test-123-abcdse-02-primary-key",\n'),
            (41, '                                "not_before_date": null,\n'),
            (42, '                                "resource_id": "abcd/subscriptions/123/resourceGroups/abcd",\n'),
            (43, '                                "resource_versionless_id": "abcd/subscriptions/123/resourceGroups/abcd",\n'),
            (44, '                                "tags":\n'),
            (45, '                                {},\n'),
            (46, '                                "timeouts": null,\n'),
            (47, '                                "value": "IClnjeTb8fgd14LyV9m1qG0xvFfUyQY3qHq/slUIrk5=",\n'),
            (48, '                                "version": "123d0b12ab123c123456ab123e120bc1",\n'),
            (49, '                                "versionless_id": "https://test-123-abcdse-02.vault.azure.net/secrets/test-123-abcdse-02"\n')]


@pytest.fixture
def tfplan_resource_lines_without_secrets():
    return [(35, '                            {\n'),
            (36, '                                "content_type": "",\n'),
            (37, '                                "expiration_date": null,\n'),
            (38, '                                "id": "https://test-123-abcdse-02.vault.azure.net/secrets/test-123-abcdse-02-primary-key/352d0b63ac873c528170cb366b570da5",\n'),
            (39, '                                "key_vault_id": "abcd/subscriptions/123/resourceGroups/abcd",\n'),
            (40, '                                "name": "test-123-abcdse-02-primary-key",\n'),
            (41, '                                "not_before_date": null,\n'),
            (42, '                                "resource_id": "abcd/subscriptions/123/resourceGroups/abcd",\n'),
            (43, '                                "resource_versionless_id": "abcd/subscriptions/123/resourceGroups/abcd",\n'),
            (44, '                                "tags":\n'),
            (45, '                                {},\n'),
            (46, '                                "timeouts": null,\n'),
            (47, '                                "value": "IClnje**********",\n'),
            (48, '                                "version": "123d0b12ab123c123456ab123e120bc1",\n'),
            (49,
             '                                "versionless_id": "https://test-123-abcdse-02.vault.azure.net/secrets/test-123-abcdse-02"\n')]

@pytest.fixture
def tfplan_resource_lines_without_secrets_multiple_keys():
    return [(35, '                            {\n'),
            (36, '                                "content_type": "",\n'),
            (37, '                                "expiration_date": null,\n'),
            (38, '                                "id": "https://test-123-abcdse-02.vault.azure.net/secrets/test-123-abcdse-02-primary-key/352d0b63ac873c528170cb366b570da5",\n'),
            (39, '                                "key_vault_id": "abcd/subscriptions/123/resourceGroups/abcd",\n'),
            (40, '                                "name": "test-123-abcdse-02-primary-key",\n'),
            (41, '                                "not_before_date": null,\n'),
            (42, '                                "resource_id": "abcd/subscriptions/123/resourceGroups/abcd",\n'),
            (43, '                                "resource_versionless_id": "abcd/subscriptions/123/resourceGroups/abcd",\n'),
            (44, '                                "tags":\n'),
            (45, '                                {},\n'),
            (46, '                                "timeouts": null,\n'),
            (47, '                                "value": "IClnje**************************************",\n'),
            (48, '                                "version": "123d0b**************************",\n'),

            (49,
             '                                "versionless_id": "https://test-123-abcdse-02.vault.azure.net/secrets/test-123-abcdse-02"\n')]
