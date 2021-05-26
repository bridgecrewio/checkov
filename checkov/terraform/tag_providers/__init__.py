from typing import Dict, Any, Optional

from checkov.terraform.tag_providers import aws
from checkov.terraform.tag_providers import azure
from checkov.terraform.tag_providers import gcp

provider_tag_mapping = {"aws": aws.get_resource_tags, "azure": azure.get_resource_tags, "gcp": gcp.get_resource_tags}


def get_resource_tags(resource_type: str, entity_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(entity_config, dict):
        return None

    if "_" not in resource_type:
        return None  # probably not a resource block
    provider = resource_type[: resource_type.index("_")]
    provider_tag_function = provider_tag_mapping.get(provider)
    if provider_tag_function:
        return provider_tag_function(entity_config)
    else:
        return None
