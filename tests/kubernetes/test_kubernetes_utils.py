import os
from operator import itemgetter
from pathlib import Path

from checkov.kubernetes.kubernetes_utils import get_folder_definitions, get_skipped_checks, should_include_path


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


def test_get_skipped_checks_supported_prefixes():
    # given
    manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "nginx",
            "annotations": {
                "checkov.io/skip1": "CKV_K8S_11=checkov prefix",
                "bridgecrew.io/skip1": "CKV_K8S_14=bridgecrew prefix",
                "cortex.io/skip1": "CKV_K8S_16=cortex prefix",
                "__startline__": 6,
                "__endline__": 9,
            },
            "__startline__": 4,
            "__endline__": 9,
        },
        "spec": {"containers": [], "__startline__": 10, "__endline__": 10},
        "__startline__": 1,
        "__endline__": 10,
    }

    # when
    skipped = get_skipped_checks(entity_conf=manifest)

    # then
    for skip in skipped:
        skip.pop("bc_id", None)

    assert sorted(skipped, key=itemgetter("id")) == sorted(
        [
            {"id": "CKV_K8S_11", "suppress_comment": "checkov prefix"},
            {"id": "CKV_K8S_14", "suppress_comment": "bridgecrew prefix"},
            {"id": "CKV_K8S_16", "suppress_comment": "cortex prefix"},
        ],
        key=itemgetter("id"),
    )


def test_get_skipped_checks_ignores_unknown_prefix():
    # given
    manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "nginx",
            "annotations": {
                "example.com/skip1": "CKV_K8S_16=unsupported prefix",
                "__startline__": 6,
                "__endline__": 7,
            },
            "__startline__": 4,
            "__endline__": 7,
        },
        "spec": {"containers": [], "__startline__": 8, "__endline__": 8},
        "__startline__": 1,
        "__endline__": 8,
    }

    # when
    skipped = get_skipped_checks(entity_conf=manifest)

    # then
    assert skipped == []


DEPLOYMENT = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.14.2
"""


def _write_manifest(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    manifest = directory / "deployment.yaml"
    manifest.write_text(DEPLOYMENT)
    return manifest


def test_get_folder_definitions_root_inside_hidden_dir(tmp_path: Path) -> None:
    # given
    root = tmp_path / "project" / ".build" / "chart" / "templates"
    manifest = _write_manifest(root)

    # when
    definitions, _ = get_folder_definitions(str(root), None)

    # then
    assert str(manifest) in definitions


def test_get_folder_definitions_root_with_parent_dir_reference(tmp_path: Path) -> None:
    # given
    (tmp_path / "project" / "sub").mkdir(parents=True)
    manifest = _write_manifest(tmp_path / "project" / "templates")
    root = os.path.join(str(tmp_path), "project", "sub", "..", "templates")

    # when
    definitions, _ = get_folder_definitions(root, None)

    # then
    assert os.path.join(root, manifest.name) in definitions


def test_get_folder_definitions_skips_hidden_dir_below_root(tmp_path: Path) -> None:
    # given
    root = tmp_path / "project"
    visible = _write_manifest(root / "templates")
    hidden = _write_manifest(root / ".build" / "templates")

    # when
    definitions, _ = get_folder_definitions(str(root), None)

    # then
    assert str(visible) in definitions
    assert str(hidden) not in definitions


def test_should_include_path_relative_to_root_folder() -> None:
    root = os.path.join("project", ".build", "chart")

    assert should_include_path(os.path.join(root, "templates", "deployment.yaml"), True, root) is True
    assert should_include_path(os.path.join(root, ".hidden", "deployment.yaml"), True, root) is False
    assert should_include_path(os.path.join(root, ".hidden", "deployment.yaml"), False, root) is True


def test_should_include_path_windows_separators() -> None:
    assert should_include_path("C:\project\.hidden\deployment.yaml", True) is False
    assert should_include_path("C:\project\not_hidden\deployment.yaml", True) is True
    assert should_include_path("project/../templates/deployment.yaml", True) is True
