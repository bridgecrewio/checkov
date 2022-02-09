import logging
import requests
import re

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.severities import Severities
from checkov.common.util.data_structures_utils import merge_dicts
from checkov.common.util.http_utils import get_default_get_headers, get_auth_header, extract_error_message

# service-provider::service-name::data-type-name
CFN_RESOURCE_TYPE_IDENTIFIER = re.compile(r"^[a-zA-Z0-9]+::[a-zA-Z0-9]+::[a-zA-Z0-9]+$")


class RepoConfigIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration):
        super().__init__(bc_integration, order=0)
        self.skip_paths = []
        self.code_review_threshold = None
        self.code_review_skip_policies = []

    def is_valid(self) -> bool:
        return (
            self.bc_integration.is_integration_configured()
            and not self.bc_integration.skip_download
            and not self.integration_feature_failures
        )

    def pre_scan(self):
        try:
            if not self.bc_integration.customer_run_config_response:
                logging.warning('In the pre-scan for repo config settings, but nothing was fetched from the platform')
                self.integration_feature_failures = True
                return

            vcs_config = self.bc_integration.customer_run_config_response['vcsConfig']

            for section in vcs_config['scannedFiles']['sections']:
                repos = section['repos']
                if any(repo for repo in repos if self.bc_integration.repo_matches(repo)):
                    logging.debug(f'Found path exclusion config section for repo: {section}')
                    self.skip_paths += section['rule']['excludePaths']

            self.skip_paths = set(self.skip_paths)
            logging.debug(f'Skipping the following paths based on platform settings: {self.skip_paths}')

            code_reviews = vcs_config['codeReviews']
            if code_reviews['enabled']:
                for section in code_reviews['sections']:
                    repos = section['repos']
                    if any(repo for repo in repos if self.bc_integration.repo_matches(repo)):
                        logging.debug(f'Found code reviews config section for repo: {section}')
                        severity_level = section['rule']['severityLevel']
                        if not self.code_review_threshold or Severities[severity_level].level < self.code_review_threshold.level:
                            logging.debug(f'Severity threshold of {severity_level} is lower than {self.code_review_threshold}')
                            self.code_review_threshold = Severities[severity_level]
                        self.code_review_skip_policies += section['rule']['excludePolicies']
                self.code_review_skip_policies = set(self.code_review_skip_policies)
                logging.debug(f'Found the following code review policy exclusions: {self.code_review_skip_policies}')
            else:
                logging.info('Code reviews are disabled in the platform, so will not be applied to this run')
        except Exception as e:
            self.integration_feature_failures = True
            logging.debug(f'{e} \nScanning without applying custom policies from the platform.', exc_info=True)

    @staticmethod
    def _convert_raw_check(policy):
        metadata = {
            'id': policy['id'],
            'name': policy['title'],
            'category': policy['category'],
            'scope': {
                'provider': policy['provider']
            }
        }
        check = {
            'metadata': metadata,
            'definition': policy['conditionQuery']
        }
        return check


integration = RepoConfigIntegration(bc_integration)
