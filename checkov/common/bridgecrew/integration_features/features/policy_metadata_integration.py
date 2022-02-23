import logging
import re

from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.severities import Severities, get_severity
from checkov.common.checks.base_check_registry import BaseCheckRegistry


class PolicyMetadataIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration):
        super().__init__(bc_integration, order=0)
        self.check_metadata = {}
        self.bc_to_ckv_id_mapping = {}

    def is_valid(self) -> bool:
        return (
            not self.bc_integration.skip_download
            and not self.integration_feature_failures
        )

    def pre_scan(self):
        try:
            if self.bc_integration.customer_run_config_response:
                self._handle_customer_run_config(self.bc_integration.customer_run_config_response)
            elif self.bc_integration.public_metadata_response:
                self._handle_public_metadata(self.bc_integration.public_metadata_response)
            else:
                logging.debug('In the pre-scan for policy metadata, but nothing was fetched from the platform')
                self.integration_feature_failures = True
                return

            all_checks = BaseCheckRegistry.get_all_registered_checks()

            graph_registry = get_graph_checks_registry("terraform")
            graph_registry.load_checks()

            for check in all_checks + graph_registry.checks:
                checkov_id = check.id
                metadata = self.get_policy_metadata(checkov_id)
                if metadata:
                    check.bc_id = metadata.get('id')
                    check.guideline = metadata.get('guideline')
                    check.bc_severity = get_severity(metadata.get('severity'))
                    check.pc_severity = get_severity(metadata.get('pcSeverity'))
                    check.bc_category = metadata.get('category')
                    check.benchmarks = metadata.get('benchmarks')
                    # check.pc_title = metadata.get('pcTitle')  # TODO needs to be deployed to platform
        except Exception as e:
            self.integration_feature_failures = True
            logging.debug(f'{e}\nSome metadata may be missing from the run.', exc_info=True)

    def get_bc_id(self, checkov_id):
        return self.check_metadata.get(checkov_id, {}).get('id')

    def get_guideline(self, checkov_id):
        return self.check_metadata.get(checkov_id, {}).get('guideline')

    def get_severity(self, checkov_id):
        severity = self.check_metadata.get(checkov_id, {}).get('severity')
        if severity and type(severity) == str:
            severity = Severities[severity]  # not all runners register their checks in time for being processed above
        return severity

    def get_category(self, checkov_id):
        return self.check_metadata.get(checkov_id, {}).get('category')

    def get_benchmarks(self, checkov_id):
        return self.check_metadata.get(checkov_id, {}).get('benchmarks')

    def get_policy_metadata(self, checkov_id):
        return self.check_metadata.get(checkov_id)

    def get_ckv_id_from_bc_id(self, bc_id):
        return self.bc_to_ckv_id_mapping.get(bc_id)

    def _handle_public_metadata(self, check_metadata):
        guidelines = check_metadata['guidelines']
        self.bc_to_ckv_id_mapping = check_metadata['idMapping']

        for ckv_id, guideline in guidelines.items():
            self.check_metadata[ckv_id] = {
                'guideline': guideline
            }

        for bc_id, ckv_id in self.bc_to_ckv_id_mapping.items():
            if ckv_id in self.check_metadata:
                self.check_metadata[ckv_id]['id'] = bc_id
            else:
                self.check_metadata[ckv_id] = {
                    'id': bc_id
                }

    def _handle_customer_run_config(self, run_config):
        self.check_metadata = run_config['policyMetadata']

        # Custom policies are returned in run_config['customPolicies'] rather than run_config['policyMetadata'].
        if 'customPolicies' in run_config:
            for custom_policy in run_config['customPolicies']:
                if 'guideline' in custom_policy:
                    self.check_metadata[custom_policy['id']] = {
                        'guideline': custom_policy['guideline']
                    }

        self.bc_to_ckv_id_mapping = {pol['id']: ckv_id for (ckv_id, pol) in self.check_metadata.items()}


integration = PolicyMetadataIntegration(bc_integration)
