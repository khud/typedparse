import inspect
import re
from dataclasses import dataclass
from typing import Any, Optional, List

# from decorator import decorate
from docstring_parser import parse


# def short(ch: str, arg: str):
#     def deco(func):
#         def wrapped(*args, **kwargs):
#             return func(*args, **kwargs)
#
#         result = decorate(func, wrapped)
#         # result.test = "hello"
#         return result
#
#     return deco


@dataclass
class Argument(object):
    name: str
    tpe: str
    optional: bool
    default: Optional[Any]
    desc: str


class ParserSpec(object):
    def __init__(self, desc: str):
        self.args: List[Argument] = []
        self.desc = desc

    def add(self, name: str, tpe: str, optional: bool, default: Optional[Any], desc: str):
        self.args.append(Argument(name, tpe, optional, default, desc))

    def get(self, name: str) -> Optional[Argument]:
        for arg in self.args:
            if arg.name == name:
                return arg

        return None


def create_spec(obj: object) -> ParserSpec:
    desc = parse(inspect.getdoc(obj)).short_description
    spec = ParserSpec(desc)

    for k, v in inspect.getmembers(obj):
        if inspect.ismethod(v):
            args_spec = inspect.getfullargspec(v)
            doc = parse(inspect.getdoc(v))

            defaults = args_spec.defaults if args_spec.defaults is not None else [None] * len(args_spec.args[1:])
            for index, (name, default) in enumerate(zip(args_spec.args[1:], defaults)):
                tpe = str(args_spec.annotations[name])
                is_opt, in_type = _is_optional(tpe)
                optional = is_opt or (_is_bool(tpe) and default is not None)
                spec.add(name.replace("_", "-"), in_type or _type(tpe), optional, default,
                         doc.params[index].description)

    return spec


def _is_optional(tpe: str) -> (bool, Optional[str]):
    result = re.search(r"typing.Union\[(.+), NoneType]", tpe)
    return (True, result.group(1)) if result else (False, None)


def _is_list(tpe: str) -> (bool, Optional[str]):
    result = re.search(r"typing.List\[(.+)]", tpe)
    return (True, result.group(1)) if result else (False, None)


def _is_bool(tpe: str) -> bool:
    return tpe == "<class 'bool'>"


def _type(tpe: str) -> str:
    result = re.search(r"<class '(.+)'", tpe)
    return result.group(1) if result else tpe
