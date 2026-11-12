from __future__ import annotations

from pathlib import Path

import pytest

from checkov.kubernetes.graph_builder.graph_components.edge_builders.KeywordEdgeBuilder import KeywordEdgeBuilder
from checkov.kubernetes.graph_builder.local_graph import KubernetesLocalGraph
from checkov.kubernetes.parser.parser import parse
from checkov.kubernetes.runner import Runner
from checkov.runner_filter import RunnerFilter
from tests.graph_utils.utils import GRAPH_FRAMEWORKS, set_db_connector_by_graph_framework


COLLIDING_ROLES_DIR = Path(__file__).parent / "checks/resources/ReadAllSecrets/CollidingRoleNames"


def role(namespace: str | None, kind: str = "Role", name: str = "shared") -> str:
    namespace_line = f"  namespace: {namespace}\n" if namespace is not None else ""
    return f"""apiVersion: rbac.authorization.k8s.io/v1
kind: {kind}
metadata:
  name: {name}
{namespace_line}rules:
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get"]
"""


def binding(namespace: str | None, role_kind: str = "Role", kind: str = "RoleBinding") -> str:
    namespace_line = f"  namespace: {namespace}\n" if namespace is not None else ""
    return f"""apiVersion: rbac.authorization.k8s.io/v1
kind: {kind}
metadata:
  name: binding
{namespace_line}roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: {role_kind}
  name: shared
subjects:
  - kind: ServiceAccount
    name: reader
    namespace: namespace-b
"""


def graph_edges(files: list[Path]) -> list[tuple[str, str]]:
    definitions = {str(path): parse(str(path))[0] for path in files}
    graph = KubernetesLocalGraph(definitions)
    graph.edge_builders = [KeywordEdgeBuilder]
    graph.build_graph(render_variables=False)
    return sorted((graph.vertices[edge.origin].id, graph.vertices[edge.dest].id) for edge in graph.edges)


@pytest.mark.parametrize("binding_namespace,role_namespace,connected", [
    ("namespace-a", "namespace-a", True),
    ("namespace-a", "namespace-b", False),
    (None, None, True),
    (None, "default", True),
    ("default", None, True),
    ("default", "default", True),
    (None, "namespace-a", False),
    ("namespace-a", None, False),
    ("default", "namespace-a", False),
])
def test_role_reference_namespace(tmp_path: Path, binding_namespace, role_namespace, connected):
    path = tmp_path / "rbac.yaml"
    path.write_text(binding(binding_namespace) + "---\n" + role(role_namespace), encoding="utf-8")

    expected = [(f"RoleBinding.{binding_namespace or 'default'}.binding",
                 f"Role.{role_namespace or 'default'}.shared")] if connected else []
    assert graph_edges([path]) == expected


@pytest.mark.parametrize("binding_kind,binding_namespace,role_kind,expected_role", [
    ("RoleBinding", "namespace-a", "Role", "Role.namespace-a.shared"),
    ("RoleBinding", "namespace-b", "Role", "Role.namespace-b.shared"),
    ("RoleBinding", "namespace-a", "ClusterRole", "ClusterRole.default.shared"),
    ("RoleBinding", "namespace-b", "ClusterRole", "ClusterRole.default.shared"),
    ("ClusterRoleBinding", None, "ClusterRole", "ClusterRole.default.shared"),
])
def test_role_reference_kind(tmp_path: Path, binding_kind, binding_namespace, role_kind, expected_role):
    path = tmp_path / "rbac.yaml"
    path.write_text("---\n".join([
        binding(binding_namespace, role_kind, binding_kind),
        role("namespace-a"), role("namespace-b"), role(None, "ClusterRole"),
    ]), encoding="utf-8")

    assert graph_edges([path]) == [(f"{binding_kind}.{binding_namespace or 'default'}.binding", expected_role)]


def test_role_namespace_is_independent_of_subject_namespace(tmp_path: Path):
    path = tmp_path / "rbac.yaml"
    path.write_text("---\n".join([
        binding("namespace-a"), role("namespace-a"), role("namespace-b"),
        """apiVersion: v1
kind: ServiceAccount
metadata:
  name: reader
  namespace: namespace-a
""",
        """apiVersion: v1
kind: ServiceAccount
metadata:
  name: reader
  namespace: namespace-b
""",
    ]), encoding="utf-8")

    assert graph_edges([path]) == [
        ("RoleBinding.namespace-a.binding", "Role.namespace-a.shared"),
        ("RoleBinding.namespace-a.binding", "ServiceAccount.namespace-b.reader"),
    ]


