from __future__ import annotations

from checkov.kubernetes.graph_builder.graph_components.blocks import KubernetesBlock
from checkov.kubernetes.graph_builder.graph_components.edge_builders.K8SEdgeBuilder import K8SEdgeBuilder


class VertexConncetions:
    def __init__(self, origin_vertex_index: int, destination_vertices_indices: list[int] | None = None) -> None:
        self.origin_vertex_index = origin_vertex_index
        self.destination_vertices_indices = destination_vertices_indices or []


class ServiceAccountEdgeBuilder(K8SEdgeBuilder):
    def __init__(self) -> None:
        self._cache: dict[str, VertexConncetions] = {}

    @staticmethod
    def should_search_for_edges(vertex: KubernetesBlock) -> bool:
        kind: str | None = vertex.attributes.get('kind')
        return kind == 'ServiceAccount'

    def _find_all_service_accounts(self, vertices: list[KubernetesBlock]) -> bool:
        found_service_accounts = False
        for index, vertex in enumerate(vertices):
            service_account_name = vertex.attributes.get('metadata.name')
            if vertex.attributes.get('kind') != 'ServiceAccount' or service_account_name is None:
                continue
            self._cache[service_account_name] = VertexConncetions(index)
            found_service_accounts = True
        return found_service_accounts

    @staticmethod
    def find_connections(vertex: KubernetesBlock, vertices: list[KubernetesBlock]) -> list[int]:
        # DEPRECATED - this is just here for this builder to support the interface. Use `find_connections_for_instance`
        raise NotImplementedError

    def find_connections_for_instance(self, vertex: KubernetesBlock, vertices: list[KubernetesBlock]) -> list[int]:
        if not self._cache:
            found_service_accounts = self._find_all_service_accounts(vertices)
            if found_service_accounts:
                for index, destination_vertex in enumerate(vertices):
                    if destination_vertex.id == vertex.id:
                        continue

                    destination_vertex_ref = destination_vertex.attributes.get('spec.serviceAccountName')
                    if destination_vertex_ref in self._cache:
                        self._cache[destination_vertex_ref].destination_vertices_indices.append(index)

        vertex_ref = vertex.attributes.get('metadata.name')
        if vertex_ref is None:
            return []
        return self._cache[vertex_ref].destination_vertices_indices
