import responses
import pytest
from unittest import mock

from checkov.terraform.module_loading.loaders.registry_loader import RegistryLoader
from checkov.terraform.module_loading.module_params import ModuleParams


@responses.activate
def test_module_version_url_invoked_once():
    # given
    module_version_url = "https://registry.terraform.io/v1/modules/terraform-aws-modules/example/versions"
    responses.add(
        method=responses.GET,
        url=module_version_url,
        json={"modules": [{"versions": [{"version": "1.0.0"}]}]},
        status=200,
    )
    loader = RegistryLoader()
    RegistryLoader.modules_versions_cache = {}  # reset cache
    module_params = ModuleParams("", "", "terraform-aws-modules/example", "", "", "")
    loader.discover(module_params)

    # when
    loader._is_matching_loader(module_params)
    loader._is_matching_loader(module_params)

    # then
    responses.assert_call_count(module_version_url, 1)
    assert loader.modules_versions_cache == {module_version_url: ["1.0.0"]}

def test_determine_tf_api_endpoints_tfc():
    # given
    loader = RegistryLoader()
    module_params = ModuleParams("", "", "terraform-aws-modules/example", "", "", "")
    loader.discover(module_params)

    # when
    loader._determine_tf_api_endpoints(module_params)

    # then
    assert module_params.tf_host_name == "app.terraform.io"
    assert module_params.tf_modules_endpoint == "https://registry.terraform.io/v1/modules/"
    assert module_params.tf_modules_versions_endpoint == "https://registry.terraform.io/v1/modules/terraform-aws-modules/example/versions"

@pytest.mark.parametrize(
    "discovery_response",
    [
        ({
        "modules.v1": "/api/registry/v1/modules/",
        "providers.v1": "/api/registry/v1/providers/",
        "state.v2": "/api/v2/",
        "tfe.v2": "/api/v2/",
        "tfe.v2.1": "/api/v2/",
        "tfe.v2.2": "/api/v2/",
        "versions.v1": "https://checkpoint-api.hashicorp.com/v1/versions/"
        }),
        ({
        "modules.v1": "https://example.registry.com/api/registry/v1/modules/",
        "providers.v1": "https://example.registry.com/api/registry/v1/providers/",
        "state.v2": "https://example.registry.com/api/v2/",
        "tfe.v2": "https://example.registry.com/api/v2/",
        "tfe.v2.1": "https://example.registry.com/api/v2/",
        "tfe.v2.2": "https://example.registry.com/api/v2/",
        "versions.v1": "https://checkpoint-api.hashicorp.com/v1/versions/"
        }),
    ]
)
@responses.activate
def test_determine_tf_api_endpoints_tfe(discovery_response):
    # given
    loader = RegistryLoader()
    module_params = ModuleParams("", "", "example.registry.com/terraform-aws-modules/example", "", "", "")
    with mock.patch.dict("os.environ", {"TF_HOST_NAME": "example.registry.com"}):
        loader.discover(module_params)
    responses.add(
        method=responses.GET,
        url=f"https://{module_params.tf_host_name}/.well-known/terraform.json",
        json=discovery_response,
        status=200,
    )

    # when
    loader._determine_tf_api_endpoints(module_params)

    # then
    responses.assert_call_count(f"https://{module_params.tf_host_name}/.well-known/terraform.json", 1)
    assert module_params.tf_host_name == "example.registry.com"
    assert module_params.tf_modules_endpoint == "https://example.registry.com/api/registry/v1/modules/"
    assert module_params.tf_modules_versions_endpoint == "https://example.registry.com/api/registry/v1/modules/terraform-aws-modules/example/versions"

@responses.activate
def test_load_module():
    # given
    loader = RegistryLoader()
    module_params = ModuleParams("", "", "terraform-aws-modules/example", "", "", "")
    module_params.tf_modules_endpoint = "https://example.registry.com/api/registry/v1/modules/"
    module_params.best_version = "1.0.0"
    with mock.patch.dict("os.environ", {"TF_HOST_NAME": "example.registry.com"}):
        loader.discover(module_params)
    responses.add(
        method=responses.GET,
        url="https://example.registry.com/api/registry/v1/modules/terraform-aws-modules/example/1.0.0/download",
        status=200,
    )

    # when
    loader._load_module(module_params)

    # then
    responses.assert_call_count("https://example.registry.com/api/registry/v1/modules/terraform-aws-modules/example/1.0.0/download", 1)

@pytest.mark.parametrize(
    "download_url, expected_result",
    [
        ("https://example.com/download?archive=tgz", "tgz"),
        ("https://example.com/download?archive=zip", "zip"),
        ("https://example.com/download/module.zip", "zip"),
        ("https://example.com/download/module.zip?sig=foo", "zip"),
        ("https://example.com/download/module/archive", None),
    ]
)
def test_get_archive_extension(download_url, expected_result):
    archive_extension = RegistryLoader._get_archive_extension(download_url)
    assert archive_extension == expected_result

@pytest.mark.parametrize(
    "tf_host_name, module_download_url, expected_result",
    [
        ("example.com", "https://example.com/download?archive=tgz", "https://example.com/download?archive=tgz"),
        ("example.com", "https://example.com/abc", "https://example.com/abc"),
        ("example.com", "/api/registry/v1/modules/namespace/version/download?archive=tgz", "https://example.com/api/registry/v1/modules/namespace/version/download?archive=tgz"),
    ]
)
def test_normalize_module_download_url(tf_host_name, module_download_url, expected_result):
    # given
    loader = RegistryLoader()
    module_params = ModuleParams("", "", "example.com/terraform-aws-modules/example", "", "", "")
    with mock.patch.dict("os.environ", {"TF_HOST_NAME": tf_host_name}):
        loader.discover(module_params)

    # when
    normalized_url = loader._normalize_module_download_url(module_params, module_download_url)

    # then
    assert normalized_url == expected_result

@pytest.mark.parametrize(
    "source_url",
    [
        ("git::https://example.com/repo.git"),
        ("git@github.com:org/repo"),
        ("github.com/org/repo"),
        ("bitbucket.org/org/repo"),
    ]
)
def test_is_matching_loader_git_sources(source_url):
    #given
    loader = RegistryLoader()
    module_params = ModuleParams("", "", source_url, "", "", "")
    loader.discover(module_params)

    # then
    assert not loader._is_matching_loader(module_params)
