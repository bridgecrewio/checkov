class ResourceKeywordIdentifier:
    """
    this class maps connections between resources by their unique keyword identifier.
    each resource in this class has a list of objects, and each object defines a potential connection to a different
    resource only if all attributes in the object are matched. each object in the list is independent regardless of
    the other objects in the list.

    for example:
    A ServiceAccount resource A with the property 'metadata.name' with value 'service-123' will match a resource B
    of type 'ClusterRoleBinding' with a 'subjects.name' property equals to 'service-123'
    and
    the property 'kind' for resource A matches resource B's 'subjects.kind' property
    """

    KINDS_KEYWORDS_MAP = {
        # TODO: "PersistentVolumeClaim": ["claimName"],
        # TODO: "ClusterRole": ["rules[].resources", "rules[].resourceNames"],
        # TODO: "Role": ["rules[].resources", "rules[].resourceNames"],

        "ServiceAccount": [
            {"spec.serviceAccountName": "metadata.name"}
        ],
        "ClusterRoleBinding": [
            {"metadata.name": "roleRef.name", "kind": "roleRef.kind"},
            [{"subjects": {"metadata.name": "name", "kind": "kind"}}]
        ],
        "RoleBinding": [
            {"metadata.name": "roleRef.name", "kind": "roleRef.kind"},
            [{"subjects": {"metadata.name": "name", "kind": "kind", "metadata.namespace": "namespace"}}]
        ]
    }
