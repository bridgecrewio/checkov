"""count / for_each expansion values: recorded at baseline, reused by the PR scan when provably unchanged.

Checkov's count / for_each handler (ForeachEntityHandler._get_statements) decides, for every counted / for_each
resource or data block of a graph, its expansion value ("statement": an int for count, a list / dict for for_each, or
None = not expanded). Static statements are evaluated directly; dynamic ones are rendered on a copy of the graph (a
sub-graph render) and read back. That sub-graph render dominates the cost of rebuilding a unit with count / for_each.

The value of a block's statement is a function of the vertices in its READ CLOSURE in the pre-expansion graph: the
block itself plus every vertex reachable from it through out-edges (an edge evaluation writes only its origin and reads
only its origin and destination; subgraph_scope.read_closure uses the same argument). If no vertex of that closure
differs from the baseline (pre-expansion content digest) and the closure's edge set is the same, the statement is
the baseline's: recompute nothing. Otherwise the statement is recomputed with Checkov's own code, but only for those
blocks (the sub-graph render then covers only their read closures).

Recording happens on the baseline's handler call, per graph, in Checkov's call order; blocks are identified by stable
keys (file, module chain, type, name), so the record is valid for a PR graph built from the same unit.

Opt-in: the PR scan sets graph.foreach_statement_oracle; nothing changes otherwise.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import Any, Optional

from checkov.common.util.json_utils import CustomJSONEncoder
from checkov.terraform.graph_builder.foreach.consts import COUNT_STRING, FOREACH_STRING

NEGATIVE_CONTROL = os.getenv("DFO_NEGATIVE", "")
RECORD_WEAKENED_CLOSURE = os.getenv("DFO_RECORD_WEAKENED_CLOSURE", "") == "true"
"""Test-only: the baseline also records the weakened closure the `imprecise_closure_drop_destinations` control compares
against (the baseline worker never sees DFO_NEGATIVE; recording changes no scan result)."""
PRECISE_CLOSURE_ENV = "CHECKOV_DIFF_PRECISE_CLOSURE"


def _anonymised_identity(value: Any, root: str) -> str:
    """Identity strings (statement-record keys) keep the CURRENT path: the expansions section is renamed with the
    artifact (rename.section_remapper), so keys of renamed blocks already carry the new path."""
    return json.dumps(value, cls=CustomJSONEncoder, sort_keys=True, default=str).replace(root, "<root>")


def _anonymised(value: Any, root: str) -> str:
    """Closure signatures and statement keys of the baseline were computed with OLD paths of renamed files
    (incremental_graph.PATH_RENAMES): the PR side maps new paths back so they compare equal."""
    from checkov.terraform.graph_builder.incremental_graph import PATH_RENAMES

    text = json.dumps(value, cls=CustomJSONEncoder, sort_keys=True, default=str).replace(root, "<root>")
    for old, new in PATH_RENAMES:
        text = text.replace(new, old)
    return text


def block_key(vertex: Any, root: str) -> str:
    """Stable identity of a (pre-expansion) block: no index, it is the same before and after expansion."""
    from checkov.common.graph.graph_builder.deterministic import module_chain_key

    chain = [list(m) for m in module_chain_key(vertex.source_module_object)]
    return _anonymised_identity([vertex.path, chain, vertex.block_type, vertex.name], root)


def content_digest(vertex: Any, root: str) -> str:
    """Everything of a pre-expansion vertex its statement evaluation can read (attributes, config, identity)."""
    payload = [block_key(vertex, root), vertex.attributes, vertex.config, getattr(vertex, "foreach_attrs", None),
               vertex.for_each_index]
    return hashlib.sha256(_anonymised(payload, root).encode()).hexdigest()


def read_closure(graph: Any, start: int) -> set[int]:
    closure = {start}
    stack = [start]
    while stack:
        for edge in graph.out_edges.get(stack.pop(), []):
            if edge.dest not in closure:
                closure.add(edge.dest)
                stack.append(edge.dest)
    return closure


def precise_closure_enabled() -> bool:
    return os.getenv(PRECISE_CLOSURE_ENV, "false").lower() == "true"


SIGNATURE_FIELD = {False: "signature", True: "precise_signature"}
"""Record field per closure mode: the baseline records both, the PR scan compares the one its mode uses."""

RESOURCE_LIKE = ("resource", "data")
"""Destination block types whose value an edge evaluation reads only through the referenced attribute key path
(TerraformVariableRenderer.extract_value_from_vertex looks up `attributes[<path suffix>]`, plus the data-block
special keywords). Variables, locals, outputs, modules, providers, tfvars are always read as a whole.

