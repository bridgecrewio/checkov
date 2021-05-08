import inspect
from abc import ABCMeta
from functools import update_wrapper
from typing import Callable, Any, TypeVar, Dict, List

T = TypeVar("T")


class MultiSignatureMeta(ABCMeta):
    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        multi_signatures = {
            name: value
            for name, value in namespace.items()
            if hasattr(value, "__multi_signature_wrappers__") and inspect.isfunction(value)
            # isfunction, because function is not bound yet
        }
        # search in base classes for decorated functions
        for base in bases:
            for name, value in getattr(base, "__multi_signature_methods__", {}).items():
                if inspect.isfunction(value) and hasattr(value, "__multi_signature_wrappers__"):
                    multi_signature_wrappers = getattr(value, "__multi_signature_wrappers__", False)
                    if multi_signature_wrappers:
                        current_function = multi_signatures.get(name)
                        if current_function:
                            current_function.__multi_signature_wrappers__.update(multi_signature_wrappers)
                        else:
                            multi_signatures[name] = value

        cls.__multi_signature_methods__ = multi_signatures
        for name, value in multi_signatures.items():
            wrapped = getattr(cls, name)
            arguments = inspect.getargs(wrapped.__code__)
            if arguments == inspect.getargs(value.__code__):
                # Do not replace if the signature is the same
                continue
            # convert args into a tuple
            args, varargs, varkw = arguments
            arguments = tuple(args), varargs, varkw
            get_wrapper = value.__multi_signature_wrappers__.get(tuple(arguments), None)
            if get_wrapper:
                wrapper = get_wrapper(cls, wrapped)
                update_wrapper(wrapper, wrapped)
                setattr(cls, name, wrapper)
            else:
                # unknown implementation
                raise NotImplementedError(f"The signature {arguments} for {name} is not supported.")

        return cls


class multi_signature:
    """
    Decorator to allow other signatures in sub classes.

    You can use this decorator on class methods. The implementation requires that the metaclass of that class is
    :class:`MultiSignatureMeta`
    This class extends :class:`ABCMeta` so it supports abstract base classes.
    """

    def __init__(self) -> None:
        self.__wrappers__: Dict[Any, Callable[..., T]] = {}

    def __call__(self, fn: Callable[..., T]) -> Callable[..., T]:
        fn.add_signature = self.add_signature
        fn.__multi_signature_wrappers__ = self.__wrappers__
        return fn

    def add_signature(
        self, *, args: List[str], varargs: Any = None, varkw: Any = None
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
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

        def wrapper(fn: Callable[..., T]) -> Callable[..., T]:
            self.__wrappers__[(tuple(args), varargs, varkw)] = fn
            return fn

        return wrapper
