import pytest

from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.images.image_referencer import enable_image_referencer


@pytest.mark.parametrize(
    "api_key,frameworks,skip_frameworks,expected",
    [
        ("1234567890", ["all"], None, True),
        (None, ["all"], None, False),
        ("1234567890", ["terraform", "sca_image"], None, True),
        ("1234567890", ["terraform"], None, False),
        ("1234567890", None, ["sca_image"], False),
    ],
    ids=["pass", "without_api_key", "frameworks_with_sca_image", "frameworks_without_sca_image", "skip_sca_image"],
)
def test_enable_image_referencer(api_key, frameworks, skip_frameworks, expected):
    # given
    bc_integration = BcPlatformIntegration()
    bc_integration.bc_api_key = api_key

    # when
    use_image_referencer = enable_image_referencer(
        bc_integration=bc_integration, frameworks=frameworks, skip_frameworks=skip_frameworks
    )

    # then
    assert use_image_referencer is expected
