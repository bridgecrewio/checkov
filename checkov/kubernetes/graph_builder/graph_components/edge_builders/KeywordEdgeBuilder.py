from __future__ import annotations

from checkov.kubernetes.graph_builder.graph_components.edge_builders.K8SEdgeBuilder import K8SEdgeBuilder
from checkov.kubernetes.graph_builder.graph_components.blocks import KubernetesBlock
from checkov.kubernetes.graph_builder.graph_components.ResourceKeywordIdentifier import ResourceKeywordIdentifier
from checkov.kubernetes.kubernetes_utils import FILTERED_RESOURCES_FOR_EDGE_BUILDERS


class KeywordEdgeBuilder(K8SEdgeBuilder):

    @staticmethod
    def should_search_for_edges(vertex: KubernetesBlock) -> bool:
        return vertex.attributes.get("kind") in ResourceKeywordIdentifier.KINDS_KEYWORDS_MAP.keys() \
            and vertex.attributes.get("kind") not in FILTERED_RESOURCES_FOR_EDGE_BUILDERS

    @staticmethod
    def find_connections(vertex: KubernetesBlock, vertices: list[KubernetesBlock]) -> list[int]:
        """
        connection is defined by a match between a vertex's (of a certain type) references definitions to a potential
        vertex (of any type).

        example:
        A Pod with the property 'spec.serviceAccountName' with value 'service-123' will match a resource of type
        'ServiceAccount' with a 'metadata.name' property equals to 'service-123'
        """

        connections: list[int] = []
        for potential_vertex_index, potential_vertex in enumerate(vertices):
            if potential_vertex.id == vertex.id:
                continue
            resource_references_definitions: list[dict[str, str] | list[dict[str, dict[str, str]]]] = ResourceKeywordIdentifier.KINDS_KEYWORDS_MAP[vertex.attributes["kind"]]  # type: ignore[assignment]
            # check that resource items comply to all references definitions defined in ResourceKeywordIdentifier
            for references_definition in resource_references_definitions:
                match = True

                if isinstance(references_definition, dict):
                    for potential_vertex_key, vertex_key in references_definition.items():
                        match = KeywordEdgeBuilder._find_match_in_attributes(vertex, potential_vertex, potential_vertex_key, vertex_key, match)
                    if match:
                        connections.append(potential_vertex_index)

                # some items are nested in lists and their value in the vertex is concatenated with their index,
                # like so:  subjects.0.name
                elif isinstance(references_definition, list):
                    # not really a loop, just extracting the dict's key
                    for base_key_attribute, reference_definitions_items in references_definition[0].items():
                        vertex_attribute_references_list: list[dict[str, str]] = vertex.attributes.get(base_key_attribute)  # type: ignore[assignment]
                        if not vertex_attribute_references_list:
                            continue
                        # iterate every item on the list as a separate resource
                        for i in range(len(vertex_attribute_references_list)):
                            match = True
                            for potential_vertex_key, vertex_key in reference_definitions_items.items():
                                vertex_key = f"{base_key_attribute}.{i}.{vertex_key}"
                                match = KeywordEdgeBuilder._find_match_in_attributes(vertex, potential_vertex, potential_vertex_key, vertex_key, match)
                            if match:
                                connections.append(potential_vertex_index)

        return connections

    @staticmethod
    def _find_match_in_attributes(vertex: KubernetesBlock,
                                  potential_vertex: KubernetesBlock,
                                  potential_vertex_key: str,
                                  vertex_key: str,
                                  match: bool) -> bool:

        vertex_ref = vertex.attributes.get(vertex_key)
        potential_vertex_ref = potential_vertex.attributes.get(potential_vertex_key)
        if vertex_ref is None or potential_vertex_ref is None or vertex_ref != potential_vertex_ref:
            # if not all attributes match then it's not qualified as an edge
            match = False

        return match
