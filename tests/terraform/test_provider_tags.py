import pytest

from checkov.terraform.tag_providers import get_provider_tag


@pytest.mark.parametrize("resource_type, expected", [
    ("aws_instance.example", "aws"),
    ("module.test.aws_instance.example", "aws"),
    ("azure_instance.example", "azure"),
    ("google_instance.example", "gcp"),
])
def test_get_provider_tag(resource_type, expected) -> None:
    assert get_provider_tag(resource_type) == expected
