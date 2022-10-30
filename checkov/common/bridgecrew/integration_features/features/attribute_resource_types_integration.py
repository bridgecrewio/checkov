from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, List, Set

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.output.report import Report
from checkov.common.typing import _ResourceDefinitions, _ResourceTypes

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration


ALL_TYPES = '__all__'


class AttributeResourceTypesIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration: BcPlatformIntegration) -> None:
        super().__init__(bc_integration=bc_integration, order=3)  # must be after policy metadata
        self.attribute_resources: Dict[str, Dict[str, List[str]]] = {}
        self.provider_resources: Dict[str, List[str]] = {}

    def is_valid(self) -> bool:
        return (
            self.bc_integration.is_integration_configured()
            and not self.bc_integration.skip_download
            and not self.integration_feature_failures
        )

    def pre_runner(self) -> None:
        # not used
        pass

    def post_runner(self, scan_reports: Report) -> None:
        # not used
        pass

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

    def get_attribute_resource_types(self, solver: Dict[str, Any], provider: Optional[str] = None) -> Optional[List[str]]:
        attr = solver.get('attribute')
        if not attr:
            return None
        if '.' in attr:
            attr = attr[0:attr.index('.')]

        resource_types = self.attribute_resources.get(attr, None)
        if not resource_types:
            return None

        return resource_types.get(provider or ALL_TYPES)

    def _build_attribute_resource_map(self, resource_definitions: _ResourceDefinitions) -> None:
        """
        Builds two internal maps to be referenced during policy evaluation.

        1. self.attribute_resources - a mapping of attributes to providers to resource types in that provider
        that have the attribute.

        Example:
        {
          tags: {
            aws: [
              aws_s3_bucket,
              aws_instance,
              ...
            ],
            azure: [
              azurerm_storage_account,
              ...
            ],
            __all__: [
              aws_s3_bucket,
              aws_instance,
              ...
              azurerm_storage_account,
              ...
            ]
          },
          labels:
            gcp: [
              google_sql_database_instance,
              ...
            ],
            __all__: [...]
          },
          freeform_tags: {
            oci:
            ...etc
        }

        Later, whenever we see a policy condition with "all" resource types and one of these attributes, we can
        replace the resource list with the list from the given provider, or __all__ if we do not know the provider

        2.  self.provider_resources - A mapping of providers to all resource types for that provider (irrespective of attributes)

        :param resource_definitions: returned from the platform, contains a map of resource types to their metadata
        (provider and attributes), and a map of attribute names to their providers that we should substitute whenever
        we see "all" resource types in a yaml policy
        :return:
        """

        filter_attributes: Dict[str, List[str]] = resource_definitions['filterAttributes']
        resource_types: Dict[str, _ResourceTypes] = resource_definitions['resourceTypes']

        attribute_resources: Dict[str, Dict[str, Set[str]]] = {}

        for attribute, providers in filter_attributes.items():
            attribute_resources[attribute] = {p: set() for p in providers}
            attribute_resources[attribute][ALL_TYPES] = set()

        for resource, properties in resource_types.items():
            provider = properties['provider'].lower()
            if provider == 'ali':
                # 'alibabacloud' is the actual provider value in the custom policy, but the resource provider is just 'ali'
                provider = 'alibabacloud'

            if provider in self.provider_resources:
                self.provider_resources[provider].append(resource)
            else:
                self.provider_resources[provider] = [resource]

            for attribute in properties['arguments']:
                if '.' in attribute:
                    attribute = attribute[:attribute.index('.')]
                if attribute not in filter_attributes or provider not in filter_attributes[attribute]:
                    continue
                attribute_resources[attribute][provider].add(resource)
                attribute_resources[attribute][ALL_TYPES].add(resource)

        # convert to list
        self.attribute_resources = {
            attribute: {
                provider: list(resources) for provider, resources in provider_map.items()
            } for attribute, provider_map in attribute_resources.items()
        }


integration = AttributeResourceTypesIntegration(bc_integration)
