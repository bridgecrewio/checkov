class ResourceKeywordIdentifier:
    KINDS_KEYWORDS_MAP = {
        "PersistentVolumeClaim": ["claimName"],
        "ServiceAccount": ["serviceAccountName"],
        "ClusterRole": ["rules[].resources", "rules[].resourceNames"],
        "ClusterRoleBinding": [["roleRef.name", "kind"], ["subjects[].name", "kind"], ["aggregationRule.clusterRoleSelectors.matchLabels"]],
        "Role": ["rules[].resources", "rules[].resourceNames"],
        "RoleBinding": [["roleRef.name", "kind"], ["subjects[].name", "kind"]]
    }
