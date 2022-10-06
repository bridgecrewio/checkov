from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, List, Set

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration


ALL_TYPES = '__all__'


class AttributeResourceTypesIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration: BcPlatformIntegration) -> None:
        super().__init__(bc_integration=bc_integration, order=1)  # must be after policy metadata
        self.attribute_resources: Dict[str, Dict[str, Set[str]]] = {}

    def is_valid(self) -> bool:
        return (
            self.bc_integration.is_integration_configured()
            and not self.bc_integration.skip_download
            and not self.integration_feature_failures
        )

    def pre_scan(self) -> None:
        try:
            if not self.bc_integration.customer_run_config_response:
                logging.debug('In the pre-scan for attribute resource types, but nothing was fetched from the platform')
                self.integration_feature_failures = True
                return

            if 'resourceDefinitions' not in self.bc_integration.customer_run_config_response:
                # TODO remove - this makes it easier to make sure that platform scans will also work
                logging.debug('resourceDefinitions is not in the run config response - might not be deployed to the platform yet')
                return

            resource_definitions = self.bc_integration.customer_run_config_response.get('resourceDefinitions')
            self._build_attribute_resource_map(resource_definitions)

        except Exception:
            self.integration_feature_failures = True
            logging.debug("Scanning without handling 'all' resource type policies.", exc_info=True)

    def get_attribute_resource_types(self, solver: Dict[str, Any], provider: Optional[str] = None) -> Optional[Set[str]]:
        attr = solver.get('attribute')
        if not attr:
            return None
        if '.' in attr:
            attr = attr[0:attr.index('.')]

        resource_types = self.attribute_resources.get(attr, None)
        if not resource_types:
            return None

        return resource_types.get(provider or '__all__')

    def _build_attribute_resource_map(self, resource_definitions) -> None:
        filter_attributes: Dict[str, List[str]] = resource_definitions.get('filterAttributes')
        resource_types: Dict[str, Dict[str, Any]] = resource_definitions.get('resourceTypes')

        for attribute, providers in filter_attributes.items():
            self.attribute_resources[attribute] = {p: set() for p in providers}
            self.attribute_resources[attribute][ALL_TYPES] = set()

        for resource, properties in resource_types.items():
            provider = properties['provider'].lower()
            if provider == 'ali':
                # 'alibabacloud' is the actual provider value in the custom policy, but the resource provider is just 'ali'
                provider = 'alibabacloud'
            for attribute in properties['arguments']:
                if '.' in attribute:
                    attribute = attribute[:attribute.index('.')]
                if attribute not in filter_attributes or provider not in filter_attributes[attribute]:
                    continue
                self.attribute_resources[attribute][provider].add(resource)
                self.attribute_resources[attribute][ALL_TYPES].add(resource)


integration = AttributeResourceTypesIntegration(bc_integration)
