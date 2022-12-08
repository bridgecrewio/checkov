from checkov.common.vcs.vcs_schema import VCSSchema


class BranchSchema(VCSSchema):
    def __init__(self) -> None:
        schema = {
            "title": "Branch With Protection",
            "description": "Branch With Protection",
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "commit": {
                    "title": "Commit",
                    "description": "Commit",
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "format": "uri"
                        },
                        "sha": {
                            "type": "string"
                        },
                        "node_id": {
                            "type": "string"
                        },
                        "html_url": {
                            "type": "string",
                            "format": "uri"
                        },
                        "comments_url": {
                            "type": "string",
                            "format": "uri",
                            "examples": [
                                "https://api.github.com/repos/octocat/Hello-World/commits/6dcb09b5b57875f334f61aebed695e2e4193db5e/comments"
                            ]
                        },
                        "commit": {
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "format": "uri",
                                    "examples": [
                                        "https://api.github.com/repos/octocat/Hello-World/commits/6dcb09b5b57875f334f61aebed695e2e4193db5e"
                                    ]
                                },
                                "author": {
                                    "anyOf": [
                                        {
                                            "type": "null"
                                        },
                                        {
                                            "title": "Git User",
                                            "description": "Metaproperties for Git author/committer information.",
                                            "type": "object",
                                            "properties": {
                                                "name": {
                                                    "type": "string",
                                                    "examples": [
                                                        "\"Chris Wanstrath\""
                                                    ]
                                                },
                                                "email": {
                                                    "type": "string",
                                                    "examples": [
                                                        "\"chris@ozmm.org\""
                                                    ]
                                                },
                                                "date": {
                                                    "type": "string",
                                                    "examples": [
                                                        "\"2007-10-29T02:42:39.000-07:00\""
                                                    ]
                                                }
                                            }
                                        }
                                    ]
                                },
                                "committer": {
                                    "anyOf": [
                                        {
                                            "type": "null"
                                        },
                                        {
                                            "title": "Git User",
                                            "description": "Metaproperties for Git author/committer information.",
                                            "type": "object",
                                            "properties": {
                                                "name": {
                                                    "type": "string",
                                                    "examples": [
                                                        "\"Chris Wanstrath\""
                                                    ]
                                                },
                                                "email": {
                                                    "type": "string",
                                                    "examples": [
                                                        "\"chris@ozmm.org\""
                                                    ]
                                                },
                                                "date": {
                                                    "type": "string",
                                                    "examples": [
                                                        "\"2007-10-29T02:42:39.000-07:00\""
                                                    ]
                                                }
                                            }
                                        }
                                    ]
                                },
                                "message": {
                                    "type": "string",
                                    "examples": [
                                        "Fix all the bugs"
                                    ]
                                },
                                "comment_count": {
                                    "type": "integer",
                                    "examples": [
                                        0
                                    ]
                                },
                                "tree": {
                                    "type": "object",
                                    "properties": {
                                        "sha": {
                                            "type": "string",
                                            "examples": [
                                                "827efc6d56897b048c772eb4087f854f46256132"
                                            ]
                                        },
                                        "url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://api.github.com/repos/octocat/Hello-World/tree/827efc6d56897b048c772eb4087f854f46256132"
                                            ]
                                        }
                                    },
                                    "required": [
                                        "sha",
                                        "url"
                                    ]
                                },
                                "verification": {
                                    "title": "Verification",
                                    "type": "object",
                                    "properties": {
                                        "verified": {
                                            "type": "boolean"
                                        },
                                        "reason": {
                                            "type": "string"
                                        },
                                        "payload": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        },
                                        "signature": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        }
                                    },
                                    "required": [
                                        "verified",
                                        "reason",
                                        "payload",
                                        "signature"
                                    ]
                                }
                            },
                            "required": [
                                "author",
                                "committer",
                                "comment_count",
                                "message",
                                "tree",
                                "url"
                            ]
                        },
                        "author": {
                            "anyOf": [
                                {
                                    "type": "null"
                                },
                                {
                                    "title": "Simple User",
                                    "description": "A GitHub user.",
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        },
                                        "email": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        },
                                        "login": {
                                            "type": "string",
                                            "examples": [
                                                "octocat"
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
                                                "MDQ6VXNlcjE="
                                            ]
                                        },
                                        "avatar_url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://github.com/images/error/octocat_happy.gif"
                                            ]
                                        },
                                        "gravatar_id": {
                                            "type": [
                                                "string",
                                                "null"
                                            ],
                                            "examples": [
                                                "41d064eb2195891e12d0413f63227ea7"
                                            ]
                                        },
                                        "url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://api.github.com/users/octocat"
                                            ]
                                        },
                                        "html_url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://github.com/octocat"
                                            ]
                                        },
                                        "followers_url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://api.github.com/users/octocat/followers"
                                            ]
                                        },
                                        "following_url": {
                                            "type": "string",
                                            "examples": [
                                                "https://api.github.com/users/octocat/following{/other_user}"
                                            ]
                                        },
                                        "gists_url": {
                                            "type": "string",
                                            "examples": [
                                                "https://api.github.com/users/octocat/gists{/gist_id}"
                                            ]
                                        },
                                        "starred_url": {
                                            "type": "string",
                                            "examples": [
                                                "https://api.github.com/users/octocat/starred{/owner}{/repo}"
                                            ]
                                        },
                                        "subscriptions_url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://api.github.com/users/octocat/subscriptions"
                                            ]
                                        },
                                        "organizations_url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://api.github.com/users/octocat/orgs"
                                            ]
                                        },
                                        "repos_url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://api.github.com/users/octocat/repos"
                                            ]
                                        },
                                        "events_url": {
                                            "type": "string",
                                            "examples": [
                                                "https://api.github.com/users/octocat/events{/privacy}"
                                            ]
                                        },
                                        "received_events_url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://api.github.com/users/octocat/received_events"
                                            ]
                                        },
                                        "type": {
                                            "type": "string",
                                            "examples": [
                                                "User"
                                            ]
                                        },
                                        "site_admin": {
                                            "type": "boolean"
                                        },
                                        "starred_at": {
                                            "type": "string",
                                            "examples": [
                                                "\"2020-07-09T00:17:55Z\""
                                            ]
                                        }
                                    },
                                    "required": [
                                        "avatar_url",
                                        "events_url",
                                        "followers_url",
                                        "following_url",
                                        "gists_url",
                                        "gravatar_id",
                                        "html_url",
                                        "id",
                                        "node_id",
                                        "login",
                                        "organizations_url",
                                        "received_events_url",
                                        "repos_url",
                                        "site_admin",
                                        "starred_url",
                                        "subscriptions_url",
                                        "type",
                                        "url"
                                    ]
                                }
                            ]
                        },
                        "committer": {
                            "anyOf": [
                                {
                                    "type": "null"
                                },
                                {
                                    "title": "Simple User",
                                    "description": "A GitHub user.",
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        },
                                        "email": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        },
                                        "login": {
                                            "type": "string",
                                            "examples": [
                                                "octocat"
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
                                                "MDQ6VXNlcjE="
                                            ]
                                        },
                                        "avatar_url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://github.com/images/error/octocat_happy.gif"
                                            ]
                                        },
                                        "gravatar_id": {
                                            "type": [
                                                "string",
                                                "null"
                                            ],
                                            "examples": [
                                                "41d064eb2195891e12d0413f63227ea7"
                                            ]
                                        },
                                        "url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://api.github.com/users/octocat"
                                            ]
                                        },
                                        "html_url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://github.com/octocat"
                                            ]
                                        },
                                        "followers_url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://api.github.com/users/octocat/followers"
                                            ]
                                        },
                                        "following_url": {
                                            "type": "string",
                                            "examples": [
                                                "https://api.github.com/users/octocat/following{/other_user}"
                                            ]
                                        },
                                        "gists_url": {
                                            "type": "string",
                                            "examples": [
                                                "https://api.github.com/users/octocat/gists{/gist_id}"
                                            ]
                                        },
                                        "starred_url": {
                                            "type": "string",
                                            "examples": [
                                                "https://api.github.com/users/octocat/starred{/owner}{/repo}"
                                            ]
                                        },
                                        "subscriptions_url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://api.github.com/users/octocat/subscriptions"
                                            ]
                                        },
                                        "organizations_url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://api.github.com/users/octocat/orgs"
                                            ]
                                        },
                                        "repos_url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://api.github.com/users/octocat/repos"
                                            ]
                                        },
                                        "events_url": {
                                            "type": "string",
                                            "examples": [
                                                "https://api.github.com/users/octocat/events{/privacy}"
                                            ]
                                        },
                                        "received_events_url": {
                                            "type": "string",
                                            "format": "uri",
                                            "examples": [
                                                "https://api.github.com/users/octocat/received_events"
                                            ]
                                        },
                                        "type": {
                                            "type": "string",
                                            "examples": [
                                                "User"
                                            ]
                                        },
                                        "site_admin": {
                                            "type": "boolean"
                                        },
                                        "starred_at": {
                                            "type": "string",
                                            "examples": [
                                                "\"2020-07-09T00:17:55Z\""
                                            ]
                                        }
                                    },
                                    "required": [
                                        "avatar_url",
                                        "events_url",
                                        "followers_url",
                                        "following_url",
                                        "gists_url",
                                        "gravatar_id",
                                        "html_url",
                                        "id",
                                        "node_id",
                                        "login",
                                        "organizations_url",
                                        "received_events_url",
                                        "repos_url",
                                        "site_admin",
                                        "starred_url",
                                        "subscriptions_url",
                                        "type",
                                        "url"
                                    ]
                                }
                            ]
                        },
                        "parents": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "sha": {
                                        "type": "string",
                                        "examples": [
                                            "7638417db6d59f3c431d3e1f261cc637155684cd"
                                        ]
                                    },
                                    "url": {
                                        "type": "string",
                                        "format": "uri",
                                        "examples": [
                                            "https://api.github.com/repos/octocat/Hello-World/commits/7638417db6d59f3c431d3e1f261cc637155684cd"
                                        ]
                                    },
                                    "html_url": {
                                        "type": "string",
                                        "format": "uri",
                                        "examples": [
                                            "https://github.com/octocat/Hello-World/commit/7638417db6d59f3c431d3e1f261cc637155684cd"
                                        ]
                                    }
                                },
                                "required": [
                                    "sha",
                                    "url"
                                ]
                            }
                        },
                        "stats": {
                            "type": "object",
                            "properties": {
                                "additions": {
                                    "type": "integer"
                                },
                                "deletions": {
                                    "type": "integer"
                                },
                                "total": {
                                    "type": "integer"
                                }
                            }
                        },
                        "files": {
                            "type": "array",
                            "items": {
                                "title": "Diff Entry",
                                "description": "Diff Entry",
                                "type": "object",
                                "properties": {
                                    "sha": {
                                        "type": "string",
                                        "examples": [
                                            "bbcd538c8e72b8c175046e27cc8f907076331401"
                                        ]
                                    },
                                    "filename": {
                                        "type": "string",
                                        "examples": [
                                            "file1.txt"
                                        ]
                                    },
                                    "status": {
                                        "type": "string",
                                        "enum": [
                                            "added",
                                            "removed",
                                            "modified",
                                            "renamed",
                                            "copied",
                                            "changed",
                                            "unchanged"
                                        ],
                                        "examples": [
                                            "added"
                                        ]
                                    },
                                    "additions": {
                                        "type": "integer",
                                        "examples": [
                                            103
                                        ]
                                    },
                                    "deletions": {
                                        "type": "integer",
                                        "examples": [
                                            21
                                        ]
                                    },
                                    "changes": {
                                        "type": "integer",
                                        "examples": [
                                            124
                                        ]
                                    },
                                    "blob_url": {
                                        "type": "string",
                                        "format": "uri",
                                        "examples": [
                                            "https://github.com/octocat/Hello-World/blob/6dcb09b5b57875f334f61aebed695e2e4193db5e/file1.txt"
                                        ]
                                    },
                                    "raw_url": {
                                        "type": "string",
                                        "format": "uri",
                                        "examples": [
                                            "https://github.com/octocat/Hello-World/raw/6dcb09b5b57875f334f61aebed695e2e4193db5e/file1.txt"
                                        ]
                                    },
                                    "contents_url": {
                                        "type": "string",
                                        "format": "uri",
                                        "examples": [
                                            "https://api.github.com/repos/octocat/Hello-World/contents/file1.txt?ref=6dcb09b5b57875f334f61aebed695e2e4193db5e"
                                        ]
                                    },
                                    "patch": {
                                        "type": "string",
                                        "examples": [
                                            "@@ -132,7 +132,7 @@ module Test @@ -1000,7 +1000,7 @@ module Test"
                                        ]
                                    },
                                    "previous_filename": {
                                        "type": "string",
                                        "examples": [
                                            "file.txt"
                                        ]
                                    }
                                },
                                "required": [
                                    "additions",
                                    "blob_url",
                                    "changes",
                                    "contents_url",
                                    "deletions",
                                    "filename",
                                    "raw_url",
                                    "sha",
                                    "status"
                                ]
                            }
                        }
                    },
                    "required": [
                        "url",
                        "sha",
                        "node_id",
                        "html_url",
                        "comments_url",
                        "commit",
                        "author",
                        "committer",
                        "parents"
                    ]
                },
                "_links": {
                    "type": "object",
                    "properties": {
                        "html": {
                            "type": "string"
                        },
                        "self": {
                            "type": "string",
                            "format": "uri"
                        }
                    },
                    "required": [
                        "html",
                        "self"
                    ]
                },
                "protected": {
                    "type": "boolean"
                },
                "protection": {
                    "title": "Branch Protection",
                    "description": "Branch Protection",
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string"
                        },
                        "enabled": {
                            "type": "boolean"
                        },
                        "required_status_checks": {
                            "title": "Protected Branch Required Status Check",
                            "description": "Protected Branch Required Status Check",
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string"
                                },
                                "enforcement_level": {
                                    "type": "string"
                                },
                                "contexts": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                },
                                "checks": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "context": {
                                                "type": "string"
                                            },
                                            "app_id": {
                                                "type": [
                                                    "integer",
                                                    "null"
                                                ]
                                            }
                                        },
                                        "required": [
                                            "context",
                                            "app_id"
                                        ]
                                    }
                                },
                                "contexts_url": {
                                    "type": "string"
                                },
                                "strict": {
                                    "type": "boolean"
                                }
                            },
                            "required": [
                                "contexts",
                                "checks"
                            ]
                        },
                        "enforce_admins": {
                            "title": "Protected Branch Admin Enforced",
                            "description": "Protected Branch Admin Enforced",
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "format": "uri",
                                    "examples": [
                                        "https://api.github.com/repos/octocat/Hello-World/branches/master/protection/enforce_admins"
                                    ]
                                },
                                "enabled": {
                                    "type": "boolean",
                                    "examples": [
                                        True
                                    ]
                                }
                            },
                            "required": [
                                "url",
                                "enabled"
                            ]
                        },
                        "required_pull_request_reviews": {
                            "title": "Protected Branch Pull Request Review",
                            "description": "Protected Branch Pull Request Review",
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "format": "uri",
                                    "examples": [
                                        "https://api.github.com/repos/octocat/Hello-World/branches/master/protection/dismissal_restrictions"
                                    ]
                                },
                                "dismissal_restrictions": {
                                    "type": "object",
                                    "properties": {
                                        "users": {
                                            "description": "The list of users with review dismissal access.",
                                            "type": "array",
                                            "items": {
                                                "title": "Simple User",
                                                "description": "A GitHub user.",
                                                "type": "object",
                                                "properties": {
                                                    "name": {
                                                        "type": [
                                                            "string",
                                                            "null"
                                                        ]
                                                    },
                                                    "email": {
                                                        "type": [
                                                            "string",
                                                            "null"
                                                        ]
                                                    },
                                                    "login": {
                                                        "type": "string",
                                                        "examples": [
                                                            "octocat"
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
                                                            "MDQ6VXNlcjE="
                                                        ]
                                                    },
                                                    "avatar_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://github.com/images/error/octocat_happy.gif"
                                                        ]
                                                    },
                                                    "gravatar_id": {
                                                        "type": [
                                                            "string",
                                                            "null"
                                                        ],
                                                        "examples": [
                                                            "41d064eb2195891e12d0413f63227ea7"
                                                        ]
                                                    },
                                                    "url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat"
                                                        ]
                                                    },
                                                    "html_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://github.com/octocat"
                                                        ]
                                                    },
                                                    "followers_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/followers"
                                                        ]
                                                    },
                                                    "following_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/following{/other_user}"
                                                        ]
                                                    },
                                                    "gists_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/gists{/gist_id}"
                                                        ]
                                                    },
                                                    "starred_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/starred{/owner}{/repo}"
                                                        ]
                                                    },
                                                    "subscriptions_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/subscriptions"
                                                        ]
                                                    },
                                                    "organizations_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/orgs"
                                                        ]
                                                    },
                                                    "repos_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/repos"
                                                        ]
                                                    },
                                                    "events_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/events{/privacy}"
                                                        ]
                                                    },
                                                    "received_events_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/received_events"
                                                        ]
                                                    },
                                                    "type": {
                                                        "type": "string",
                                                        "examples": [
                                                            "User"
                                                        ]
                                                    },
                                                    "site_admin": {
                                                        "type": "boolean"
                                                    },
                                                    "starred_at": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"2020-07-09T00:17:55Z\""
                                                        ]
                                                    }
                                                },
                                                "required": [
                                                    "avatar_url",
                                                    "events_url",
                                                    "followers_url",
                                                    "following_url",
                                                    "gists_url",
                                                    "gravatar_id",
                                                    "html_url",
                                                    "id",
                                                    "node_id",
                                                    "login",
                                                    "organizations_url",
                                                    "received_events_url",
                                                    "repos_url",
                                                    "site_admin",
                                                    "starred_url",
                                                    "subscriptions_url",
                                                    "type",
                                                    "url"
                                                ]
                                            }
                                        },
                                        "teams": {
                                            "description": "The list of teams with review dismissal access.",
                                            "type": "array",
                                            "items": {
                                                "title": "Team",
                                                "description": "Groups of organization members that gives permissions on specified repositories.",
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer"
                                                    },
                                                    "node_id": {
                                                        "type": "string"
                                                    },
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "slug": {
                                                        "type": "string"
                                                    },
                                                    "description": {
                                                        "type": [
                                                            "string",
                                                            "null"
                                                        ]
                                                    },
                                                    "privacy": {
                                                        "type": "string"
                                                    },
                                                    "permission": {
                                                        "type": "string"
                                                    },
                                                    "permissions": {
                                                        "type": "object",
                                                        "properties": {
                                                            "pull": {
                                                                "type": "boolean"
                                                            },
                                                            "triage": {
                                                                "type": "boolean"
                                                            },
                                                            "push": {
                                                                "type": "boolean"
                                                            },
                                                            "maintain": {
                                                                "type": "boolean"
                                                            },
                                                            "admin": {
                                                                "type": "boolean"
                                                            }
                                                        },
                                                        "required": [
                                                            "pull",
                                                            "triage",
                                                            "push",
                                                            "maintain",
                                                            "admin"
                                                        ]
                                                    },
                                                    "url": {
                                                        "type": "string",
                                                        "format": "uri"
                                                    },
                                                    "html_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://github.com/orgs/rails/teams/core"
                                                        ]
                                                    },
                                                    "members_url": {
                                                        "type": "string"
                                                    },
                                                    "repositories_url": {
                                                        "type": "string",
                                                        "format": "uri"
                                                    },
                                                    "parent": {
                                                        "anyOf": [
                                                            {
                                                                "type": "null"
                                                            },
                                                            {
                                                                "title": "Team Simple",
                                                                "description": "Groups of organization members that gives permissions on specified repositories.",
                                                                "type": "object",
                                                                "properties": {
                                                                    "id": {
                                                                        "description": "Unique identifier of the team",
                                                                        "type": "integer",
                                                                        "examples": [
                                                                            1
                                                                        ]
                                                                    },
                                                                    "node_id": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "MDQ6VGVhbTE="
                                                                        ]
                                                                    },
                                                                    "url": {
                                                                        "description": "URL for the team",
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/organizations/1/team/1"
                                                                        ]
                                                                    },
                                                                    "members_url": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "https://api.github.com/organizations/1/team/1/members{/member}"
                                                                        ]
                                                                    },
                                                                    "name": {
                                                                        "description": "Name of the team",
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "Justice League"
                                                                        ]
                                                                    },
                                                                    "description": {
                                                                        "description": "Description of the team",
                                                                        "type": [
                                                                            "string",
                                                                            "null"
                                                                        ],
                                                                        "examples": [
                                                                            "A great team."
                                                                        ]
                                                                    },
                                                                    "permission": {
                                                                        "description": "Permission that the team will have for its repositories",
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "admin"
                                                                        ]
                                                                    },
                                                                    "privacy": {
                                                                        "description": "The level of privacy this team should have",
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "closed"
                                                                        ]
                                                                    },
                                                                    "html_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://github.com/orgs/rails/teams/core"
                                                                        ]
                                                                    },
                                                                    "repositories_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/organizations/1/team/1/repos"
                                                                        ]
                                                                    },
                                                                    "slug": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "justice-league"
                                                                        ]
                                                                    },
                                                                    "ldap_dn": {
                                                                        "description": "Distinguished Name (DN) that team maps to within LDAP environment",
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "uid=example,ou=users,dc=github,dc=com"
                                                                        ]
                                                                    }
                                                                },
                                                                "required": [
                                                                    "id",
                                                                    "node_id",
                                                                    "url",
                                                                    "members_url",
                                                                    "name",
                                                                    "description",
                                                                    "permission",
                                                                    "html_url",
                                                                    "repositories_url",
                                                                    "slug"
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                },
                                                "required": [
                                                    "id",
                                                    "node_id",
                                                    "url",
                                                    "members_url",
                                                    "name",
                                                    "description",
                                                    "permission",
                                                    "html_url",
                                                    "repositories_url",
                                                    "slug",
                                                    "parent"
                                                ]
                                            }
                                        },
                                        "apps": {
                                            "description": "The list of apps with review dismissal access.",
                                            "type": "array",
                                            "items": {
                                                "title": "GitHub app",
                                                "description": "GitHub apps are a new way to extend GitHub. They can be installed directly on organizations and user accounts and granted access to specific repositories. They come with granular permissions and built-in webhooks. GitHub apps are first class actors within GitHub.",
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "description": "Unique identifier of the GitHub app",
                                                        "type": "integer",
                                                        "examples": [
                                                            37
                                                        ]
                                                    },
                                                    "slug": {
                                                        "description": "The slug name of the GitHub app",
                                                        "type": "string",
                                                        "examples": [
                                                            "probot-owners"
                                                        ]
                                                    },
                                                    "node_id": {
                                                        "type": "string",
                                                        "examples": [
                                                            "MDExOkludGVncmF0aW9uMQ=="
                                                        ]
                                                    },
                                                    "owner": {
                                                        "anyOf": [
                                                            {
                                                                "type": "null"
                                                            },
                                                            {
                                                                "title": "Simple User",
                                                                "description": "A GitHub user.",
                                                                "type": "object",
                                                                "properties": {
                                                                    "name": {
                                                                        "type": [
                                                                            "string",
                                                                            "null"
                                                                        ]
                                                                    },
                                                                    "email": {
                                                                        "type": [
                                                                            "string",
                                                                            "null"
                                                                        ]
                                                                    },
                                                                    "login": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "octocat"
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
                                                                            "MDQ6VXNlcjE="
                                                                        ]
                                                                    },
                                                                    "avatar_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://github.com/images/error/octocat_happy.gif"
                                                                        ]
                                                                    },
                                                                    "gravatar_id": {
                                                                        "type": [
                                                                            "string",
                                                                            "null"
                                                                        ],
                                                                        "examples": [
                                                                            "41d064eb2195891e12d0413f63227ea7"
                                                                        ]
                                                                    },
                                                                    "url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat"
                                                                        ]
                                                                    },
                                                                    "html_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://github.com/octocat"
                                                                        ]
                                                                    },
                                                                    "followers_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/followers"
                                                                        ]
                                                                    },
                                                                    "following_url": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/following{/other_user}"
                                                                        ]
                                                                    },
                                                                    "gists_url": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/gists{/gist_id}"
                                                                        ]
                                                                    },
                                                                    "starred_url": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/starred{/owner}{/repo}"
                                                                        ]
                                                                    },
                                                                    "subscriptions_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/subscriptions"
                                                                        ]
                                                                    },
                                                                    "organizations_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/orgs"
                                                                        ]
                                                                    },
                                                                    "repos_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/repos"
                                                                        ]
                                                                    },
                                                                    "events_url": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/events{/privacy}"
                                                                        ]
                                                                    },
                                                                    "received_events_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/received_events"
                                                                        ]
                                                                    },
                                                                    "type": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "User"
                                                                        ]
                                                                    },
                                                                    "site_admin": {
                                                                        "type": "boolean"
                                                                    },
                                                                    "starred_at": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "\"2020-07-09T00:17:55Z\""
                                                                        ]
                                                                    }
                                                                },
                                                                "required": [
                                                                    "avatar_url",
                                                                    "events_url",
                                                                    "followers_url",
                                                                    "following_url",
                                                                    "gists_url",
                                                                    "gravatar_id",
                                                                    "html_url",
                                                                    "id",
                                                                    "node_id",
                                                                    "login",
                                                                    "organizations_url",
                                                                    "received_events_url",
                                                                    "repos_url",
                                                                    "site_admin",
                                                                    "starred_url",
                                                                    "subscriptions_url",
                                                                    "type",
                                                                    "url"
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    "name": {
                                                        "description": "The name of the GitHub app",
                                                        "type": "string",
                                                        "examples": [
                                                            "Probot Owners"
                                                        ]
                                                    },
                                                    "description": {
                                                        "type": [
                                                            "string",
                                                            "null"
                                                        ],
                                                        "examples": [
                                                            "The description of the app."
                                                        ]
                                                    },
                                                    "external_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://example.com"
                                                        ]
                                                    },
                                                    "html_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://github.com/apps/super-ci"
                                                        ]
                                                    },
                                                    "created_at": {
                                                        "type": "string",
                                                        "format": "date-time",
                                                        "examples": [
                                                            "2017-07-08T16:18:44-04:00"
                                                        ]
                                                    },
                                                    "updated_at": {
                                                        "type": "string",
                                                        "format": "date-time",
                                                        "examples": [
                                                            "2017-07-08T16:18:44-04:00"
                                                        ]
                                                    },
                                                    "permissions": {
                                                        "description": "The set of permissions for the GitHub app",
                                                        "type": "object",
                                                        "properties": {
                                                            "issues": {
                                                                "type": "string"
                                                            },
                                                            "checks": {
                                                                "type": "string"
                                                            },
                                                            "metadata": {
                                                                "type": "string"
                                                            },
                                                            "contents": {
                                                                "type": "string"
                                                            },
                                                            "deployments": {
                                                                "type": "string"
                                                            }
                                                        },
                                                        "additionalProperties": {
                                                            "type": "string"
                                                        },
                                                        "example": {
                                                            "issues": "read",
                                                            "deployments": "write"
                                                        }
                                                    },
                                                    "events": {
                                                        "description": "The list of events for the GitHub app",
                                                        "type": "array",
                                                        "items": {
                                                            "type": "string"
                                                        },
                                                        "examples": [
                                                            "label",
                                                            "deployment"
                                                        ]
                                                    },
                                                    "installations_count": {
                                                        "description": "The number of installations associated with the GitHub app",
                                                        "type": "integer",
                                                        "examples": [
                                                            5
                                                        ]
                                                    },
                                                    "client_id": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"Iv1.25b5d1e65ffc4022\""
                                                        ]
                                                    },
                                                    "client_secret": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"1d4b2097ac622ba702d19de498f005747a8b21d3\""
                                                        ]
                                                    },
                                                    "webhook_secret": {
                                                        "type": [
                                                            "string",
                                                            "null"
                                                        ],
                                                        "examples": [
                                                            "\"6fba8f2fc8a7e8f2cca5577eddd82ca7586b3b6b\""
                                                        ]
                                                    },
                                                    "pem": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"-----BEGIN RSA PRIVATE KEY-----\\nMIIEogIBAAKCAQEArYxrNYD/iT5CZVpRJu4rBKmmze3PVmT/gCo2ATUvDvZTPTey\\nxcGJ3vvrJXazKk06pN05TN29o98jrYz4cengG3YGsXPNEpKsIrEl8NhbnxapEnM9\\nJCMRe0P5JcPsfZlX6hmiT7136GRWiGOUba2X9+HKh8QJVLG5rM007TBER9/z9mWm\\nrJuNh+m5l320oBQY/Qq3A7wzdEfZw8qm/mIN0FCeoXH1L6B8xXWaAYBwhTEh6SSn\\nZHlO1Xu1JWDmAvBCi0RO5aRSKM8q9QEkvvHP4yweAtK3N8+aAbZ7ovaDhyGz8r6r\\nzhU1b8Uo0Z2ysf503WqzQgIajr7Fry7/kUwpgQIDAQABAoIBADwJp80Ko1xHPZDy\\nfcCKBDfIuPvkmSW6KumbsLMaQv1aGdHDwwTGv3t0ixSay8CGlxMRtRDyZPib6SvQ\\n6OH/lpfpbMdW2ErkksgtoIKBVrDilfrcAvrNZu7NxRNbhCSvN8q0s4ICecjbbVQh\\nnueSdlA6vGXbW58BHMq68uRbHkP+k+mM9U0mDJ1HMch67wlg5GbayVRt63H7R2+r\\nVxcna7B80J/lCEjIYZznawgiTvp3MSanTglqAYi+m1EcSsP14bJIB9vgaxS79kTu\\noiSo93leJbBvuGo8QEiUqTwMw4tDksmkLsoqNKQ1q9P7LZ9DGcujtPy4EZsamSJT\\ny8OJt0ECgYEA2lxOxJsQk2kI325JgKFjo92mQeUObIvPfSNWUIZQDTjniOI6Gv63\\nGLWVFrZcvQBWjMEQraJA9xjPbblV8PtfO87MiJGLWCHFxmPz2dzoedN+2Coxom8m\\nV95CLz8QUShuao6u/RYcvUaZEoYs5bHcTmy5sBK80JyEmafJPtCQVxMCgYEAy3ar\\nZr3yv4xRPEPMat4rseswmuMooSaK3SKub19WFI5IAtB/e7qR1Rj9JhOGcZz+OQrl\\nT78O2OFYlgOIkJPvRMrPpK5V9lslc7tz1FSh3BZMRGq5jSyD7ETSOQ0c8T2O/s7v\\nbeEPbVbDe4mwvM24XByH0GnWveVxaDl51ABD65sCgYB3ZAspUkOA5egVCh8kNpnd\\nSd6SnuQBE3ySRlT2WEnCwP9Ph6oPgn+oAfiPX4xbRqkL8q/k0BdHQ4h+zNwhk7+h\\nWtPYRAP1Xxnc/F+jGjb+DVaIaKGU18MWPg7f+FI6nampl3Q0KvfxwX0GdNhtio8T\\nTj1E+SnFwh56SRQuxSh2gwKBgHKjlIO5NtNSflsUYFM+hyQiPiqnHzddfhSG+/3o\\nm5nNaSmczJesUYreH5San7/YEy2UxAugvP7aSY2MxB+iGsiJ9WD2kZzTUlDZJ7RV\\nUzWsoqBR+eZfVJ2FUWWvy8TpSG6trh4dFxImNtKejCR1TREpSiTV3Zb1dmahK9GV\\nrK9NAoGAbBxRLoC01xfxCTgt5BDiBcFVh4fp5yYKwavJPLzHSpuDOrrI9jDn1oKN\\nonq5sDU1i391zfQvdrbX4Ova48BN+B7p63FocP/MK5tyyBoT8zQEk2+vWDOw7H/Z\\nu5dTCPxTIsoIwUw1I+7yIxqJzLPFgR2gVBwY1ra/8iAqCj+zeBw=\\n-----END RSA PRIVATE KEY-----\\n\""
                                                        ]
                                                    }
                                                },
                                                "required": [
                                                    "id",
                                                    "node_id",
                                                    "owner",
                                                    "name",
                                                    "description",
                                                    "external_url",
                                                    "html_url",
                                                    "created_at",
                                                    "updated_at",
                                                    "permissions",
                                                    "events"
                                                ]
                                            }
                                        },
                                        "url": {
                                            "type": "string",
                                            "examples": [
                                                "\"https://api.github.com/repos/the-org/an-org-repo/branches/master/protection/dismissal_restrictions\""
                                            ]
                                        },
                                        "users_url": {
                                            "type": "string",
                                            "examples": [
                                                "\"https://api.github.com/repos/the-org/an-org-repo/branches/master/protection/dismissal_restrictions/users\""
                                            ]
                                        },
                                        "teams_url": {
                                            "type": "string",
                                            "examples": [
                                                "\"https://api.github.com/repos/the-org/an-org-repo/branches/master/protection/dismissal_restrictions/teams\""
                                            ]
                                        }
                                    }
                                },
                                "bypass_pull_request_allowances": {
                                    "type": "object",
                                    "description": "Allow specific users, teams, or apps to bypass pull request requirements.",
                                    "properties": {
                                        "users": {
                                            "description": "The list of users allowed to bypass pull request requirements.",
                                            "type": "array",
                                            "items": {
                                                "title": "Simple User",
                                                "description": "A GitHub user.",
                                                "type": "object",
                                                "properties": {
                                                    "name": {
                                                        "type": [
                                                            "string",
                                                            "null"
                                                        ]
                                                    },
                                                    "email": {
                                                        "type": [
                                                            "string",
                                                            "null"
                                                        ]
                                                    },
                                                    "login": {
                                                        "type": "string",
                                                        "examples": [
                                                            "octocat"
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
                                                            "MDQ6VXNlcjE="
                                                        ]
                                                    },
                                                    "avatar_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://github.com/images/error/octocat_happy.gif"
                                                        ]
                                                    },
                                                    "gravatar_id": {
                                                        "type": [
                                                            "string",
                                                            "null"
                                                        ],
                                                        "examples": [
                                                            "41d064eb2195891e12d0413f63227ea7"
                                                        ]
                                                    },
                                                    "url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat"
                                                        ]
                                                    },
                                                    "html_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://github.com/octocat"
                                                        ]
                                                    },
                                                    "followers_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/followers"
                                                        ]
                                                    },
                                                    "following_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/following{/other_user}"
                                                        ]
                                                    },
                                                    "gists_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/gists{/gist_id}"
                                                        ]
                                                    },
                                                    "starred_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/starred{/owner}{/repo}"
                                                        ]
                                                    },
                                                    "subscriptions_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/subscriptions"
                                                        ]
                                                    },
                                                    "organizations_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/orgs"
                                                        ]
                                                    },
                                                    "repos_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/repos"
                                                        ]
                                                    },
                                                    "events_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/events{/privacy}"
                                                        ]
                                                    },
                                                    "received_events_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://api.github.com/users/octocat/received_events"
                                                        ]
                                                    },
                                                    "type": {
                                                        "type": "string",
                                                        "examples": [
                                                            "User"
                                                        ]
                                                    },
                                                    "site_admin": {
                                                        "type": "boolean"
                                                    },
                                                    "starred_at": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"2020-07-09T00:17:55Z\""
                                                        ]
                                                    }
                                                },
                                                "required": [
                                                    "avatar_url",
                                                    "events_url",
                                                    "followers_url",
                                                    "following_url",
                                                    "gists_url",
                                                    "gravatar_id",
                                                    "html_url",
                                                    "id",
                                                    "node_id",
                                                    "login",
                                                    "organizations_url",
                                                    "received_events_url",
                                                    "repos_url",
                                                    "site_admin",
                                                    "starred_url",
                                                    "subscriptions_url",
                                                    "type",
                                                    "url"
                                                ]
                                            }
                                        },
                                        "teams": {
                                            "description": "The list of teams allowed to bypass pull request requirements.",
                                            "type": "array",
                                            "items": {
                                                "title": "Team",
                                                "description": "Groups of organization members that gives permissions on specified repositories.",
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "type": "integer"
                                                    },
                                                    "node_id": {
                                                        "type": "string"
                                                    },
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "slug": {
                                                        "type": "string"
                                                    },
                                                    "description": {
                                                        "type": [
                                                            "string",
                                                            "null"
                                                        ]
                                                    },
                                                    "privacy": {
                                                        "type": "string"
                                                    },
                                                    "permission": {
                                                        "type": "string"
                                                    },
                                                    "permissions": {
                                                        "type": "object",
                                                        "properties": {
                                                            "pull": {
                                                                "type": "boolean"
                                                            },
                                                            "triage": {
                                                                "type": "boolean"
                                                            },
                                                            "push": {
                                                                "type": "boolean"
                                                            },
                                                            "maintain": {
                                                                "type": "boolean"
                                                            },
                                                            "admin": {
                                                                "type": "boolean"
                                                            }
                                                        },
                                                        "required": [
                                                            "pull",
                                                            "triage",
                                                            "push",
                                                            "maintain",
                                                            "admin"
                                                        ]
                                                    },
                                                    "url": {
                                                        "type": "string",
                                                        "format": "uri"
                                                    },
                                                    "html_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://github.com/orgs/rails/teams/core"
                                                        ]
                                                    },
                                                    "members_url": {
                                                        "type": "string"
                                                    },
                                                    "repositories_url": {
                                                        "type": "string",
                                                        "format": "uri"
                                                    },
                                                    "parent": {
                                                        "anyOf": [
                                                            {
                                                                "type": "null"
                                                            },
                                                            {
                                                                "title": "Team Simple",
                                                                "description": "Groups of organization members that gives permissions on specified repositories.",
                                                                "type": "object",
                                                                "properties": {
                                                                    "id": {
                                                                        "description": "Unique identifier of the team",
                                                                        "type": "integer",
                                                                        "examples": [
                                                                            1
                                                                        ]
                                                                    },
                                                                    "node_id": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "MDQ6VGVhbTE="
                                                                        ]
                                                                    },
                                                                    "url": {
                                                                        "description": "URL for the team",
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/organizations/1/team/1"
                                                                        ]
                                                                    },
                                                                    "members_url": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "https://api.github.com/organizations/1/team/1/members{/member}"
                                                                        ]
                                                                    },
                                                                    "name": {
                                                                        "description": "Name of the team",
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "Justice League"
                                                                        ]
                                                                    },
                                                                    "description": {
                                                                        "description": "Description of the team",
                                                                        "type": [
                                                                            "string",
                                                                            "null"
                                                                        ],
                                                                        "examples": [
                                                                            "A great team."
                                                                        ]
                                                                    },
                                                                    "permission": {
                                                                        "description": "Permission that the team will have for its repositories",
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "admin"
                                                                        ]
                                                                    },
                                                                    "privacy": {
                                                                        "description": "The level of privacy this team should have",
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "closed"
                                                                        ]
                                                                    },
                                                                    "html_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://github.com/orgs/rails/teams/core"
                                                                        ]
                                                                    },
                                                                    "repositories_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/organizations/1/team/1/repos"
                                                                        ]
                                                                    },
                                                                    "slug": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "justice-league"
                                                                        ]
                                                                    },
                                                                    "ldap_dn": {
                                                                        "description": "Distinguished Name (DN) that team maps to within LDAP environment",
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "uid=example,ou=users,dc=github,dc=com"
                                                                        ]
                                                                    }
                                                                },
                                                                "required": [
                                                                    "id",
                                                                    "node_id",
                                                                    "url",
                                                                    "members_url",
                                                                    "name",
                                                                    "description",
                                                                    "permission",
                                                                    "html_url",
                                                                    "repositories_url",
                                                                    "slug"
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                },
                                                "required": [
                                                    "id",
                                                    "node_id",
                                                    "url",
                                                    "members_url",
                                                    "name",
                                                    "description",
                                                    "permission",
                                                    "html_url",
                                                    "repositories_url",
                                                    "slug",
                                                    "parent"
                                                ]
                                            }
                                        },
                                        "apps": {
                                            "description": "The list of apps allowed to bypass pull request requirements.",
                                            "type": "array",
                                            "items": {
                                                "title": "GitHub app",
                                                "description": "GitHub apps are a new way to extend GitHub. They can be installed directly on organizations and user accounts and granted access to specific repositories. They come with granular permissions and built-in webhooks. GitHub apps are first class actors within GitHub.",
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "description": "Unique identifier of the GitHub app",
                                                        "type": "integer",
                                                        "examples": [
                                                            37
                                                        ]
                                                    },
                                                    "slug": {
                                                        "description": "The slug name of the GitHub app",
                                                        "type": "string",
                                                        "examples": [
                                                            "probot-owners"
                                                        ]
                                                    },
                                                    "node_id": {
                                                        "type": "string",
                                                        "examples": [
                                                            "MDExOkludGVncmF0aW9uMQ=="
                                                        ]
                                                    },
                                                    "owner": {
                                                        "anyOf": [
                                                            {
                                                                "type": "null"
                                                            },
                                                            {
                                                                "title": "Simple User",
                                                                "description": "A GitHub user.",
                                                                "type": "object",
                                                                "properties": {
                                                                    "name": {
                                                                        "type": [
                                                                            "string",
                                                                            "null"
                                                                        ]
                                                                    },
                                                                    "email": {
                                                                        "type": [
                                                                            "string",
                                                                            "null"
                                                                        ]
                                                                    },
                                                                    "login": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "octocat"
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
                                                                            "MDQ6VXNlcjE="
                                                                        ]
                                                                    },
                                                                    "avatar_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://github.com/images/error/octocat_happy.gif"
                                                                        ]
                                                                    },
                                                                    "gravatar_id": {
                                                                        "type": [
                                                                            "string",
                                                                            "null"
                                                                        ],
                                                                        "examples": [
                                                                            "41d064eb2195891e12d0413f63227ea7"
                                                                        ]
                                                                    },
                                                                    "url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat"
                                                                        ]
                                                                    },
                                                                    "html_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://github.com/octocat"
                                                                        ]
                                                                    },
                                                                    "followers_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/followers"
                                                                        ]
                                                                    },
                                                                    "following_url": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/following{/other_user}"
                                                                        ]
                                                                    },
                                                                    "gists_url": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/gists{/gist_id}"
                                                                        ]
                                                                    },
                                                                    "starred_url": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/starred{/owner}{/repo}"
                                                                        ]
                                                                    },
                                                                    "subscriptions_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/subscriptions"
                                                                        ]
                                                                    },
                                                                    "organizations_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/orgs"
                                                                        ]
                                                                    },
                                                                    "repos_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/repos"
                                                                        ]
                                                                    },
                                                                    "events_url": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/events{/privacy}"
                                                                        ]
                                                                    },
                                                                    "received_events_url": {
                                                                        "type": "string",
                                                                        "format": "uri",
                                                                        "examples": [
                                                                            "https://api.github.com/users/octocat/received_events"
                                                                        ]
                                                                    },
                                                                    "type": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "User"
                                                                        ]
                                                                    },
                                                                    "site_admin": {
                                                                        "type": "boolean"
                                                                    },
                                                                    "starred_at": {
                                                                        "type": "string",
                                                                        "examples": [
                                                                            "\"2020-07-09T00:17:55Z\""
                                                                        ]
                                                                    }
                                                                },
                                                                "required": [
                                                                    "avatar_url",
                                                                    "events_url",
                                                                    "followers_url",
                                                                    "following_url",
                                                                    "gists_url",
                                                                    "gravatar_id",
                                                                    "html_url",
                                                                    "id",
                                                                    "node_id",
                                                                    "login",
                                                                    "organizations_url",
                                                                    "received_events_url",
                                                                    "repos_url",
                                                                    "site_admin",
                                                                    "starred_url",
                                                                    "subscriptions_url",
                                                                    "type",
                                                                    "url"
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    "name": {
                                                        "description": "The name of the GitHub app",
                                                        "type": "string",
                                                        "examples": [
                                                            "Probot Owners"
                                                        ]
                                                    },
                                                    "description": {
                                                        "type": [
                                                            "string",
                                                            "null"
                                                        ],
                                                        "examples": [
                                                            "The description of the app."
                                                        ]
                                                    },
                                                    "external_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://example.com"
                                                        ]
                                                    },
                                                    "html_url": {
                                                        "type": "string",
                                                        "format": "uri",
                                                        "examples": [
                                                            "https://github.com/apps/super-ci"
                                                        ]
                                                    },
                                                    "created_at": {
                                                        "type": "string",
                                                        "format": "date-time",
                                                        "examples": [
                                                            "2017-07-08T16:18:44-04:00"
                                                        ]
                                                    },
                                                    "updated_at": {
                                                        "type": "string",
                                                        "format": "date-time",
                                                        "examples": [
                                                            "2017-07-08T16:18:44-04:00"
                                                        ]
                                                    },
                                                    "permissions": {
                                                        "description": "The set of permissions for the GitHub app",
                                                        "type": "object",
                                                        "properties": {
                                                            "issues": {
                                                                "type": "string"
                                                            },
                                                            "checks": {
                                                                "type": "string"
                                                            },
                                                            "metadata": {
                                                                "type": "string"
                                                            },
                                                            "contents": {
                                                                "type": "string"
                                                            },
                                                            "deployments": {
                                                                "type": "string"
                                                            }
                                                        },
                                                        "additionalProperties": {
                                                            "type": "string"
                                                        },
                                                        "example": {
                                                            "issues": "read",
                                                            "deployments": "write"
                                                        }
                                                    },
                                                    "events": {
                                                        "description": "The list of events for the GitHub app",
                                                        "type": "array",
                                                        "items": {
                                                            "type": "string"
                                                        },
                                                        "examples": [
                                                            "label",
                                                            "deployment"
                                                        ]
                                                    },
                                                    "installations_count": {
                                                        "description": "The number of installations associated with the GitHub app",
                                                        "type": "integer",
                                                        "examples": [
                                                            5
                                                        ]
                                                    },
                                                    "client_id": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"Iv1.25b5d1e65ffc4022\""
                                                        ]
                                                    },
                                                    "client_secret": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"1d4b2097ac622ba702d19de498f005747a8b21d3\""
                                                        ]
                                                    },
                                                    "webhook_secret": {
                                                        "type": [
                                                            "string",
                                                            "null"
                                                        ],
                                                        "examples": [
                                                            "\"6fba8f2fc8a7e8f2cca5577eddd82ca7586b3b6b\""
                                                        ]
                                                    },
                                                    "pem": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"-----BEGIN RSA PRIVATE KEY-----\\nMIIEogIBAAKCAQEArYxrNYD/iT5CZVpRJu4rBKmmze3PVmT/gCo2ATUvDvZTPTey\\nxcGJ3vvrJXazKk06pN05TN29o98jrYz4cengG3YGsXPNEpKsIrEl8NhbnxapEnM9\\nJCMRe0P5JcPsfZlX6hmiT7136GRWiGOUba2X9+HKh8QJVLG5rM007TBER9/z9mWm\\nrJuNh+m5l320oBQY/Qq3A7wzdEfZw8qm/mIN0FCeoXH1L6B8xXWaAYBwhTEh6SSn\\nZHlO1Xu1JWDmAvBCi0RO5aRSKM8q9QEkvvHP4yweAtK3N8+aAbZ7ovaDhyGz8r6r\\nzhU1b8Uo0Z2ysf503WqzQgIajr7Fry7/kUwpgQIDAQABAoIBADwJp80Ko1xHPZDy\\nfcCKBDfIuPvkmSW6KumbsLMaQv1aGdHDwwTGv3t0ixSay8CGlxMRtRDyZPib6SvQ\\n6OH/lpfpbMdW2ErkksgtoIKBVrDilfrcAvrNZu7NxRNbhCSvN8q0s4ICecjbbVQh\\nnueSdlA6vGXbW58BHMq68uRbHkP+k+mM9U0mDJ1HMch67wlg5GbayVRt63H7R2+r\\nVxcna7B80J/lCEjIYZznawgiTvp3MSanTglqAYi+m1EcSsP14bJIB9vgaxS79kTu\\noiSo93leJbBvuGo8QEiUqTwMw4tDksmkLsoqNKQ1q9P7LZ9DGcujtPy4EZsamSJT\\ny8OJt0ECgYEA2lxOxJsQk2kI325JgKFjo92mQeUObIvPfSNWUIZQDTjniOI6Gv63\\nGLWVFrZcvQBWjMEQraJA9xjPbblV8PtfO87MiJGLWCHFxmPz2dzoedN+2Coxom8m\\nV95CLz8QUShuao6u/RYcvUaZEoYs5bHcTmy5sBK80JyEmafJPtCQVxMCgYEAy3ar\\nZr3yv4xRPEPMat4rseswmuMooSaK3SKub19WFI5IAtB/e7qR1Rj9JhOGcZz+OQrl\\nT78O2OFYlgOIkJPvRMrPpK5V9lslc7tz1FSh3BZMRGq5jSyD7ETSOQ0c8T2O/s7v\\nbeEPbVbDe4mwvM24XByH0GnWveVxaDl51ABD65sCgYB3ZAspUkOA5egVCh8kNpnd\\nSd6SnuQBE3ySRlT2WEnCwP9Ph6oPgn+oAfiPX4xbRqkL8q/k0BdHQ4h+zNwhk7+h\\nWtPYRAP1Xxnc/F+jGjb+DVaIaKGU18MWPg7f+FI6nampl3Q0KvfxwX0GdNhtio8T\\nTj1E+SnFwh56SRQuxSh2gwKBgHKjlIO5NtNSflsUYFM+hyQiPiqnHzddfhSG+/3o\\nm5nNaSmczJesUYreH5San7/YEy2UxAugvP7aSY2MxB+iGsiJ9WD2kZzTUlDZJ7RV\\nUzWsoqBR+eZfVJ2FUWWvy8TpSG6trh4dFxImNtKejCR1TREpSiTV3Zb1dmahK9GV\\nrK9NAoGAbBxRLoC01xfxCTgt5BDiBcFVh4fp5yYKwavJPLzHSpuDOrrI9jDn1oKN\\nonq5sDU1i391zfQvdrbX4Ova48BN+B7p63FocP/MK5tyyBoT8zQEk2+vWDOw7H/Z\\nu5dTCPxTIsoIwUw1I+7yIxqJzLPFgR2gVBwY1ra/8iAqCj+zeBw=\\n-----END RSA PRIVATE KEY-----\\n\""
                                                        ]
                                                    }
                                                },
                                                "required": [
                                                    "id",
                                                    "node_id",
                                                    "owner",
                                                    "name",
                                                    "description",
                                                    "external_url",
                                                    "html_url",
                                                    "created_at",
                                                    "updated_at",
                                                    "permissions",
                                                    "events"
                                                ]
                                            }
                                        }
                                    }
                                },
                                "dismiss_stale_reviews": {
                                    "type": "boolean",
                                    "examples": [
                                        True
                                    ]
                                },
                                "require_code_owner_reviews": {
                                    "type": "boolean",
                                    "examples": [
                                        True
                                    ]
                                },
                                "required_approving_review_count": {
                                    "type": "integer",
                                    "minimum": 0,
                                    "maximum": 6,
                                    "examples": [
                                        2
                                    ]
                                },
                                "require_last_push_approval": {
                                    "description": "Whether the most recent push must be approved by someone other than the person who pushed it.",
                                    "type": "boolean",
                                    "default": False,
                                    "examples": [
                                        True
                                    ]
                                }
                            },
                            "required": [
                                "dismiss_stale_reviews",
                                "require_code_owner_reviews"
                            ]
                        },
                        "restrictions": {
                            "title": "Branch Restriction Policy",
                            "description": "Branch Restriction Policy",
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "format": "uri"
                                },
                                "users_url": {
                                    "type": "string",
                                    "format": "uri"
                                },
                                "teams_url": {
                                    "type": "string",
                                    "format": "uri"
                                },
                                "apps_url": {
                                    "type": "string",
                                    "format": "uri"
                                },
                                "users": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "login": {
                                                "type": "string"
                                            },
                                            "id": {
                                                "type": "integer"
                                            },
                                            "node_id": {
                                                "type": "string"
                                            },
                                            "avatar_url": {
                                                "type": "string"
                                            },
                                            "gravatar_id": {
                                                "type": "string"
                                            },
                                            "url": {
                                                "type": "string"
                                            },
                                            "html_url": {
                                                "type": "string"
                                            },
                                            "followers_url": {
                                                "type": "string"
                                            },
                                            "following_url": {
                                                "type": "string"
                                            },
                                            "gists_url": {
                                                "type": "string"
                                            },
                                            "starred_url": {
                                                "type": "string"
                                            },
                                            "subscriptions_url": {
                                                "type": "string"
                                            },
                                            "organizations_url": {
                                                "type": "string"
                                            },
                                            "repos_url": {
                                                "type": "string"
                                            },
                                            "events_url": {
                                                "type": "string"
                                            },
                                            "received_events_url": {
                                                "type": "string"
                                            },
                                            "type": {
                                                "type": "string"
                                            },
                                            "site_admin": {
                                                "type": "boolean"
                                            }
                                        }
                                    }
                                },
                                "teams": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {
                                                "type": "integer"
                                            },
                                            "node_id": {
                                                "type": "string"
                                            },
                                            "url": {
                                                "type": "string"
                                            },
                                            "html_url": {
                                                "type": "string"
                                            },
                                            "name": {
                                                "type": "string"
                                            },
                                            "slug": {
                                                "type": "string"
                                            },
                                            "description": {
                                                "type": [
                                                    "string",
                                                    "null"
                                                ]
                                            },
                                            "privacy": {
                                                "type": "string"
                                            },
                                            "permission": {
                                                "type": "string"
                                            },
                                            "members_url": {
                                                "type": "string"
                                            },
                                            "repositories_url": {
                                                "type": "string"
                                            },
                                            "parent": {
                                                "type": [
                                                    "string",
                                                    "null"
                                                ]
                                            }
                                        }
                                    }
                                },
                                "apps": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {
                                                "type": "integer"
                                            },
                                            "slug": {
                                                "type": "string"
                                            },
                                            "node_id": {
                                                "type": "string"
                                            },
                                            "owner": {
                                                "type": "object",
                                                "properties": {
                                                    "login": {
                                                        "type": "string"
                                                    },
                                                    "id": {
                                                        "type": "integer"
                                                    },
                                                    "node_id": {
                                                        "type": "string"
                                                    },
                                                    "url": {
                                                        "type": "string"
                                                    },
                                                    "repos_url": {
                                                        "type": "string"
                                                    },
                                                    "events_url": {
                                                        "type": "string"
                                                    },
                                                    "hooks_url": {
                                                        "type": "string"
                                                    },
                                                    "issues_url": {
                                                        "type": "string"
                                                    },
                                                    "members_url": {
                                                        "type": "string"
                                                    },
                                                    "public_members_url": {
                                                        "type": "string"
                                                    },
                                                    "avatar_url": {
                                                        "type": "string"
                                                    },
                                                    "description": {
                                                        "type": "string"
                                                    },
                                                    "gravatar_id": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"\""
                                                        ]
                                                    },
                                                    "html_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"https://github.com/testorg-ea8ec76d71c3af4b\""
                                                        ]
                                                    },
                                                    "followers_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"https://api.github.com/users/testorg-ea8ec76d71c3af4b/followers\""
                                                        ]
                                                    },
                                                    "following_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"https://api.github.com/users/testorg-ea8ec76d71c3af4b/following{/other_user}\""
                                                        ]
                                                    },
                                                    "gists_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"https://api.github.com/users/testorg-ea8ec76d71c3af4b/gists{/gist_id}\""
                                                        ]
                                                    },
                                                    "starred_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"https://api.github.com/users/testorg-ea8ec76d71c3af4b/starred{/owner}{/repo}\""
                                                        ]
                                                    },
                                                    "subscriptions_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"https://api.github.com/users/testorg-ea8ec76d71c3af4b/subscriptions\""
                                                        ]
                                                    },
                                                    "organizations_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"https://api.github.com/users/testorg-ea8ec76d71c3af4b/orgs\""
                                                        ]
                                                    },
                                                    "received_events_url": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"https://api.github.com/users/testorg-ea8ec76d71c3af4b/received_events\""
                                                        ]
                                                    },
                                                    "type": {
                                                        "type": "string",
                                                        "examples": [
                                                            "\"Organization\""
                                                        ]
                                                    },
                                                    "site_admin": {
                                                        "type": "boolean",
                                                        "examples": [
                                                            False
                                                        ]
                                                    }
                                                }
                                            },
                                            "name": {
                                                "type": "string"
                                            },
                                            "description": {
                                                "type": "string"
                                            },
                                            "external_url": {
                                                "type": "string"
                                            },
                                            "html_url": {
                                                "type": "string"
                                            },
                                            "created_at": {
                                                "type": "string"
                                            },
                                            "updated_at": {
                                                "type": "string"
                                            },
                                            "permissions": {
                                                "type": "object",
                                                "properties": {
                                                    "metadata": {
                                                        "type": "string"
                                                    },
                                                    "contents": {
                                                        "type": "string"
                                                    },
                                                    "issues": {
                                                        "type": "string"
                                                    },
                                                    "single_file": {
                                                        "type": "string"
                                                    }
                                                }
                                            },
                                            "events": {
                                                "type": "array",
                                                "items": {
                                                    "type": "string"
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "required": [
                                "url",
                                "users_url",
                                "teams_url",
                                "apps_url",
                                "users",
                                "teams",
                                "apps"
                            ]
                        },
                        "required_linear_history": {
                            "type": "object",
                            "properties": {
                                "enabled": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "allow_force_pushes": {
                            "type": "object",
                            "properties": {
                                "enabled": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "allow_deletions": {
                            "type": "object",
                            "properties": {
                                "enabled": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "block_creations": {
                            "type": "object",
                            "properties": {
                                "enabled": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "required_conversation_resolution": {
                            "type": "object",
                            "properties": {
                                "enabled": {
                                    "type": "boolean"
                                }
                            }
                        },
                        "name": {
                            "type": "string",
                            "examples": [
                                "\"branch/with/protection\""
                            ]
                        },
                        "protection_url": {
                            "type": "string",
                            "examples": [
                                "\"https://api.github.com/repos/owner-79e94e2d36b3fd06a32bb213/AAA_Public_Repo/branches/branch/with/protection/protection\""
                            ]
                        },
                        "required_signatures": {
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "format": "uri",
                                    "examples": [
                                        "https://api.github.com/repos/octocat/Hello-World/branches/master/protection/required_signatures"
                                    ]
                                },
                                "enabled": {
                                    "type": "boolean",
                                    "examples": [
                                        True
                                    ]
                                }
                            },
                            "required": [
                                "url",
                                "enabled"
                            ]
                        },
                        "lock_branch": {
                            "type": "object",
                            "description": "Whether to set the branch as read-only. If this is true, users will not be able to push to the branch.",
                            "properties": {
                                "enabled": {
                                    "default": False,
                                    "type": "boolean"
                                }
                            }
                        },
                        "allow_fork_syncing": {
                            "type": "object",
                            "description": "Whether users can pull changes from upstream when the branch is locked. Set to `true` to allow fork syncing. Set to `false` to prevent fork syncing.",
                            "properties": {
                                "enabled": {
                                    "default": False,
                                    "type": "boolean"
                                }
                            }
                        }
                    }
                },
                "protection_url": {
                    "type": "string",
                    "format": "uri"
                },
                "pattern": {
                    "type": "string",
                    "examples": [
                        "\"mas*\""
                    ]
                },
                "required_approving_review_count": {
                    "type": "integer",
                    "examples": [
                        1
                    ]
                }
            },
            "required": [
                "name",
                "commit",
                "_links",
                "protection",
                "protected",
                "protection_url"
            ]
        }
        super().__init__(schema=schema)


schema = BranchSchema()
