import os
from contextlib import contextmanager
from typing import Any, Generator


@contextmanager
def temp_environ(**kwargs: Any) -> Generator[None, None, None]:
    """Temporarily set environment variables and restores previous values

    copy of https://gist.github.com/igniteflow/7267431?permalink_comment_id=2553451#gistcomment-2553451
    """
    original_env = {key: os.getenv(key) for key in kwargs}
    os.environ.update(kwargs)
    try:
        yield
    finally:
        for key, value in original_env.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value
