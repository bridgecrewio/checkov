from checkov.cloudformation.checks.resource.registry import cfn_registry
from checkov.cloudformation.parser.node import dict_node


def get_resource_tags(entity, registry=cfn_registry):
    entity_details = registry.extract_entity_details(entity)
    entity_config = entity_details[-1]

    properties = entity_config.get('Properties')
    if properties:
        tags = properties.get('Tags')
        if tags:
            tag_dict = {tag['Key']: str(get_entity_value_as_string(tag['Value'])) for tag in tags}
            return tag_dict

    return None


def get_entity_value_as_string(value):
    if type(value) in (dict, dict_node):
        value = list(value.values())[0]
        # If the value is a long-form function, then the first element is the template string (technically str_node)
        # Otherwise the dict value is the template string
        if type(value) == list:
            return value[0]
        else:
            return value
    else:
        return value
