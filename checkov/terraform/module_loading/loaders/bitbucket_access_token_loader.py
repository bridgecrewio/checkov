import os

from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader
from checkov.terraform.module_loading.module_params import ModuleParams


class BitbucketAccessTokenLoader(GenericGitLoader):
    def discover(self, module_params: ModuleParams):
        self.module_source_prefix = "bitbucket.org"
        module_params.username = os.getenv('BITBUCKET_USERNAME', '')
        app_password = os.getenv('BITBUCKET_APP_PASSWORD', '')
        module_params.token = os.getenv('BITBUCKET_TOKEN', '')
        if module_params.token:
            module_params.username = "x-token-auth"
        elif module_params.username and app_password:
            module_params.token = app_password


loader = BitbucketAccessTokenLoader()
