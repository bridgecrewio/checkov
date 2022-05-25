from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader


class BitbucketLoader(GenericGitLoader):
    def discover(self):
        self.module_source_prefix = "bitbucket.org"


loader = BitbucketLoader()
