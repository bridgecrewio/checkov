from __future__ import annotations

from typing import Optional

FOREACH_KEY_SEPERATOR = '["'
FOREACH_KEY_ENDER = '"]'
COUNT_KEY_SEPERATOR = "["
COUNT_KEY_ENDER = "]"


def get_terraform_foreach_or_count_key(resource_id: str) -> Optional[str]:
    sanitized_id = get_sanitized_terraform_resource_id(resource_id)
    if sanitized_id == resource_id:
        return None
    key = resource_id.split(sanitized_id)[-1]
    while key.startswith(FOREACH_KEY_SEPERATOR) and key.endswith(FOREACH_KEY_ENDER):
        key = key[2:-2]
    while key.startswith(COUNT_KEY_SEPERATOR) and key.endswith(COUNT_KEY_ENDER):
        key = key[1:-1]
    return key


def get_sanitized_terraform_resource_id(resource_id: str) -> str:
    if FOREACH_KEY_SEPERATOR in resource_id:
        original_id_parts = resource_id.split(FOREACH_KEY_SEPERATOR, maxsplit=1)
        original_resource_name = original_id_parts[-2]  # As the last item will be the key itself,
        return original_resource_name  # This will be the resource id before the foreach key was added
    elif COUNT_KEY_SEPERATOR in resource_id:
        original_id_parts = resource_id.split(COUNT_KEY_SEPERATOR)
        original_resource_name = original_id_parts[-2]
        return original_resource_name
    return resource_id
