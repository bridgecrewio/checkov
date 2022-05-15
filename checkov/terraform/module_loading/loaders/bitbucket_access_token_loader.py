import os

from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader


class BitbucketAccessTokenLoader(GenericGitLoader):
    def discover(self):
        self.module_source_prefix = "bitbucket.org"
        self.username = os.getenv('BITBUCKET_USERNAME', '')
        self.app_password = os.getenv('BITBUCKET_APP_PASSWORD', '')
        self.token = os.getenv('BITBUCKET_TOKEN', '')
        if self.token:
            self.username = "x-token-auth"
        elif self.username and self.app_password:
            self.token = self.app_password


loader = BitbucketAccessTokenLoader()
