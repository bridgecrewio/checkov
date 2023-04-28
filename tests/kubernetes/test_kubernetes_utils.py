from operator import itemgetter

from checkov.kubernetes.kubernetes_utils import get_skipped_checks


def test_get_skipped_checks():
    # given
    manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "nginx",
            "labels": {"test": "test", "__startline__": 6, "__endline__": 7},
            "annotations": {
                "checkov.io/skip1": "CKV_K8S_11=I have not set CPU limits as I want BestEffort QoS",
                "checkov.io/skip2": "CKV2_CUSTOM_1=I have not set CPU limits as I want BestEffort QoS",
                "checkov.io/skip3": "CKV_K8S_14",
                "checkov.io/skip4": "CUSTOM_1",
                "__startline__": 8,
                "__endline__": 12,
            },
            "__startline__": 4,
            "__endline__": 12,
        },
        "spec": {
            "containers": [
                {
                    "name": "nginx",
                    "image": "nginx:1.14.2",
                    "ports": [{"containerPort": 80, "__startline__": 17, "__endline__": 17}],
                    "__startline__": 14,
                    "__endline__": 17,
                }
            ],
            "__startline__": 13,
            "__endline__": 17,
        },
        "__startline__": 1,
        "__endline__": 17,
    }

    # when
    skipped = get_skipped_checks(entity_conf=manifest)

    # then
    # remove 'bc_id' if present
    for skip in skipped:
        skip.pop("bc_id", None)

    assert sorted(skipped, key=itemgetter("id")) == sorted(
        [
            {"id": "CKV_K8S_11", "suppress_comment": "I have not set CPU limits as I want BestEffort QoS"},
            {"id": "CKV2_CUSTOM_1", "suppress_comment": "I have not set CPU limits as I want BestEffort QoS"},
            {"id": "CKV_K8S_14", "suppress_comment": "No comment provided"},
            {"id": "CUSTOM_1", "suppress_comment": "No comment provided"},
        ],
        key=itemgetter("id"),
    )
