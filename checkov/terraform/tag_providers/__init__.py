from typing import Dict, Any, Optional

from checkov.terraform.tag_providers import aws
from checkov.terraform.tag_providers import azure
from checkov.terraform.tag_providers import gcp

provider_tag_mapping = {"aws": aws.get_resource_tags, "azure": azure.get_resource_tags, "gcp": gcp.get_resource_tags,
                        "google": gcp.get_resource_tags}


def get_resource_tags(resource_type: str, entity_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(entity_config, dict):
        return None

    provider_tag = get_provider_tag(resource_type)
    provider_tag_function = provider_tag_mapping.get(provider_tag) if provider_tag else None
    if provider_tag_function:
        return provider_tag_function(entity_config)
    else:
        return None


def get_provider_tag(resource_type: str) -> Optional[str]:
    provider_tag = None
    if 'aws' in resource_type:
        provider_tag = "aws"
    elif 'azure' in resource_type:
        provider_tag = "azure"
    elif 'gcp' in resource_type or 'google' in resource_type:
        provider_tag = "gcp"
    return provider_tag