@pytest.mark.parametrize("target", ["missing", "other-name", "other-kind"])
def test_unresolved_role_reference(tmp_path: Path, target: str):
    documents = [binding("namespace-a")]
    if target == "other-name":
        documents.append(role("namespace-a", name="different"))
    elif target == "other-kind":
        documents.append(role(None, "ClusterRole"))
    path = tmp_path / "rbac.yaml"
    path.write_text("---\n".join(documents), encoding="utf-8")

    assert graph_edges([path]) == []


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
@pytest.mark.parametrize("resource,should_fail", [("secrets", True), ("pods", False)])
def test_cluster_role_shared_across_namespaces(tmp_path: Path, graph_framework, resource, should_fail):
    path = tmp_path / "rbac.yaml"
    path.write_text("---\n".join([
        role(None, "ClusterRole").replace('resources: ["secrets"]', f'resources: ["{resource}"]'),
        role("namespace-a"), role("namespace-b"),
        binding("namespace-a", "ClusterRole"), binding("namespace-b", "ClusterRole"),
        binding(None, "ClusterRole", "ClusterRoleBinding"),
    ]), encoding="utf-8")
    binding_ids = ["ClusterRoleBinding.default.binding", "RoleBinding.namespace-a.binding", "RoleBinding.namespace-b.binding"]
    assert graph_edges([path]) == [(binding_id, "ClusterRole.default.shared") for binding_id in binding_ids]

    report = Runner(db_connector=set_db_connector_by_graph_framework(graph_framework)).run(
        root_folder=None, files=[str(path)], runner_filter=RunnerFilter(checks=["CKV2_K8S_5"])
    )
    assert sorted(record.resource for record in report.passed_checks) == ([] if should_fail else binding_ids)
    assert sorted(record.resource for record in report.failed_checks) == (binding_ids if should_fail else [])
    assert report.parsing_errors == []


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
@pytest.mark.parametrize("reverse_order", [False, True])
@pytest.mark.parametrize("swap_namespaces", [False, True])
@pytest.mark.parametrize("single_file", [False, True])
def test_colliding_roles_scan(tmp_path: Path, graph_framework, reverse_order, swap_namespaces, single_file):
    documents = []
    for source in sorted(COLLIDING_ROLES_DIR.glob("*.yaml"), reverse=reverse_order):
        document = source.read_text(encoding="utf-8")
        if swap_namespaces:
            document = document.replace("namespace-a", "namespace-swap").replace(
                "namespace-b", "namespace-a"
            ).replace("namespace-swap", "namespace-b")
        documents.append(document)
    assert len(documents) == 4
    if single_file:
        documents = ["---\n".join(documents)]
    files = []
    for index, document in enumerate(documents):
        path = tmp_path / f"{index}.yaml"
        path.write_text(document, encoding="utf-8")
        files.append(path)

    assert graph_edges(files) == [
        ("RoleBinding.namespace-a.full-access-binding", "Role.namespace-a.full-access"),
        ("RoleBinding.namespace-b.full-access-binding", "Role.namespace-b.full-access"),
    ]
    runner = Runner(db_connector=set_db_connector_by_graph_framework(graph_framework))
    report = runner.run(root_folder=None, files=[str(path) for path in files],
                        runner_filter=RunnerFilter(checks=["CKV2_K8S_5"]))

    safe_namespace, unsafe_namespace = ("namespace-b", "namespace-a") if swap_namespaces else ("namespace-a", "namespace-b")
    assert [record.resource for record in report.passed_checks] == [f"RoleBinding.{safe_namespace}.full-access-binding"]
    assert [record.resource for record in report.failed_checks] == [f"RoleBinding.{unsafe_namespace}.full-access-binding"]
    assert report.parsing_errors == []
    assert report.skipped_checks == []
    binding_files = {
        f"RoleBinding.{document['metadata']['namespace']}.{document['metadata']['name']}": path
        for path in files for document in parse(str(path))[0] if document["kind"] == "RoleBinding"
    }
    for record in report.passed_checks + report.failed_checks:
        assert Path(record.file_abs_path) == binding_files[record.resource]
