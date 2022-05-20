import logging
from typing import Optional

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.severities import Severity, Severities


class CodeCategoryConfiguration:
    def __init__(self, soft_fail_threshold: Severity, hard_fail_threshold: Severity):
        self.soft_fail_threshold = soft_fail_threshold
        self.hard_fail_threshold = hard_fail_threshold


class RepoConfigIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration):
        super().__init__(bc_integration, order=0)
        self.skip_paths = []
        self.images_config: Optional[CodeCategoryConfiguration] = None
        self.sca_config: Optional[CodeCategoryConfiguration] = None
        self.secrets_config: Optional[CodeCategoryConfiguration] = None
        self.iac_config: Optional[CodeCategoryConfiguration] = None

    def is_valid(self) -> bool:
        return (
            self.bc_integration.is_integration_configured()
            and not self.bc_integration.skip_download
            and not self.integration_feature_failures
        )

    def pre_scan(self) -> None:
        try:
            if not self.bc_integration.customer_run_config_response:
                logging.debug('In the pre-scan for repo config settings, but nothing was fetched from the platform')
                self.integration_feature_failures = True
                return

            # It is possible that they will have two different and conflicting rules for this repo - one for the VCS
            # integration that matches the value of --repo-id (org/repo), and one for the CLI upload repo (e.g., customer_org/repo).
            # For the skip paths, we can just combine the lists and call it good. For enforcement rules, we will have
            # to decide which rule to take: we can take the lowest severity for each category, or just take one or the other.

            vcs_config = self.bc_integration.customer_run_config_response['vcsConfig']

            for section in vcs_config['scannedFiles']['sections']:
                repos = section['repos']
                if any(repo for repo in repos if self.bc_integration.repo_matches(repo)):
                    logging.debug(f'Found path exclusion config section for repo: {section}')
                    self.skip_paths += section['rule']['excludePaths']

            self.skip_paths = set(self.skip_paths)
            logging.debug(f'Skipping the following paths based on platform settings: {self.skip_paths}')

            enforcement_rules_config = self.bc_integration.customer_run_config_response['enforcementRules']
            rules = enforcement_rules_config['rules']
            default_rule = next(r for r in rules if r['mainRule'] is True)
            other_rules = [r for r in rules if r != default_rule]

            matched_rules = []

            for rule in other_rules:
                if any(repo for repo in rule['repositories'] if self.bc_integration.repo_matches(repo['accountName'])):
                    matched_rules.append(rule)

            if len(matched_rules) > 1:
                logging.warning(f'Found {len(matched_rules)} enforcement rules for the specified repo. This likely means '
                                f'that one rule was created for the VCS repo, and another rule for the CLI repo.')  # TODO explain the behavior
                selected_rule = matched_rules[0]  # TODO temporary
            elif len(matched_rules) == 0:
                logging.info('Did not find any enforcement rules for the specified repo; using the default rule')
                selected_rule = default_rule
            else:
                logging.info('Found exactly one matching enforcement rule for the specified repo')
                selected_rule = matched_rules[0]

            self.images_config = RepoConfigIntegration._get_code_category_object(selected_rule['codeCategories']['IMAGES'])
            self.sca_config = RepoConfigIntegration._get_code_category_object(selected_rule['codeCategories']['OPEN_SOURCE'])
            self.secrets_config = RepoConfigIntegration._get_code_category_object(selected_rule['codeCategories']['SECRETS'])
            self.iac_config = RepoConfigIntegration._get_code_category_object(selected_rule['codeCategories']['IAC'])

        except Exception:
            self.integration_feature_failures = True
            logging.debug("Scanning without applying scanning configs from the platform.", exc_info=True)

    @staticmethod
    def _get_code_category_object(code_category) -> CodeCategoryConfiguration:
        soft_fail_threshold = Severities[code_category['softFailThreshold']]
        hard_fail_threshold = Severities[code_category['hardFailThreshold']]
        return CodeCategoryConfiguration(soft_fail_threshold, hard_fail_threshold)

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
