from checkov.kubernetes.checks.resource.base_rbac_check import BaseRbacK8sCheck, RbacOperation


class RbacEscalateRoles(BaseRbacK8sCheck):
    def __init__(self):
        name = "Minimize Roles and ClusterRoles that grant permissions to escalate Roles or ClusterRoles"
        id = "CKV_K8S_158"
        super().__init__(name=name, id=id)

        self.failing_operations = [
            RbacOperation(
                apigroups=["rbac.authorization.k8s.io"],
                verbs=["escalate"],
                resources=["roles", "clusterroles"]
            ),
        ]


check = RbacEscalateRoles()
