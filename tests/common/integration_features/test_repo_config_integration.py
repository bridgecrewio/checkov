import unittest

from checkov.common.bridgecrew.code_categories import CodeCategoryType, CodeCategoryConfiguration
from checkov.common.bridgecrew.integration_features.features.repo_config_integration import \
    RepoConfigIntegration
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.bridgecrew.severities import BcSeverities, Severities


class TestRepoConfigIntegration(unittest.TestCase):

    def test_integration_valid(self):
        instance = BcPlatformIntegration()
        instance.skip_download = False
        instance.platform_integration_configured = True

        repo_config_integration = RepoConfigIntegration(instance)

        self.assertTrue(repo_config_integration.is_valid())

        instance.skip_download = True
        self.assertFalse(repo_config_integration.is_valid())

        instance.platform_integration_configured = False
        self.assertFalse(repo_config_integration.is_valid())

        instance.skip_download = False
        self.assertFalse(repo_config_integration.is_valid())

        repo_config_integration.integration_feature_failures = True
        self.assertFalse(repo_config_integration.is_valid())

    def test_enforcement_rule_default(self):
        enforcement_rule_config = {
            "rules": [
                {
                    "id": "1",
                    "creationDate": "2022-05-02T12:18:27.379Z",
                    "name": "Security default findings",
                    "createdBy": "Bridgecrew",
                    "mainRule": True,
                    "editable": True,
                    "codeCategories": {
                        "LICENSES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "VULNERABILITIES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "IAC": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "SECRETS": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "BUILD_INTEGRITY": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        }
                    },
                    "repositories": []
                },
            ],
            "accountsNotInMainRule": []
        }

        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        repo_config_integration = RepoConfigIntegration(instance)
        repo_config_integration._set_enforcement_rules(enforcement_rule_config)
        self.assertEqual(repo_config_integration.enforcement_rule['id'], '1')

    def test_enforcement_rule_default_non_matching(self):
        enforcement_rule_config = {
            "rules": [
                {
                    "id": "1",
                    "creationDate": "2022-05-02T12:18:27.379Z",
                    "name": "Security default findings",
                    "createdBy": "Bridgecrew",
                    "mainRule": True,
                    "editable": True,
                    "codeCategories": {
                        "LICENSES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "VULNERABILITIES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "IAC": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "SECRETS": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "BUILD_INTEGRITY": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        }
                    },
                    "repositories": []
                },
                {
                    "id": "2",
                    "creationDate": "2022-05-02T12:18:27.379Z",
                    "name": "rule2",
                    "createdBy": "Bridgecrew",
                    "mainRule": False,
                    "editable": True,
                    "codeCategories": {
                        "LICENSES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "VULNERABILITIES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "IAC": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "SECRETS": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "BUILD_INTEGRITY": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        }
                    },
                    "repositories": [
                        {
                            "accountId": "1234",
                            "accountName": "org/other_repo"
                        }
                    ]
                },
            ],
            "accountsNotInMainRule": []
        }

        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        repo_config_integration = RepoConfigIntegration(instance)
        repo_config_integration._set_enforcement_rules(enforcement_rule_config)
        self.assertEqual(repo_config_integration.enforcement_rule['id'], '1')

    def test_enforcement_rule_simple_match(self):
        enforcement_rule_config = {
            "rules": [
                {
                    "id": "1",
                    "creationDate": "2022-05-02T12:18:27.379Z",
                    "name": "Security default findings",
                    "createdBy": "Bridgecrew",
                    "mainRule": True,
                    "editable": True,
                    "codeCategories": {
                        "LICENSES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "VULNERABILITIES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "IAC": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "SECRETS": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "BUILD_INTEGRITY": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        }
                    },
                    "repositories": []
                },
                {
                    "id": "2",
                    "creationDate": "2022-05-02T12:18:27.379Z",
                    "name": "rule2",
                    "createdBy": "Bridgecrew",
                    "mainRule": False,
                    "editable": True,
                    "codeCategories": {
                        "LICENSES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "VULNERABILITIES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "IAC": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "SECRETS": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "BUILD_INTEGRITY": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        }
                    },
                    "repositories": [
                        {
                            "accountId": "1234",
                            "accountName": "org/repo"
                        }
                    ]
                },
            ],
            "accountsNotInMainRule": []
        }

        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        repo_config_integration = RepoConfigIntegration(instance)
        repo_config_integration._set_enforcement_rules(enforcement_rule_config)
        self.assertEqual(repo_config_integration.enforcement_rule['id'], '2')

    def test_enforcement_rule_cli_repo_match(self):
        enforcement_rule_config = {
            "rules": [
                {
                    "id": "1",
                    "creationDate": "2022-05-02T12:18:27.379Z",
                    "name": "Security default findings",
                    "createdBy": "Bridgecrew",
                    "mainRule": True,
                    "editable": True,
                    "codeCategories": {
                        "LICENSES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "VULNERABILITIES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "IAC": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "SECRETS": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "BUILD_INTEGRITY": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        }
                    },
                    "repositories": []
                },
                {
                    "id": "2",
                    "creationDate": "2022-05-02T12:18:27.379Z",
                    "name": "rule2",
                    "createdBy": "Bridgecrew",
                    "mainRule": False,
                    "editable": True,
                    "codeCategories": {
                        "LICENSES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "VULNERABILITIES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "IAC": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "SECRETS": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "BUILD_INTEGRITY": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        }
                    },
                    "repositories": [
                        {
                            "accountId": "1234",
                            "accountName": "bcorg_org/repo"
                        }
                    ]
                },
            ],
            "accountsNotInMainRule": []
        }

        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        repo_config_integration = RepoConfigIntegration(instance)
        repo_config_integration._set_enforcement_rules(enforcement_rule_config)
        self.assertEqual(repo_config_integration.enforcement_rule['id'], '2')

    def test_enforcement_rule_vcs_and_cli_repo_match(self):
        enforcement_rule_config = {
            "rules": [
                {
                    "id": "1",
                    "creationDate": "2022-05-02T12:18:27.379Z",
                    "name": "Security default findings",
                    "createdBy": "Bridgecrew",
                    "mainRule": True,
                    "editable": True,
                    "codeCategories": {
                        "LICENSES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "VULNERABILITIES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "IAC": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "SECRETS": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "BUILD_INTEGRITY": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        }
                    },
                    "repositories": []
                },
                {
                    "id": "2",
                    "creationDate": "2022-05-02T12:18:27.379Z",
                    "name": "rule2",
                    "createdBy": "Bridgecrew",
                    "mainRule": False,
                    "editable": True,
                    "codeCategories": {
                        "LICENSES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "VULNERABILITIES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "IAC": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "SECRETS": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "BUILD_INTEGRITY": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        }
                    },
                    "repositories": [
                        {
                            "accountId": "1234",
                            "accountName": "bcorg_org/repo"
                        },
                        {
                            "accountId": "5678",
                            "accountName": "org/repo"
                        }
                    ]
                },
            ],
            "accountsNotInMainRule": []
        }

        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        repo_config_integration = RepoConfigIntegration(instance)
        repo_config_integration._set_enforcement_rules(enforcement_rule_config)
        self.assertEqual(repo_config_integration.enforcement_rule['id'], '2')

    def test_enforcement_rule_conflicting_match(self):
        enforcement_rule_config = {
            "rules": [
                {
                    "id": "1",
                    "creationDate": "2022-05-02T12:18:27.379Z",
                    "name": "Security default findings",
                    "createdBy": "Bridgecrew",
                    "mainRule": True,
                    "editable": True,
                    "codeCategories": {
                        "LICENSES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "VULNERABILITIES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "IAC": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "SECRETS": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "BUILD_INTEGRITY": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        }
                    },
                    "repositories": []
                },
                {
                    "id": "2",
                    "creationDate": "2022-05-02T12:18:27.379Z",
                    "name": "rule2",
                    "createdBy": "Bridgecrew",
                    "mainRule": False,
                    "editable": True,
                    "codeCategories": {
                        "LICENSES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "VULNERABILITIES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "IAC": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "SECRETS": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "BUILD_INTEGRITY": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        }
                    },
                    "repositories": [
                        {
                            "accountId": "1234",
                            "accountName": "bcorg_org/repo"
                        }
                    ]
                },
                {
                    "id": "3",
                    "creationDate": "2022-05-02T12:18:27.379Z",
                    "name": "rule3",
                    "createdBy": "Bridgecrew",
                    "mainRule": False,
                    "editable": True,
                    "codeCategories": {
                        "LICENSES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "VULNERABILITIES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "IAC": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "SECRETS": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "BUILD_INTEGRITY": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        }
                    },
                    "repositories": [
                        {
                            "accountId": "5678",
                            "accountName": "org/repo"
                        }
                    ]
                },
            ],
            "accountsNotInMainRule": []
        }

        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        repo_config_integration = RepoConfigIntegration(instance)
        repo_config_integration._set_enforcement_rules(enforcement_rule_config)
        self.assertEqual(repo_config_integration.enforcement_rule['id'], '3')

    def test_enforcement_rule_conflicting_multiple_vcs_match(self):
        enforcement_rule_config = {
            "rules": [
                {
                    "id": "1",
                    "creationDate": "2022-05-02T12:18:27.379Z",
                    "name": "Security default findings",
                    "createdBy": "Bridgecrew",
                    "mainRule": True,
                    "editable": True,
                    "codeCategories": {
                        "LICENSES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "VULNERABILITIES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "IAC": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "SECRETS": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "BUILD_INTEGRITY": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        }
                    },
                    "repositories": []
                },
                {
                    "id": "2",
                    "creationDate": "2022-05-02T12:18:27.379Z",
                    "name": "rule2",
                    "createdBy": "Bridgecrew",
                    "mainRule": False,
                    "editable": True,
                    "codeCategories": {
                        "LICENSES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "VULNERABILITIES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "IAC": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "SECRETS": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "BUILD_INTEGRITY": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        }
                    },
                    "repositories": [
                        {
                            "accountId": "1234",
                            "accountName": "org/repo"
                        }
                    ]
                },
                {
                    "id": "3",
                    "creationDate": "2022-05-02T12:18:27.379Z",
                    "name": "rule3",
                    "createdBy": "Bridgecrew",
                    "mainRule": False,
                    "editable": True,
                    "codeCategories": {
                        "LICENSES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "VULNERABILITIES": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "CRITICAL",
                            "commentsBotThreshold": "LOW"
                        },
                        "IAC": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "SECRETS": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        },
                        "BUILD_INTEGRITY": {
                            "softFailThreshold": "LOW",
                            "hardFailThreshold": "LOW",
                            "commentsBotThreshold": "LOW"
                        }
                    },
                    "repositories": [
                        {
                            "accountId": "5678",
                            "accountName": "org/repo"
                        }
                    ]
                },
            ],
            "accountsNotInMainRule": []
        }

        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        repo_config_integration = RepoConfigIntegration(instance)
        repo_config_integration._set_enforcement_rules(enforcement_rule_config)
        self.assertEqual(repo_config_integration.enforcement_rule['id'], '2')

    def test_enforcement_rule_constants(self):
        # tests to ensure that the correct constants get updated as rules and runners change
        module_keys = [e.value for e in CodeCategoryType]
        self.assertEqual(set(module_keys), {'IAC', 'SECRETS', 'VULNERABILITIES', 'LICENSES', 'BUILD_INTEGRITY', 'WEAKNESSES'})

    def test_global_soft_fail(self):
        self.assertFalse(CodeCategoryConfiguration('', Severities[BcSeverities.LOW], Severities[BcSeverities.LOW]).is_global_soft_fail())
        self.assertFalse(CodeCategoryConfiguration('', Severities[BcSeverities.LOW], Severities[BcSeverities.MEDIUM]).is_global_soft_fail())
        self.assertFalse(CodeCategoryConfiguration('', Severities[BcSeverities.LOW], Severities[BcSeverities.HIGH]).is_global_soft_fail())
        self.assertFalse(CodeCategoryConfiguration('', Severities[BcSeverities.LOW], Severities[BcSeverities.CRITICAL]).is_global_soft_fail())
        self.assertFalse(CodeCategoryConfiguration('', Severities[BcSeverities.LOW], Severities[BcSeverities.INFO]).is_global_soft_fail())
        self.assertFalse(CodeCategoryConfiguration('', Severities[BcSeverities.LOW], Severities[BcSeverities.MODERATE]).is_global_soft_fail())
        self.assertTrue(CodeCategoryConfiguration('', Severities[BcSeverities.LOW], Severities[BcSeverities.OFF]).is_global_soft_fail())

    def test_skip_paths_empty(self):
        vcs_config = {
            "scannedFiles": {
                "sections": [
                    {
                        "repos": [
                            "org/repo"
                        ],
                        "rule": {
                            "excludePaths": []
                        },
                        "isDefault": True
                    }
                ]
            }
        }

        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        repo_config_integration = RepoConfigIntegration(instance)
        repo_config_integration._set_exclusion_paths(vcs_config)
        self.assertEqual(repo_config_integration.skip_paths, set())

    def test_skip_paths_non_empty(self):
        vcs_config = {
            "scannedFiles": {
                "sections": [
                    {
                        "repos": [
                            "org/repo"
                        ],
                        "rule": {
                            "excludePaths": [
                                "a/b"
                            ]
                        },
                        "isDefault": True
                    }
                ]
            }
        }

        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        repo_config_integration = RepoConfigIntegration(instance)
        repo_config_integration._set_exclusion_paths(vcs_config)
        self.assertEqual(repo_config_integration.skip_paths, {'a/b'})

    def test_skip_paths_non_matching(self):
        vcs_config = {
            "scannedFiles": {
                "sections": [
                    {
                        "repos": [
                            "org/other_repo"
                        ],
                        "rule": {
                            "excludePaths": [
                                "a/b"
                            ]
                        },
                        "isDefault": True
                    }
                ]
            }
        }

        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        repo_config_integration = RepoConfigIntegration(instance)
        repo_config_integration._set_exclusion_paths(vcs_config)
        self.assertEqual(repo_config_integration.skip_paths, set())

    def test_skip_paths_no_repos(self):
        vcs_config = {
            "scannedFiles": {
                "sections": [
                    {
                        "repos": [],
                        "rule": {
                            "excludePaths": []
                        },
                        "isDefault": True
                    }
                ]
            }
        }

        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        repo_config_integration = RepoConfigIntegration(instance)
        repo_config_integration._set_exclusion_paths(vcs_config)
        self.assertEqual(repo_config_integration.skip_paths, set())

    def test_skip_paths_multiple_one_match(self):
        vcs_config = {
            "scannedFiles": {
                "sections": [
                    {
                        "repos": [
                            "org/repo"
                        ],
                        "rule": {
                            "excludePaths": [
                                "a/b"
                            ]
                        },
                        "isDefault": True
                    },
                    {
                        "repos": [
                            "org/other_repo"
                        ],
                        "rule": {
                            "excludePaths": [
                                "x/y"
                            ]
                        },
                        "isDefault": False
                    }
                ]
            }
        }

        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        repo_config_integration = RepoConfigIntegration(instance)
        repo_config_integration._set_exclusion_paths(vcs_config)
        self.assertEqual(repo_config_integration.skip_paths, {'a/b'})

    def test_skip_paths_multiple_match(self):
        vcs_config = {
            "scannedFiles": {
                "sections": [
                    {
                        "repos": [
                            "org/repo"
                        ],
                        "rule": {
                            "excludePaths": [
                                "a/b"
                            ]
                        },
                        "isDefault": True
                    },
                    {
                        "repos": [
                            "bcorg_org/repo"
                        ],
                        "rule": {
                            "excludePaths": [
                                "x/y"
                            ]
                        },
                        "isDefault": False
                    }
                ]
            }
        }

        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        repo_config_integration = RepoConfigIntegration(instance)
        repo_config_integration._set_exclusion_paths(vcs_config)
        self.assertEqual(repo_config_integration.skip_paths, {'a/b', "x/y"})


if __name__ == '__main__':
    unittest.main()