Facts that make resource destinations safe to narrow (verified with probes, results/round8):
  * the count / for_each sub-graph render leaves every resource that is not a block-to-render out of the sub-graph
    (ForeachAbstractHandler._build_sub_graph: `{}` placeholders); an evaluation touching a placeholder returns
    immediately (the statement then stays unresolved, None). So a resource destination's attributes are not read
    at all during a resource handler call; narrowing to the referenced attributes is therefore conservative.
  * the resource's own count / for_each attribute is never read through a reference (`aws_x.y.count` is not a
    Terraform reference to the count expression)."""


def _weakened_signatures(graph: Any, root: str) -> Optional["_ClosureSignatures"]:
    """Negative control `imprecise_closure_drop_destinations` only: a closure in which resource / data destinations
    contribute nothing. None outside the control, so production baselines never pay for it."""
    if NEGATIVE_CONTROL != "imprecise_closure_drop_destinations" and not RECORD_WEAKENED_CLOSURE:
        return None
    weak = _ClosureSignatures(graph, root, precise=True)
    weak.drop_resource_destinations = True
    return weak


class _ClosureSignatures:
    """Per graph: content digests and stable keys computed once per vertex (many counted blocks share most of their
    read closure: the module's variables and locals).

    Attribute-precise closure (CHECKOV_DIFF_PRECISE_CLOSURE): the renderer evaluates an edge (origin, dest, label) by
    reading the ORIGIN's attribute `label` and, from the destination, only the value at the referenced key path. For a
    resource / data destination, that path is one of the attributes the origin's expression references
    (`aws_vpc.this.id` -> `id`), so only those attributes of the destination (and every vertex reachable from them)
    matter, not its whole content. A destination contributes its WHOLE content when its type is not resource / data,
    when the referenced attribute cannot be determined, or when the flag is off."""

    def __init__(self, graph: Any, root: str, precise: Optional[bool] = None) -> None:
        self.graph = graph
        self.root = root
        self.digests: dict[int, str] = {}
        self.keys: dict[int, str] = {}
        self.precise = precise_closure_enabled() if precise is None else precise
        self.drop_resource_destinations = False
        """negative control only: resource / data destinations contribute nothing to the closure"""

    def _digest(self, index: int) -> str:
        digest = self.digests.get(index)
        if digest is None:
            digest = self.digests[index] = content_digest(self.graph.vertices[index], self.root)
        return digest

    def _key(self, index: int) -> str:
        key = self.keys.get(index)
        if key is None:
            key = self.keys[index] = block_key(self.graph.vertices[index], self.root)
        return key

    def signature(self, block_index: int) -> str:
        """Digest of a counted block's read closure: every member's content and every edge inside it (stable keys).
        Equal signatures => the handler computes the same statement."""
        if self.precise:
            return self._precise_signature(block_index)
        closure = read_closure(self.graph, block_index)
        members = sorted(self._digest(i) for i in closure)
        edges = sorted(json.dumps([self._key(e.origin), self._key(e.dest), e.label])
                       for i in closure for e in self.graph.out_edges.get(i, []))
        return hashlib.sha256(json.dumps([members, edges]).encode()).hexdigest()

    def _precise_signature(self, block_index: int) -> str:
        """Closure walked per (vertex, attribute set). The counted block: its count / for_each attribute only. A
        vertex reached through an edge whose label is attribute A reads A; its destination reads either everything
        (non resource / data) or the attributes A's value references on that destination."""
        graph = self.graph
        start = graph.vertices[block_index]
        roots = [a for a in (COUNT_STRING, FOREACH_STRING) if a in start.attributes]
        wanted: dict[int, Optional[set[str]]] = {block_index: set(roots)}
        """vertex -> attribute names read from it (None = whole content)"""
        stack = [block_index]
        while stack:
            index = stack.pop()
            attrs = wanted[index]
            for edge in graph.out_edges.get(index, []):
                if attrs is not None and not _label_in(edge.label, attrs):
                    continue
                dest_attrs = self._read_from_destination(index, edge)
                if self.drop_resource_destinations and graph.vertices[edge.dest].block_type in RESOURCE_LIKE:
                    dest_attrs = set()
                if _merge(wanted, edge.dest, dest_attrs):
                    stack.append(edge.dest)
        parts = []
        for index in sorted(wanted, key=self._key):
            attrs = wanted[index]
            vertex = graph.vertices[index]
            if attrs is None:
                parts.append([self._key(index), self._digest(index)])
            else:
                values = {a: v for a, v in vertex.attributes.items() if _label_in(a, attrs)}
                parts.append([self._key(index), sorted(attrs), _anonymised(values, self.root)])
            for edge in graph.out_edges.get(index, []):
                if attrs is None or _label_in(edge.label, attrs):
                    parts.append([self._key(index), self._key(edge.dest), edge.label])
        return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()

    def _read_from_destination(self, origin: int, edge: Any) -> Optional[set[str]]:
        """Attributes of edge.dest the renderer can read when evaluating `edge`; None = all of them."""
        dest = self.graph.vertices[edge.dest]
        if dest.block_type not in RESOURCE_LIKE:
            return None
        from checkov.terraform.graph_builder.utils import get_referenced_vertices_in_value

        value = self.graph.vertices[origin].attributes.get(edge.label)
        try:
            references = get_referenced_vertices_in_value(value=value, aliases={},
                                                          resources_types=self.graph.get_resources_types_in_graph())
        except Exception:
            return None
        attrs: set[str] = set()
        dest_name = dest.name.split("[")[0]
        for reference in references:
            if reference.block_type != dest.block_type:
                continue
            joined = ".".join(reference.sub_parts)
            if not (joined == dest_name or joined.startswith(dest_name + ".")):
                continue
            rest = joined[len(dest_name) + 1:] if joined != dest_name else ""
            if not rest:
                return None
            attrs.add(rest)
            attrs.add(rest.split(".")[0])
        if not attrs:
            return None
        return attrs | {"binding"}


def _label_in(label: str, attrs: set[str]) -> bool:
    """An attribute (or edge label) belongs to the read set: exact, or one is a dotted prefix of the other."""
    if label in attrs:
        return True
    return any(label.startswith(a + ".") or a.startswith(label + ".") for a in attrs)


def _merge(wanted: dict[int, Optional[set[str]]], index: int, attrs: Optional[set[str]]) -> bool:
    """Union `attrs` into wanted[index]; True when the set grew (the vertex must be (re)visited)."""
    if index not in wanted:
        wanted[index] = None if attrs is None else set(attrs)
        return True
    current = wanted[index]
    if current is None:
        return False
    if attrs is None:
        wanted[index] = None
        return True
    if attrs <= current:
        return False
    current |= attrs
    return True


def closure_signature(graph: Any, block_index: int, root: str) -> str:
    return _ClosureSignatures(graph, root).signature(block_index)


def _counted_blocks(handler: Any) -> list[int]:
    return [i for i, b in enumerate(handler.local_graph.vertices)
            if b.block_type == handler.block_type_to_handle
            and (FOREACH_STRING in b.attributes or COUNT_STRING in b.attributes)]


def _json_statement(statement: Any) -> Any:
    """Statements are int / list[str] / dict[str, Any] / None; JSON-safe for the artifact."""
    return json.loads(json.dumps(statement, cls=CustomJSONEncoder, default=str))


def same_expansion(a: Any, b: Any) -> bool:
    """Whether two statements produce the same instances: Checkov's _create_new_resources skips every falsy statement
    (None: not resolvable, 0, empty list / dict), so all of them leave the block unexpanded."""
    if not a and not b:
        return True
    return _json_statement(a) == _json_statement(b)


@dataclass
class ExpansionRecorder:
    """Baseline: records every handler call's statements with the read-closure signature of each block."""

    root: str
    records: dict[str, dict[str, Any]] = field(default_factory=dict)

    def statements(self, handler: Any, resources_blocks: list[int]) -> Any:
        graph = handler.local_graph
        full = _ClosureSignatures(graph, self.root, precise=False)
        precise = _ClosureSignatures(graph, self.root, precise=True)
        weak = _weakened_signatures(graph, self.root)
        before = {index: (full.signature(index), precise.signature(index), weak.signature(index) if weak else None)
                  for index in _counted_blocks(handler)}
        result = handler._get_statements_checkov(resources_blocks)
        for index, (signature, precise_signature, weakened) in before.items():
            key = block_key(graph.vertices[index], self.root)
            self.records[key] = {"signature": signature, "precise_signature": precise_signature,
                                 "statement": _json_statement(result.get(index))}
            if weakened is not None:
                self.records[key]["weakened_signature"] = weakened
        return result


@dataclass
class ExpansionOracle:
    """PR scan: reuse the baseline statement of every block whose read-closure signature is unchanged; recompute the
    rest with Checkov's own code (the sub-graph render then only covers those blocks' read closures)."""

    root: str
    records: dict[str, dict[str, Any]]
    reused: list[str] = field(default_factory=list)
    recomputed: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)
    """block keys whose recomputed statement differs from the baseline's (the expansion really changed)"""
    decided: dict[str, Any] = field(default_factory=dict)
    """block key -> statement used (reused or recomputed)"""

    def _weakened_closure_unchanged(self, graph: Any, index: int, key: str) -> bool:
        """Negative control: compare closure signatures that ignore resource / data destinations entirely (the
        baseline side recomputed the same weakened way from the baseline's pre-expansion graph, stored by the
        control's own baseline run: `weakened_signature`)."""
        weak = _weakened_signatures(graph, self.root)
        record = self.records.get(key) or {}
        return record.get("weakened_signature") == weak.signature(index)

    def statement_for(self, key: str) -> Any:
        """The statement the last statements() call decided for this block (reused or recomputed)."""
        return self.decided[key]

    def statement_changed(self, key: str) -> bool:
        return key in self.changed

    def statements(self, handler: Any, resources_blocks: list[int]) -> Any:
        graph = handler.local_graph
        signatures = _ClosureSignatures(graph, self.root)
        field_name = SIGNATURE_FIELD[signatures.precise]
        result: dict[int, Any] = {}
        to_compute: list[int] = []
        for index in _counted_blocks(handler):
            key = block_key(graph.vertices[index], self.root)
            record = self.records.get(key)
            stale_ok = NEGATIVE_CONTROL == "stale_expansion" and record is not None
            if record is not None and NEGATIVE_CONTROL == "imprecise_closure_drop_destinations":
                stale_ok = self._weakened_closure_unchanged(graph, index, key)
            if record is not None and (stale_ok or record.get(field_name) == signatures.signature(index)):
                result[index] = _restore_statement(record["statement"])
                self.decided[key] = result[index]
                self.reused.append(key)
            else:
                to_compute.append(index)
        if to_compute:
            computed = _checkov_statements_for(handler, to_compute)
            for index in to_compute:
                key = block_key(graph.vertices[index], self.root)
                statement = computed.get(index)
                result[index] = statement
                self.decided[key] = statement
                self.recomputed.append(key)
                record = self.records.get(key)
                if record is None or not same_expansion(statement, record["statement"]):
                    self.changed.append(key)
        return result


def _restore_statement(statement: Any) -> Any:
    return statement


def _checkov_statements_for(handler: Any, blocks: list[int]) -> dict[int, Any]:
    """ForeachEntityHandler._get_statements restricted to `blocks`: same static / dynamic split, same sub-graph render,
    with only these blocks as blocks_to_render (a dynamic block's value depends only on its own read closure)."""
    statements: dict[int, Any] = {}
    for index in blocks:
        statements[index] = handler._get_static_foreach_statement(index)
    dynamic = [index for index, statement in statements.items() if statement is None]
    if dynamic:
        statements.update(handler._handle_dynamic_statement(dynamic))
    return statements


def recorder_for(graph: Any) -> Optional[ExpansionRecorder]:
    return getattr(graph, "foreach_statement_oracle", None)
