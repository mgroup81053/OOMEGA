import re
import typing
import inspect
from contextlib import suppress
from functools import wraps


Real_name = "FloatReal"
Matrix_name = "PureMatrix"
Vector_name = "PureVector"

class UnsupportedOperandTypeError(TypeError):
    def __init__(self, a, b):
        raise TypeError(f"unsupported operand type(s) for +: '{type(a).__name__}' and '{type(b).__name__}'")



# Modified
# FIXME: Cannot handle list[...]
# https://stackoverflow.com/questions/50563546/validating-detailed-types-in-python-dataclasses
def enforce_types(callable):
    spec = inspect.getfullargspec(callable)

    def check_type(*args, **kwargs):
        parameters = dict(zip(spec.args, args))
        parameters.update(kwargs)
        for name, value in parameters.items():
            with suppress(KeyError):  # Assume un-annotated parameters can be any type
                type_hint = spec.annotations[name]
                if isinstance(type_hint, typing._SpecialForm):
                    # No check for typing.Any, typing.Union, typing.ClassVar (without parameters)
                    continue
                try:
                    actual_type = type_hint.__origin__
                except AttributeError:
                    # In case of non-typing types (such as <class 'int'>, for instance)
                    actual_type = type_hint
                # In Python 3.8 one would replace the try/except with
                # actual_type = typing.get_origin(type_hint) or type_hint
                if isinstance(actual_type, typing._SpecialForm):
                    # case of typing.Union[…] or typing.ClassVar[…]
                    actual_type = type_hint.__args__
                    
                if not isinstance(value, type_hint):
                    raise TypeError(f"Unexpected type for '{name}' (expected {type_hint} but found {type(value).__name__})")

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            check_type(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper

    if inspect.isclass(callable):
        callable.__init__ = decorate(callable.__init__)
        return callable

    return decorate(callable)
