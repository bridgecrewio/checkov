# the order is important, because it reflects the order, which will be used to download the module
from checkov.terraform.module_loading.loaders.registry_loader import RegistryLoader
from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader
from checkov.terraform.module_loading.loaders.github_loader import GithubLoader
from checkov.terraform.module_loading.loaders.bitbucket_loader import BitbucketLoader
from checkov.terraform.module_loading.loaders.github_access_token_loader import GithubAccessTokenLoader
from checkov.terraform.module_loading.loaders.bitbucket_access_token_loader import BitbucketAccessTokenLoader
from checkov.terraform.module_loading.loaders.local_path_loader import LocalPathLoader
