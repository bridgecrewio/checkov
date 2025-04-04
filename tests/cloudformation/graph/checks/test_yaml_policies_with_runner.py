import os

from checkov.cloudformation.runner import Runner
from checkov.common.graph.graph_builder import CustomAttributes


def test_connected_node_in_results_is_never_tuple():
    """
    Validates we correctly update the connected_node.
    It cannot be a tuple, as this is unserializable to json.
    """
    file_dir = os.path.dirname(__file__)
    dir_path = os.path.join(file_dir, f"resources", "ALBRedirectHTTPtoHTTPS")
    external_checks_dir = os.path.join(os.path.dirname(os.path.dirname(dir_path)), f"test_checks")

    runner = Runner()
    report = runner.run(dir_path, external_checks_dir=[external_checks_dir])

    all_results = report.failed_checks + report.passed_checks + report.skipped_checks
    for result in all_results:
        if "entity" in result.check_result:
            entity = result.check_result.get("entity", {})
            connected_node = entity.get(CustomAttributes.CONNECTED_NODE)
            if connected_node:
                if isinstance(connected_node, dict):
                    dict_keys = list(connected_node.keys())
                    assert not any([isinstance(key, tuple) for key in dict_keys])
