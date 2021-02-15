import checkov.terraform.tag_providers.aws
import checkov.terraform.tag_providers.azure
import checkov.terraform.tag_providers.gcp

provider_tag_mapping = {
    'aws': aws.get_resource_tags,
    'azure': azure.get_resource_tags,
    'gcp': gcp.get_resource_tags
}


def get_resource_tags(resource_type, entity_config):
    if not isinstance(entity_config, dict):
        return None

    if '_' not in resource_type:
        return None  # probably not a resource block
    provider = resource_type[:resource_type.index('_')]
    provider_tag_function = provider_tag_mapping.get(provider)
    if provider_tag_function:
        return provider_tag_function(entity_config)
    else:
        return None
