from __future__ import annotations

import inspect
from abc import ABCMeta
from functools import update_wrapper
from types import CodeType
from typing import Callable, Any, TypeVar, cast
from typing_extensions import Protocol

_MultiT = TypeVar("_MultiT")


class _MultiSignataureMethod(Protocol):
    __code__: CodeType
    __multi_signature_wrappers__: dict[tuple[tuple[str, ...], Any, Any], Callable[..., Any]]

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def add_signature(self, *, args: list[str], varargs: Any = None, varkw: Any = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        ...


class MultiSignatureMeta(ABCMeta):  # noqa: B024  # needs to be ABCMeta, because of the super().__new__ call
    __multi_signature_methods__: dict[str, _MultiSignataureMethod]  # noqa: CCE003

    def __new__(cls, name: str, bases: tuple[Any], namespace: dict[str, Any], **kwargs: Any) -> MultiSignatureMeta:
        mcs = super().__new__(cls, name, bases, namespace, **kwargs)
        multi_signatures: dict[str, _MultiSignataureMethod] = {
            name: value  # type:ignore[misc]
            for name, value in namespace.items()
            if hasattr(value, "__multi_signature_wrappers__") and inspect.isfunction(value)
            # isfunction, because function is not bound yet
        }
        # search in base classes for decorated functions
        for base in bases:
            for name, value in getattr(base, "__multi_signature_methods__", {}).items():
                if inspect.isfunction(value) and hasattr(value, "__multi_signature_wrappers__"):
                    multi_signature_wrappers = getattr(value, "__multi_signature_wrappers__", {})
                    if multi_signature_wrappers:
                        current_function = multi_signatures.get(name)
                        if current_function:
                            current_function.__multi_signature_wrappers__.update(multi_signature_wrappers)
                        else:
                            multi_signatures[name] = cast(_MultiSignataureMethod, value)

        mcs.__multi_signature_methods__ = multi_signatures
        for name, value in multi_signatures.items():
            wrapped = getattr(mcs, name)
            arguments = inspect.getargs(wrapped.__code__)
            if arguments == inspect.getargs(value.__code__):
                # Do not replace if the signature is the same
                continue
            # convert args into a tuple
            args, varargs, varkw = arguments
            multi_signature_key = tuple(args), varargs, varkw
            get_wrapper = value.__multi_signature_wrappers__.get(tuple(multi_signature_key), None)
            if get_wrapper:
                wrapper = get_wrapper(mcs, wrapped)
                update_wrapper(wrapper, wrapped)
                setattr(mcs, name, wrapper)
            else:
                # unknown implementation
                raise NotImplementedError(f"The signature {multi_signature_key} for {name} is not supported.")

        return mcs


class multi_signature:
    """
    Decorator to allow other signatures in sub classes.

    You can use this decorator on class methods. The implementation requires that the metaclass of that class is
    :class:`MultiSignatureMeta`
    This class extends :class:`ABCMeta` so it supports abstract base classes.
    """

    def __init__(self) -> None:
        self.__wrappers__: dict[tuple[tuple[str, ...], Any, Any], Callable[..., _MultiT]] = {}

    def __call__(self, fn: Callable[..., _MultiT]) -> _MultiSignataureMethod:
        fn.add_signature = self.add_signature  # type:ignore[attr-defined]
        fn.__multi_signature_wrappers__ = self.__wrappers__  # type:ignore[attr-defined]
        return cast(_MultiSignataureMethod, fn)

    def add_signature(
        self, *, args: list[str], varargs: Any = None, varkw: Any = None
    ) -> Callable[[Callable[..., _MultiT]], Callable[..., _MultiT]]:
        """
        Registers a new wrapper for the decorated function.

        The decorated function must have two parameters (`cls` and `wrapped`) (The names are not enforced.).
        The first one is the class so this has to be a class function. The second one is the function to wrap.
        It has to return a function that has the same signature as the one decorated with `@multi_signature`.
        The returned function has to call `wrapped`, which is a function with the parameters listed as `args`
        and must return the result of `wrapped`. If the wrapped function has varargs, the name of this variable
        is specified with `varargs`. For keyword args it is `varkw`. See :func:`inspect.getargs` to get the
        correct order.

        The implementation must not handle doc preservation. This is already done by the implementation.

        :param args: the parameters that the wrapped version of the function accepts.
        :param varargs: if the wrapped version uses varargs, this is the name of this
            parameter. If not used, this is `None`.
        :param varkw: if the wrapped version uses keyword arguments, this is the name
            of this parameter. If not used, this is `None`.

        :Example:

        >>> class Example(metaclass=MultiSignatureMeta:
        >>>
        >>>    @multi_signature
        >>>    def some_function(self, a, b, c):
        >>>        pass
        >>>
        >>>    @classmethod
        >>>    @some_function.add_signature("self", "a")
        >>>    def _some_function_self_a(cls, wrapped):
        >>>        def wrapper(self, a, b, c):
        >>>            return wrapped(self, a)
        >>>
        >>>         return wrapper
        """

        def wrapper(fn: Callable[..., _MultiT]) -> Callable[..., _MultiT]:
            self.__wrappers__[(tuple(args), varargs, varkw)] = fn  # type:ignore[assignment]  # mypy bug
            return fn

        return wrapper
