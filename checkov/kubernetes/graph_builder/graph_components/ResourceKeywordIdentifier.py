class ResourceKeywordIdentifier:
    KINDS_KEYWORDS_MAP = {
        # "PersistentVolumeClaim": ["claimName"],
        # "ServiceAccount": ["serviceAccountName"],
        # "ClusterRole": ["rules[].resources", "rules[].resourceNames"],
        "ClusterRoleBinding": [
            {"metadata.name": "roleRef.name", "kind": "roleRef.kind"},
            {"metadata.name": ["subjects.name"], "kind": ["subjects.kind"]}],
        # "Role": ["rules[].resources", "rules[].resourceNames"],
        # "RoleBinding": [["roleRef.name", "kind"], ["subjects[].name", "kind"]]
    }
