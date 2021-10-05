from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader


class BitbucketLoader(GenericGitLoader):
    def _is_matching_loader(self) -> bool:
        # https://www.terraform.io/docs/modules/sources.html#bitbucket
        if self.module_source.startswith("bitbucket.org"):
            self.module_source = f"git::https://{self.module_source}"
            return True
        return False


loader = BitbucketLoader()
