#
# No change required normally except to possibly switch it to json
# eg. from checkov.json_doc.base_registry import Registry
#
from checkov.common.bridgecrew.check_type import CheckType
from checkov.yaml_doc.base_registry import Registry

registry = Registry(CheckType.YAML)
