import typing as ty
from functools import wraps

from typedparse.argparse import ArgParserFactory


def options(**kw):
    def decorator(func):
        func.__options__ = kw

        @wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapped

    return decorator


def parse(obj: ty.Any, generate_short_flags: bool = False):
    """Parse command line arguments by specification.

    Args:
        obj: An object which specifies a mapping of the arguments. It can be a function, a class or a list.
        generate_short_flags: Generate short flags for all optional formal parameters.
    """
    return ArgParserFactory(generate_short_flags=generate_short_flags).create(obj).parse()
