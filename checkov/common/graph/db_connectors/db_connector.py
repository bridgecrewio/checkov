from typing import Any


class DBConnector:
    def save_graph(self, local_graph: Any) -> None:
        pass

    def get_reader_endpoint(self) -> None:
        pass

    def get_writer_endpoint(self) -> None:
        pass

    def disconnect(self) -> None:
        pass
