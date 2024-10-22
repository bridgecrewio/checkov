from __future__ import annotations

import os
from dataclasses import dataclass

CREATE_COMPLEX_VERTICES = 'CREATE_COMPLEX_VERTICES'
CREATE_EDGES = 'CREATE_EDGES'


@dataclass()
class K8sGraphFlags:
    create_complex_vertices: bool
    create_edges: bool

    def __init__(self, create_complex_vertices: bool = False, create_edges: bool = False) -> None:
        create_complex_vertices_env_var: bool = bool(os.environ.get(CREATE_COMPLEX_VERTICES, True))
        create_edges_env_var: bool = bool(os.environ.get(CREATE_EDGES, True))
        self.create_complex_vertices = create_complex_vertices or create_complex_vertices_env_var
        self.create_edges = create_edges or create_edges_env_var
