import responses

from checkov.terraform.module_loading.loaders.registry_loader import RegistryLoader


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
    loader.module_source = "terraform-aws-modules/example"

    # when
    loader._is_matching_loader()
    loader._is_matching_loader()

    # then
    responses.assert_call_count(module_version_url, 1)
    assert loader.modules_versions_cache == {module_version_url: ["1.0.0"]}
