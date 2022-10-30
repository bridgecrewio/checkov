from __future__ import annotations

from checkov.kubernetes.graph_builder.graph_components.K8SEdgeBuilder import K8SEdgeBuilder
from checkov.kubernetes.graph_builder.graph_components.blocks import KubernetesBlock
from checkov.kubernetes.graph_builder.graph_components.ResourceKeywordIdentifier import ResourceKeywordIdentifier
from checkov.common.util.type_forcers import force_list


class KeywordEdgeBuilder(K8SEdgeBuilder):

    @staticmethod
    def should_search_for_edges(vertex: KubernetesBlock) -> bool:
        return vertex.attributes.get("kind") in ResourceKeywordIdentifier.KINDS_KEYWORDS_MAP.keys()

    # @staticmethod
    # def find_connections(vertex: KubernetesBlock, vertices: list[KubernetesBlock]) -> list[int]:
    #     """
    #
    #     """
    #
    #     connections: list[int] = []
    #     for potential_vertex_index, potential_vertex in enumerate(vertices):
    #         if potential_vertex.id == vertex.id:
    #             continue
    #         references_definitions = ResourceKeywordIdentifier.KINDS_KEYWORDS_MAP[vertex.attributes["kind"]]
    #         for references_definition in references_definitions:
    #             match = True
    #             for reference_key, reference_value in references_definition.items():
    #                 vertex_ref = vertex.attributes.get(reference_value)
    #                 potential_vertex_ref = potential_vertex.attributes.get(reference_key)
    #                 if vertex_ref != potential_vertex_ref:
    #                     # not all attributes qualify for creating an edge
    #                     match = False
    #                     break
    #             if match:
    #                 connections.append(potential_vertex_index)
    #
    #     return connections

    @staticmethod
    def find_connections(vertex: KubernetesBlock, vertices: list[KubernetesBlock]) -> list[int]:
        """

        """

        connections: list[int] = []
        for potential_vertex_index, potential_vertex in enumerate(vertices):
            if potential_vertex.id == vertex.id:
                continue
            references_definitions = ResourceKeywordIdentifier.KINDS_KEYWORDS_MAP[vertex.attributes["kind"]]
            for references_definition in references_definitions:
                match = True
                # check that resource items comply to all references definitions defined in ResourceKeywordIdentifier
                for reference_key, reference_value in references_definition.items():
                    reference_is_list = True if isinstance(reference_value, list) else False
                    reference_values_list = force_list(reference_value)
                    # some items are nested in lists and their value in the vertex is concatenated with their index,
                    # like so:  subjects.0.name
                    # the following lines force all properties to a list for ease of use and concatenate the index
                    # only to items that are actual lists
                    for i, reference_value_item in enumerate(reference_values_list):
                        if reference_is_list:
                            reference_value_item = f".{i}.".join(reference_value_item.split(".", 1))
                        vertex_ref = vertex.attributes.get(reference_value_item)
                        potential_vertex_ref = potential_vertex.attributes.get(reference_key)
                        if vertex_ref is None or potential_vertex_ref is None or vertex_ref != potential_vertex_ref:
                            # if not all attributes match then it's not qualified as an edge
                            match = False
                            break
                if match:
                    connections.append(potential_vertex_index)
                    break

        return connections
