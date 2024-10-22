from checkov.common.vcs.vcs_schema import VCSSchema


class OrganizationSchema(VCSSchema):
    def __init__(self) -> None:
        schema = {
            "title": "Organization Full",
            "description": "Organization Full",
            "type": "object",
            "properties": {
                "login": {
                    "type": "string",
                    "examples": [
                        "github"
                    ]
                },
                "id": {
                    "type": "integer",
                    "examples": [
                        1
                    ]
                },
                "node_id": {
                    "type": "string",
                    "examples": [
                        "MDEyOk9yZ2FuaXphdGlvbjE\u003d"
                    ]
                },
                "url": {
                    "type": "string",
                    "format": "uri",
                    "examples": [
                        "https://api.github.com/orgs/github"
                    ]
                },
                "repos_url": {
                    "type": "string",
                    "format": "uri",
                    "examples": [
                        "https://api.github.com/orgs/github/repos"
                    ]
                },
                "events_url": {
                    "type": "string",
                    "format": "uri",
                    "examples": [
                        "https://api.github.com/orgs/github/events"
                    ]
                },
                "hooks_url": {
                    "type": "string",
                    "examples": [
                        "https://api.github.com/orgs/github/hooks"
                    ]
                },
                "issues_url": {
                    "type": "string",
                    "examples": [
                        "https://api.github.com/orgs/github/issues"
                    ]
                },
                "members_url": {
                    "type": "string",
                    "examples": [
                        "https://api.github.com/orgs/github/members{/member}"
                    ]
                },
                "public_members_url": {
                    "type": "string",
                    "examples": [
                        "https://api.github.com/orgs/github/public_members{/member}"
                    ]
                },
                "avatar_url": {
                    "type": "string",
                    "examples": [
                        "https://github.com/images/error/octocat_happy.gif"
                    ]
                },
                "description": {
                    "type": [
                        "string",
                        "null"
                    ],
                    "examples": [
                        "A great organization"
                    ]
                },
                "name": {
                    "type": "string",
                    "examples": [
                        "github"
                    ]
                },
                "company": {
                    "type": "string",
                    "examples": [
                        "GitHub"
                    ]
                },
                "blog": {
                    "type": "string",
                    "format": "uri",
                    "examples": [
                        "https://github.com/blog"
                    ]
                },
                "location": {
                    "type": "string",
                    "examples": [
                        "San Francisco"
                    ]
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "examples": [
                        "octocat@github.com"
                    ]
                },
                "twitter_username": {
                    "type": [
                        "string",
                        "null"
                    ],
                    "examples": [
                        "github"
                    ]
                },
                "is_verified": {
                    "type": "boolean",
                    "examples": [
                        True
                    ]
                },
                "has_organization_projects": {
                    "type": "boolean",
                    "examples": [
                        True
                    ]
                },
                "has_repository_projects": {
                    "type": "boolean",
                    "examples": [
                        True
                    ]
                },
                "public_repos": {
                    "type": "integer",
                    "examples": [
                        2
                    ]
                },
                "public_gists": {
                    "type": "integer",
                    "examples": [
                        1
                    ]
                },
                "followers": {
                    "type": "integer",
                    "examples": [
                        20
                    ]
                },
                "following": {
                    "type": "integer",
                    "examples": [
                        0
                    ]
                },
                "html_url": {
                    "type": "string",
                    "format": "uri",
                    "examples": [
                        "https://github.com/octocat"
                    ]
                },
                "created_at": {
                    "type": "string",
                    "format": "date-time",
                    "examples": [
                        "2008-01-14T04:33:35Z"
                    ]
                },
                "type": {
                    "type": "string",
                    "examples": [
                        "Organization"
                    ]
                },
                "total_private_repos": {
                    "type": "integer",
                    "examples": [
                        100
                    ]
                },
                "owned_private_repos": {
                    "type": "integer",
                    "examples": [
                        100
                    ]
                },
                "private_gists": {
                    "type": [
                        "integer",
                        "null"
                    ],
                    "examples": [
                        81
                    ]
                },
                "disk_usage": {
                    "type": [
                        "integer",
                        "null"
                    ],
                    "examples": [
                        10000
                    ]
                },
                "collaborators": {
                    "type": [
                        "integer",
                        "null"
                    ],
                    "examples": [
                        8
                    ]
                },
                "billing_email": {
                    "type": [
                        "string",
                        "null"
                    ],
                    "format": "email",
                    "examples": [
                        "org@example.com"
                    ]
                },
                "plan": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "space": {
                            "type": "integer"
                        },
                        "private_repos": {
                            "type": "integer"
                        },
                        "filled_seats": {
                            "type": "integer"
                        },
                        "seats": {
                            "type": "integer"
                        }
                    },
                    "required": [
                        "name",
                        "space",
                        "private_repos"
                    ]
                },
                "default_repository_permission": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
                "members_can_create_repositories": {
                    "type": [
                        "boolean",
                        "null"
                    ],
                    "examples": [
                        True
                    ]
                },
                "two_factor_requirement_enabled": {
                    "type": [
                        "boolean",
                        "null"
                    ],
                    "examples": [
                        True
                    ]
                },
                "members_allowed_repository_creation_type": {
                    "type": "string",
                    "examples": [
                        "all"
                    ]
                },
                "members_can_create_public_repositories": {
                    "type": "boolean",
                    "examples": [
                        True
                    ]
                },
                "members_can_create_private_repositories": {
                    "type": "boolean",
                    "examples": [
                        True
                    ]
                },
                "members_can_create_internal_repositories": {
                    "type": "boolean",
                    "examples": [
                        True
                    ]
                },
                "members_can_create_pages": {
                    "type": "boolean",
                    "examples": [
                        True
                    ]
                },
                "members_can_create_public_pages": {
                    "type": "boolean",
                    "examples": [
                        True
                    ]
                },
                "members_can_create_private_pages": {
                    "type": "boolean",
                    "examples": [
                        True
                    ]
                },
                "members_can_fork_private_repositories": {
                    "type": [
                        "boolean",
                        "null"
                    ],
                    "examples": [
                        False
                    ]
                },
                "web_commit_signoff_required": {
                    "type": "boolean",
                    "examples": [
                        False
                    ]
                },
                "updated_at": {
                    "type": "string",
                    "format": "date-time"
                },
                "advanced_security_enabled_for_new_repositories": {
                    "type": "boolean",
                    "description": "Whether GitHub Advanced Security is enabled for new repositories and repositories transferred to this organization.\n\nThis field is only visible to organization owners or members of a team with the security manager role.",
                    "examples": [
                        False
                    ]
                },
                "dependabot_alerts_enabled_for_new_repositories": {
                    "type": "boolean",
                    "description": "Whether GitHub Advanced Security is automatically enabled for new repositories and repositories transferred to\nthis organization.\n\nThis field is only visible to organization owners or members of a team with the security manager role.",
                    "examples": [
                        False
                    ]
                },
                "dependabot_security_updates_enabled_for_new_repositories": {
                    "type": "boolean",
                    "description": "Whether dependabot security updates are automatically enabled for new repositories and repositories transferred\nto this organization.\n\nThis field is only visible to organization owners or members of a team with the security manager role.",
                    "examples": [
                        False
                    ]
                },
                "dependency_graph_enabled_for_new_repositories": {
                    "type": "boolean",
                    "description": "Whether dependency graph is automatically enabled for new repositories and repositories transferred to this\norganization.\n\nThis field is only visible to organization owners or members of a team with the security manager role.",
                    "examples": [
                        False
                    ]
                },
                "secret_scanning_enabled_for_new_repositories": {
                    "type": "boolean",
                    "description": "Whether secret scanning is automatically enabled for new repositories and repositories transferred to this\norganization.\n\nThis field is only visible to organization owners or members of a team with the security manager role.",
                    "examples": [
                        False
                    ]
                },
                "secret_scanning_push_protection_enabled_for_new_repositories": {
                    "type": "boolean",
                    "description": "Whether secret scanning push protection is automatically enabled for new repositories and repositories\ntransferred to this organization.\n\nThis field is only visible to organization owners or members of a team with the security manager role.",
                    "examples": [
                        False
                    ]
                },
                "secret_scanning_push_protection_custom_link_enabled": {
                    "type": "boolean",
                    "description": "Whether a custom link is shown to contributors who are blocked from pushing a secret by push protection.",
                    "examples": [
                        False
                    ]
                },
                "secret_scanning_push_protection_custom_link": {
                    "type": [
                        "string",
                        "null"
                    ],
                    "description": "An optional URL string to display to contributors who are blocked from pushing a secret.",
                    "examples": [
                        "https://github.com/test-org/test-repo/blob/main/README.md"
                    ]
                }
            },
            "required": [
                "login",
                "url",
                "id",
                "node_id",
                "repos_url",
                "events_url",
                "hooks_url",
                "issues_url",
                "members_url",
                "public_members_url",
                "avatar_url",
                "description",
                "html_url",
                "has_organization_projects",
                "has_repository_projects",
                "public_repos",
                "public_gists",
                "followers",
                "following",
                "type",
                "created_at",
                "updated_at"
            ]
        }
        super().__init__(schema=schema)


schema = OrganizationSchema()
