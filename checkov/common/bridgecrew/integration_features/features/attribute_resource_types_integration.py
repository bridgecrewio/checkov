from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, List

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration


ALL_TYPES = '__all__'


class AttributeResourceTypesIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration: BcPlatformIntegration) -> None:
        super().__init__(bc_integration=bc_integration, order=1)  # must be after policy metadata
        self.attribute_resources: Dict[str, Dict[str, List[str]]] = {}

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

            logging.debug(f'Start time of processing API output: {datetime.datetime.now().timestamp()}')

            resourceDefinitions = self.bc_integration.customer_run_config_response.get('resourceDefinitions')
            filterAttributes: Dict[str, List[str]] = resourceDefinitions.get('filterAttributes')
            resourceTypes: Dict[str, Dict[str, Any]] = resourceDefinitions.get('resourceTypes')

            for attribute, providers in filterAttributes.items():
                self.attribute_resources[attribute] = {p: [] for p in providers}
                self.attribute_resources[attribute][ALL_TYPES] = []

            for resource, properties in resourceTypes.items():
                provider = properties['provider'].lower()
                if provider == 'ali':
                    # 'alibabacloud' is the actual provider value in the custom policy, but the resource provider is just 'ali'
                    provider = 'alibabacloud'
                for attribute in properties['arguments']:
                    if '.' in attribute:
                        attribute = attribute[:attribute.index('.')]
                    if attribute not in filterAttributes or provider not in filterAttributes[attribute]:
                        continue
                    self.attribute_resources[attribute][provider].append(resource)
                    self.attribute_resources[attribute][ALL_TYPES].append(resource)

            logging.debug(f'End time of processing API output: {datetime.datetime.now().timestamp()}')

        except Exception:
            self.integration_feature_failures = True
            logging.debug("Scanning without handling 'all' resource type policies.", exc_info=True)

    def get_attribute_resource_types(self, solver: Dict[str, Any], provider: Optional[str] = None) -> Optional[List[str]]:
        attr = solver.get('attribute')
        if not attr:
            return None
        if '.' in attr:
            attr = attr[0:attr.index('.')]

        resource_types = self.attribute_resources.get(attr, None)
        if not resource_types:
            return None

        return resource_types.get(provider or '__all__')


integration = AttributeResourceTypesIntegration(bc_integration)
