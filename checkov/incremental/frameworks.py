"""Per-framework definition of scan units and their file dependencies.

A *unit* is the smallest piece of a repository whose findings can be computed independently: its
findings depend only on the unit's own files. Which piece that is depends on how each Checkov
framework builds edges (verified by reading each framework's graph builder):

  framework       unit                         why
  -------------   --------------------------   ----------------------------------------------------
  terraform       root module (+ modules it    references resolve only inside a module instance;
                  calls, local and external)   a root module + its call tree is closed
  kubernetes      connected component of the   edges (label selectors, serviceAccountName,
                  cross-file edge graph        NetworkPolicy, RoleBinding...) span files
  bicep           root .bicep file + every     `module x './mod.bicep'` pulls other files in
                  .bicep it imports
  cloudformation  template file                Ref/GetAtt/DependsOn edges stay inside a template
  arm             template file                dependsOn/resourceId edges stay inside a template
  dockerfile      Dockerfile                   multi-stage edges stay inside the file
  serverless      serverless.yml               (no graph)
  openapi         spec file                    (no graph)
  ansible         playbook/task file           graph edges stay inside a file
  github_actions  workflow file                graph edges stay inside a file
  helm            chart directory              templates + values render together
  kustomize       kustomization overlay tree   overlays reference bases by path

Correctness rule used everywhere: a unit's findings are reused only if NONE of its files changed.
"""
from __future__ import annotations

import os
import re
from collections import defaultdict
from typing import Any, Callable, Optional

import yaml

from checkov.incremental.metadata import file_sha256

UnitFiles = dict[str, set[str]]  # unit id -> repo-relative files the unit depends on
EXTERNAL_MODULES_DIR = ".external_modules"  # where materialized external Terraform modules live


def _rel(root: str, path: str) -> str:
    return os.path.relpath(os.path.abspath(path), root)


KEPT_HIDDEN_DIRS = {".github"}  # Checkov's GitHub Actions runner includes this hidden dir explicitly


def _walk(root: str, predicate: Callable[[str], bool]) -> list[str]:
    found = []
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if (not d.startswith(".") or d in KEPT_HIDDEN_DIRS)
                         and d != "node_modules")
        for name in sorted(files):
            path = os.path.join(current, name)
            if predicate(path):
                found.append(_rel(root, path))
    return found


# ---------------------------------------------------------------------------------------------------
# file-scoped frameworks: one unit per file, discovered with the runner's own file predicate
# ---------------------------------------------------------------------------------------------------

def _per_file(root: str, predicate: Callable[[str], bool]) -> UnitFiles:
    return {path: {path} for path in _walk(root, predicate)}


def _is_cfn(path: str) -> bool:
    from checkov.cloudformation.cfn_utils import CF_POSSIBLE_ENDINGS
    if os.path.splitext(path)[1] not in CF_POSSIBLE_ENDINGS:
        return False
    text = _read(path)
    return "Resources" in text and ("AWSTemplateFormatVersion" in text or "Type: AWS::" in text
                                    or '"Type": "AWS::' in text or "Transform" in text)


def _is_arm(path: str) -> bool:
    return path.endswith(".json") and "schema.management.azure.com" in _read(path)


def _is_dockerfile(path: str) -> bool:
    from checkov.dockerfile.utils import is_dockerfile
    return is_dockerfile(os.path.basename(path))


def _is_serverless(path: str) -> bool:
    from checkov.serverless.utils import SLS_FILE_MASK
    return os.path.basename(path) in SLS_FILE_MASK


def _is_openapi(path: str) -> bool:
    if not path.endswith((".yaml", ".yml", ".json")):
        return False
    head = _read(path)[:2000]
    return "openapi" in head or "swagger" in head


def _is_gha(path: str) -> bool:
    norm = path.replace(os.sep, "/")
    return "/.github/workflows/" in f"/{norm}" or norm.startswith(".github/workflows/")


def _is_ansible(path: str) -> bool:
    if not path.endswith((".yaml", ".yml")):
        return False
    text = _read(path)
    return bool(re.search(r"^\s*-?\s*(hosts|tasks|block|ansible\.builtin\.|name):", text, re.M)) and (
        "hosts:" in text or "tasks:" in text or "ansible." in text)


