import typing as ty
from functools import wraps

from typedparse.argparse import ArgParserFactory
from typedparse.parser import Parser


def options(**kw):
    def decorator(func):
        func.__options__ = kw

        @wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapped

    return decorator


def parse(obj: ty.Any):
    return ArgParserFactory().create(obj).parse()
