class ResourceKeywordIdentifier:
    kinds_keywords_map = {
        "PersistentVolumeClaim": ["claimName"],
        "ServiceAccount": ["serviceAccountName"],
        "ClusterRole": ["rules[].resources", "rules[].resourceNames"],
        "ClusterRoleBinding": [["roleRef.name", "kind"], ["subjects[].name", "kind"], ["aggregationRule.clusterRoleSelectors.matchLabels"]],
        "Role": ["rules[].resources", "rules[].resourceNames"],
        "RoleBinding": [["roleRef.name", "kind"], ["subjects[].name", "kind"]]
    }