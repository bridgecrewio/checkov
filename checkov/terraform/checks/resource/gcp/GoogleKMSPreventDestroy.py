from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class GoogleKMSPreventDestroy(BaseResourceValueCheck):
    def __init__(self):
        # "From the Provider Documentation"
        # CryptoKeys cannot be deleted from Google Cloud Platform.Destroying a Terraform - managed CryptoKey will remove
        # it from state and delete all CryptoKeyVersions, rendering the key unusable, but will not delete the resource
        # from the project.When Terraform destroys these keys, any data previously encrypted with these keys will be
        # irrecoverable.For this reason, it is strongly recommended that you add lifecycle hooks to the resource to
        # prevent accidental destruction.
        name = "Ensure KMS keys are protected from deletion"
        id = "CKV_GCP_82"
        supported_resources = ['google_kms_crypto_key']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'lifecycle/[0]/prevent_destroy'


check = GoogleKMSPreventDestroy()
