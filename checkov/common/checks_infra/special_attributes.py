from typing import Dict, Any, Optional, List
from checkov.common.checks_infra.resource_attribute_filters import attribute_resources


def get_attribute_resource_types(solver: Dict[str, Any], provider: Optional[str] = None) -> Optional[List[str]]:
    attr = solver.get('attribute')
    if not attr:
        return None
    if '.' in attr:
        attr = attr[0:attr.index('.')]

    resource_types = attribute_resources.get(attr, None)
    if not resource_types:
        return None

    return resource_types.get(provider or '__all__')
