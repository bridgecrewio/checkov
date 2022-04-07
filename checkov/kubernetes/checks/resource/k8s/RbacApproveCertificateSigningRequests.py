from checkov.kubernetes.checks.resource.base_rbac_check import BaseRbacK8sCheck, RbacOperation


class RbacApproveCertificateSigningRequests(BaseRbacK8sCheck):
    def __init__(self):
        name = "Minimize ClusterRoles that grant permissions to approve CertificateSigningRequests"
        id = "CKV_K8S_156"
        supported_entities = ["ClusterRole"]
        super().__init__(name=name, id=id, supported_entities=supported_entities)

        # See https://kubernetes.io/docs/reference/access-authn-authz/certificate-signing-requests/
        self.failing_operations = [
            RbacOperation(
                apigroups=["certificates.k8s.io"],
                verbs=["update", "patch"],
                resources=["certificatesigningrequests/approval"]
            ),
            RbacOperation(
                apigroups=["certificates.k8s.io"],
                verbs=["approve"],
                resources=["signers"]
            ),
        ]


check = RbacApproveCertificateSigningRequests()
