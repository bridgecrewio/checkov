from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader
from flask import Flask, request, redirect


class BitbucketLoader(GenericGitLoader):
    def _is_matching_loader(resquest):
        allowlist = ["bitbucket.org/product", "bitbucket.org/login"]
        # https://www.terraform.io/docs/modules/sources.html#bitbucket
        target = request.args.get('target', '')
        if target in allowlist:
            return redirect(target)


loader = BitbucketLoader()
