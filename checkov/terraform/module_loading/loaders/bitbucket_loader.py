from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader


class BitbucketLoader(GenericGitLoader):
    def _is_matching_loader(self):
        # https://www.terraform.io/docs/modules/sources.html#bitbucket
        if 'bitbucket.org' in self.module_source:
            if not self.module_source.startswith('https://') or not self.module_source.startswith('http://'):
                self.module_source = 'https://' + self.module_source
            if not self.module_source.endswith('.git'):
                self.module_source = self.module_source + '.git'
            return True
        return False


loader = BitbucketLoader()
