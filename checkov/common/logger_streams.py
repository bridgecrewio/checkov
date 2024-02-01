import shutil
import sys
from io import StringIO
from typing import Dict


class LoggerStreams:
    def __init__(self) -> None:
        self._streams: Dict[str, StringIO] = {}

    def add_stream(self, name: str, stream: StringIO) -> None:
        self._streams[name] = stream

    def get_streams(self) -> Dict[str, StringIO]:
        return self._streams

    def print_to_files(self) -> None:
        for key, value in self._streams.items():
            with open(f'./checkov_debug_{key}.log', 'w') as fp:
                value.seek(0)
                shutil.copyfileobj(value, fp)

    def print_to_console(self) -> None:
        for key, value in self._streams.items():
            print('----')
            print(f'Logger of {key} start')
            print(value.getvalue(), file=sys.stderr)


logger_streams = LoggerStreams()
