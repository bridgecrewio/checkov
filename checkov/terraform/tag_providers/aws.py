from checkov.common.util.type_forcers import force_dict


def get_resource_tags(entity_config):
    return force_dict(entity_config.get('tags'))
