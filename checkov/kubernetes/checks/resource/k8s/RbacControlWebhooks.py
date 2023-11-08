from checkov.kubernetes.checks.resource.base_rbac_check import BaseRbacK8sCheck, RbacOperation


class RbacControlWebhooks(BaseRbacK8sCheck):
    def __init__(self) -> None:
        name = "Minimize ClusterRoles that grant control over validating or mutating admission webhook configurations"
        id = "CKV_K8S_155"
        supported_entities = ["ClusterRole"]
        super().__init__(name=name, id=id, supported_entities=supported_entities)

        self.failing_operations = [
            RbacOperation(
                apigroups=["admissionregistration.k8s.io"],
                verbs=["create", "update", "patch"],
                resources=["mutatingwebhookconfigurations", "validatingwebhookconfigurations"]
            ),
        ]


check = RbacControlWebhooks()
