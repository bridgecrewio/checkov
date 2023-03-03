from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, cast

from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.severities import Severities, get_severity
from checkov.common.checks.base_check_registry import BaseCheckRegistry

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
    from checkov.common.bridgecrew.severities import Severity
    from checkov.common.output.report import Report
    from checkov.common.typing import _BaseRunner


class PolicyMetadataIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration: BcPlatformIntegration) -> None:
        super().__init__(bc_integration=bc_integration, order=0)
        self.check_metadata: dict[str, Any] = {}
        self.bc_to_ckv_id_mapping: dict[str, str] = {}
        self.pc_to_ckv_id_mapping: dict[str, str] = {}
        self.severity_key = 'severity'
        self.filtered_policy_ids: list[str] = []

    def is_valid(self) -> bool:
        return (
            not self.bc_integration.skip_download
            and not self.integration_feature_failures
        )

    def pre_scan(self) -> None:
        try:
            if self.bc_integration.customer_run_config_response:
                self._handle_customer_run_config(self.bc_integration.customer_run_config_response)
                if self.bc_integration.is_prisma_integration():
                    self._handle_customer_prisma_policy_metadata(self.bc_integration.prisma_policies_response)
            elif self.bc_integration.public_metadata_response:
                self._handle_public_metadata(self.bc_integration.public_metadata_response)
            else:
                logging.debug('In the pre-scan for policy metadata, but nothing was fetched from the platform')
                self.integration_feature_failures = True
                return

            all_checks = BaseCheckRegistry.get_all_registered_checks()

            registries = ['terraform', 'cloudformation', 'kubernetes', 'bicep', 'terraform_plan']

            for r in registries:
                registry = get_graph_checks_registry(r)
                registry.load_checks()
                all_checks += registry.checks

            use_prisma_metadata = self.bc_integration.is_prisma_integration()

            if use_prisma_metadata:
                self.severity_key = 'pcSeverity'

            for check in all_checks:
                checkov_id = check.id
                metadata = self.get_policy_metadata(checkov_id)
                if metadata:
                    check.bc_id = metadata.get('id')
                    check.guideline = metadata.get('guideline')

                    # fall back on plain severity if there is no PC severity
                    check.severity = get_severity(metadata.get(self.severity_key, metadata.get('severity')))
                    check.bc_category = metadata.get('category')
                    check.benchmarks = metadata.get('benchmarks')

                    if use_prisma_metadata and metadata.get('descriptiveTitle'):
                        check.name = metadata['descriptiveTitle']
                else:
                    check.bc_id = None
        except Exception:
            self.integration_feature_failures = True
            logging.debug('An error occurred loading policy metadata. Some metadata may be missing from the run.', exc_info=True)

    def get_bc_id(self, checkov_id: str) -> str:
        return cast(str, self.check_metadata.get(checkov_id, {}).get('id'))

    def get_guideline(self, checkov_id: str) -> str:
        return cast(str, self.check_metadata.get(checkov_id, {}).get('guideline'))

    def get_severity(self, checkov_id: str) -> Severity | None:
        severity: str | Severity | None = self.check_metadata.get(checkov_id, {}).get(self.severity_key)
        if not severity:
            severity = self.check_metadata.get(checkov_id, {}).get('severity')
        if severity and isinstance(severity, str):
            return Severities[severity]  # not all runners register their checks in time for being processed above
        return cast(None, severity)

    def get_category(self, checkov_id: str) -> str:
        return cast(str, self.check_metadata.get(checkov_id, {}).get('category'))

    def get_benchmarks(self, checkov_id: str) -> dict[str, list[str]] | None:
        return cast("dict[str, list[str]] | None", self.check_metadata.get(checkov_id, {}).get('benchmarks'))

    def get_prisma_policy_title(self, checkov_id: str) -> str:
        return cast(str, self.check_metadata.get(checkov_id, {}).get('descriptiveTitle'))

    def get_policy_metadata(self, checkov_id: str) -> dict[str, Any] | None:
        return self.check_metadata.get(checkov_id)

    def get_ckv_id_from_bc_id(self, bc_id: str) -> str | None:
        return self.bc_to_ckv_id_mapping.get(bc_id)

    def get_ckv_id_from_pc_id(self, pc_id: str) -> str | None:
        return self.pc_to_ckv_id_mapping.get(pc_id)

    def _handle_public_metadata(self, check_metadata: dict[str, Any]) -> None:
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

    def _handle_customer_run_config(self, run_config: dict[str, Any]) -> None:
        self.check_metadata = run_config['policyMetadata']
        for ckv_id, pol in self.check_metadata.items():
            self.bc_to_ckv_id_mapping[pol['id']] = ckv_id
            if self.bc_integration.is_prisma_integration() and pol.get('pcPolicyId'):
                self.pc_to_ckv_id_mapping[pol['pcPolicyId']] = ckv_id
        # Custom policies are returned in run_config['customPolicies'] rather than run_config['policyMetadata'].
        if 'customPolicies' in run_config:
            for custom_policy in run_config['customPolicies']:
                if 'guideline' in custom_policy:
                    self.check_metadata[custom_policy['id']] = {
                        'guideline': custom_policy['guideline']
                    }
                pc_policy_id = custom_policy.get('pcPolicyId')
                if pc_policy_id:
                    self.pc_to_ckv_id_mapping[pc_policy_id] = custom_policy['id']

    def _handle_customer_prisma_policy_metadata(self, prisma_policy_metadata: list[dict[str, Any]]) -> None:
        if isinstance(prisma_policy_metadata, list):
            for metadata in prisma_policy_metadata:
                logging.debug(f"Parsing filtered_policy_ids from metadata: {json.dumps(metadata)}")
                pc_id = metadata.get('policyId')
                if pc_id:
                    ckv_id = self.get_ckv_id_from_pc_id(pc_id)
                    if ckv_id:
                        self.filtered_policy_ids.append(ckv_id)

    def pre_runner(self, runner: _BaseRunner) -> None:
        # not used
        pass

    def post_runner(self, scan_reports: Report) -> None:
        # not used
        pass

    def post_scan(self, merged_reports: list[Report]) -> None:
        # not used
        pass


integration = PolicyMetadataIntegration(bc_integration)