def _read(path: str) -> str:
    try:
        with open(path, errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


# ---------------------------------------------------------------------------------------------------
# bicep: root file + transitive local module imports
# ---------------------------------------------------------------------------------------------------

BICEP_MODULE = re.compile(r"^\s*module\s+\w+\s+'([^']+\.bicep)'", re.M)


def bicep_units(root: str) -> UnitFiles:
    files = _walk(root, lambda p: p.endswith(".bicep"))
    imports: dict[str, set[str]] = {}
    for rel in files:
        here = os.path.dirname(os.path.join(root, rel))
        imports[rel] = {_rel(root, os.path.normpath(os.path.join(here, m)))
                        for m in BICEP_MODULE.findall(_read(os.path.join(root, rel)))}
    imported = set().union(*imports.values()) if imports else set()
    units: UnitFiles = {}
    for rel in files:
        # every file is scanned by Checkov on its own (modules are not inlined), but a root's graph
        # can reference its modules' vertices, so a root depends on the files it imports
        closure, stack = {rel}, [rel]
        while stack:
            for dep in imports.get(stack.pop(), ()):
                if dep not in closure:
                    closure.add(dep)
                    stack.append(dep)
        units[rel] = closure if rel not in imported else {rel} | closure
    return units


# ---------------------------------------------------------------------------------------------------
# kubernetes: connected components over the edges Checkov's own edge builders create
# ---------------------------------------------------------------------------------------------------

def kubernetes_units(root: str) -> UnitFiles:
    """Build the Kubernetes graph with Checkov's own builders and group files by connected component.
    The metadata (labels, selectors, keyword references) is exactly what the edge builders read."""
    from checkov.kubernetes.graph_builder.local_graph import KubernetesLocalGraph
    from checkov.kubernetes.kubernetes_graph_flags import K8sGraphFlags
    from checkov.kubernetes.kubernetes_utils import get_folder_definitions

    definitions, _ = get_folder_definitions(root, [])
    graph = KubernetesLocalGraph(definitions)
    graph.build_graph(render_variables=False, graph_flags=K8sGraphFlags(True, True))
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for path in definitions:
        find(_rel(root, path))
    for edge in graph.edges:
        a = _rel(root, graph.vertices[edge.origin].path)
        b = _rel(root, graph.vertices[edge.dest].path)
        parent[find(a)] = find(b)
    groups: dict[str, set[str]] = defaultdict(set)
    for path in list(parent):
        groups[find(path)].add(path)
    return {sorted(files)[0]: files for files in groups.values()}


def kubernetes_unit_edges(root: str) -> list[dict[str, Any]]:
    """Cross-file edges, persisted so a PR can find which unchanged files a changed file used to link to."""
    from checkov.kubernetes.graph_builder.local_graph import KubernetesLocalGraph
    from checkov.kubernetes.kubernetes_graph_flags import K8sGraphFlags
    from checkov.kubernetes.kubernetes_utils import get_folder_definitions

    definitions, _ = get_folder_definitions(root, [])
    graph = KubernetesLocalGraph(definitions)
    graph.build_graph(render_variables=False, graph_flags=K8sGraphFlags(True, True))
    edges = []
    for edge in graph.edges:
        a, b = graph.vertices[edge.origin], graph.vertices[edge.dest]
        if a.path != b.path:
            edges.append({"from": _rel(root, a.path), "to": _rel(root, b.path), "from_id": a.id, "to_id": b.id})
    return edges


# ---------------------------------------------------------------------------------------------------
# helm / kustomize: directory-scoped units
# ---------------------------------------------------------------------------------------------------

def helm_units(root: str) -> UnitFiles:
    units: UnitFiles = {}
    for chart in _walk(root, lambda p: os.path.basename(p) == "Chart.yaml"):
        chart_dir = os.path.dirname(chart)
        units[chart_dir or "."] = set(_walk(os.path.join(root, chart_dir), lambda p: True))
        units[chart_dir or "."] = {os.path.normpath(os.path.join(chart_dir, f)) for f in units[chart_dir or "."]}
    return units


def kustomize_units(root: str) -> UnitFiles:
    units: UnitFiles = {}
    for kfile in _walk(root, lambda p: os.path.basename(p) in ("kustomization.yaml", "kustomization.yml")):
        overlay = os.path.dirname(kfile)
        closure, stack = set(), [overlay]
        while stack:
            d = stack.pop()
            if d in closure:
                continue
            closure.add(d)
            for name in ("kustomization.yaml", "kustomization.yml"):
                path = os.path.join(root, d, name)
                if os.path.exists(path):
                    doc = yaml.safe_load(_read(path)) or {}
                    for ref in (doc.get("resources") or []) + (doc.get("bases") or []):
                        target = os.path.normpath(os.path.join(d, ref))
                        if os.path.isdir(os.path.join(root, target)):
                            stack.append(target)
        units[overlay or "."] = {os.path.normpath(os.path.join(d, f)) for d in closure
                                 for f in _walk(os.path.join(root, d), lambda p: p.endswith((".yaml", ".yml")))}
    return units


# ---------------------------------------------------------------------------------------------------
# terraform: root modules (+ call tree), discovered with Checkov's own TFParser
# ---------------------------------------------------------------------------------------------------

def terraform_units(root: str, external_modules_content_cache: Optional[dict[str, Any]] = None) -> UnitFiles:
    from checkov.terraform.tf_parser import TFParser

    definitions = TFParser().parse_directory(root, external_modules_content_cache=external_modules_content_cache)
    unit_dirs: dict[str, set[str]] = defaultdict(set)
    for key in definitions:
        file_dir = os.path.dirname(key.file_path)
        module = key.tf_source_modules
        if module is None:
            unit_dirs[file_dir].add(file_dir)
            continue
        while module.nested_tf_module is not None:
            module = module.nested_tf_module
        unit_dirs[os.path.dirname(module.path)].add(file_dir)
    units: UnitFiles = {}
    for root_dir, dirs in unit_dirs.items():
        files: set[str] = set()
        for d in dirs:
            if os.path.commonpath([root, os.path.abspath(d)]) != root:
                continue
            if _rel(root, d).split(os.sep)[0] == EXTERNAL_MODULES_DIR:
                # materialized external modules are tracked by immutable identity (UnitMetadata.external_modules),
                # not by file hash: they are not part of the MR diff and are not present in a fresh PR checkout
                continue
            for name in sorted(os.listdir(d)):
                if name.endswith((".tf", ".hcl", ".tfvars", ".tfvars.json")):
                    files.add(_rel(root, os.path.join(d, name)))
        units[_rel(root, root_dir)] = files
    return units


TF_FILE_FN = re.compile(r"""(?:file|templatefile|filebase64|filesha256|filemd5)\(\s*"([^"$]+)\"""")


def terraform_referenced_files(root: str, unit_files: set[str]) -> set[str]:
    """Non-HCL files the unit reads through file()/templatefile() with a literal path.
    Checkov does not evaluate these today, but adding them keeps the unit invalidated if they change."""
    extra = set()
    for rel in unit_files:
        if not rel.endswith(".tf"):
            continue
        here = os.path.dirname(os.path.join(root, rel))
        for ref in TF_FILE_FN.findall(_read(os.path.join(root, rel))):
            ref = ref.replace("${path.module}/", "").replace("${path.root}/", "")
            candidate = os.path.normpath(os.path.join(here, ref))
            if os.path.isfile(candidate):
                extra.add(_rel(root, candidate))
    return extra


# ---------------------------------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------------------------------

FILE_SCOPED: dict[str, Callable[[str], bool]] = {
    "cloudformation": _is_cfn,
    "arm": _is_arm,
    "dockerfile": _is_dockerfile,
    "serverless": _is_serverless,
    "openapi": _is_openapi,
    "github_actions": _is_gha,
    "ansible": _is_ansible,
}


def discover_units(framework: str, root: str, **kwargs: Any) -> UnitFiles:
    root = os.path.abspath(root)
    if framework in FILE_SCOPED:
        return _per_file(root, FILE_SCOPED[framework])
    if framework == "terraform":
        units = terraform_units(root, kwargs.get("external_modules_content_cache"))
        return {uid: files | terraform_referenced_files(root, files) for uid, files in units.items()}
    if framework == "kubernetes":
        return kubernetes_units(root)
    if framework == "bicep":
        return bicep_units(root)
    if framework == "helm":
        return helm_units(root)
    if framework == "kustomize":
        return kustomize_units(root)
    raise ValueError(f"incremental scanning does not support framework {framework!r}")


def hash_files(root: str, files: set[str]) -> dict[str, str]:
    return {f: file_sha256(os.path.join(root, f)) for f in sorted(files)}
