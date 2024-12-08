# -*- coding: utf-8 -*-
"""
=================
stopit.processstop
=================

Control the timeout of blocks or callables with a context manager or a
decorator. Based on the use of multiprocessing for enforcing timeouts.
"""

from __future__ import annotations

import multiprocessing
from typing import Callable, Any

from .utils import TimeoutException, BaseTimeout, base_timeoutable


def process_target(block: Callable, args: tuple, kwargs: dict, return_dict: dict) -> None:
    """Run the block of code in a subprocess.

    :param block: The function to execute in the subprocess.
    :param args: Positional arguments for the block function.
    :param kwargs: Keyword arguments for the block function.
    :param return_dict: Shared dictionary to store the result or error.
    """
    try:
        # Call the block function with provided arguments and store the result
        result = block(*args, **kwargs)
        return_dict['result'] = result
    except Exception as e:
        # Store the error in return_dict
        return_dict['error'] = str(e)


class ProcessTimeout(BaseTimeout):
    """Context manager for enforcing timeouts using multiprocessing.

    See :class:`stopit.utils.BaseTimeout` for more information
    """
    def __init__(self, seconds: int, swallow_exc: bool = True) -> None:
        super().__init__(seconds, swallow_exc)
        self.process: multiprocessing.Process | None = None
        self.manager: multiprocessing.Manager | None = None
        self.return_dict: multiprocessing.Dict | None = None
        self.block: Callable | None = None
        self.args: tuple = ()
        self.kwargs: dict = {}

    def set_block(self, block: Callable, *args: Any, **kwargs: Any) -> None:
        """Set the block of code to execute
        """
        if not callable(block):
            raise ValueError("Block function must be callable.")
        self.block = block
        self.args = args
        self.kwargs = kwargs

    def setup_interrupt(self) -> None:
        """Setting up the resource that interrupts the block
        """
        if not self.block:
            raise ValueError("No block function provided for execution.")

        self.manager = multiprocessing.Manager()
        self.return_dict = self.manager.dict()

        # Start the subprocess
        self.process = multiprocessing.Process(
            target=process_target, args=(self.block, self.args, self.kwargs, self.return_dict)
        )
        self.process.start()

        # Wait for the process to complete or timeout
        self.process.join(self.seconds)
        if self.process.is_alive():
            # If still alive after timeout, terminate and raise TimeoutException
            self.process.terminate()
            self.state = self.TIMED_OUT
            raise TimeoutException(f"Block exceeded maximum timeout value ({self.seconds} seconds).")

    def suppress_interrupt(self) -> None:
        """Removing the resource that interrupts the block
        """
        if self.process and self.process.is_alive():
            self.process.terminate()  # Ensure the process is terminated
        if 'error' in self.return_dict:
            raise Exception(f"Error during execution: {self.return_dict['error']}")
        if self.manager:
            self.manager.shutdown()

    def get_result(self) -> Any:
        """Retrieve the result of the block execution
        """
        if self.return_dict and 'result' in self.return_dict:
            return self.return_dict['result']
        return None


class process_timeoutable(base_timeoutable):  # noqa: B903
    """A function or method decorator that raises a ``TimeoutException`` for
    decorated functions that exceed a certain amount of time. This uses the
    ``ProcessTimeout`` context manager.

    See :class:`.utils.base_timeoutable`` for further comments.
    """
    def __init__(self) -> None:
        super().__init__()
        self.to_ctx_mgr = ProcessTimeout
