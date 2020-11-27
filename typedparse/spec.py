import inspect
import re
import abc
from dataclasses import dataclass
import typing as ty

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
    default: ty.Optional[ty.Any]
    desc: str

    def is_list(self) -> (bool, ty.Optional[str]):
        result = re.search(r"typing.List\[(.+)]", self.tpe)
        return (True, result.group(1)) if result else (False, None)


class ParserSpec(abc.ABC):
    def __init__(self, name: ty.Optional[str], desc: ty.Optional[str]):
        self.name = name
        self.desc = desc


class ParserNode(ParserSpec):
    def __init__(self, name: ty.Optional[str] = None, desc: ty.Optional[str] = None):
        super().__init__(name, desc)
        self.children: ty.List[ParserSpec] = []

    def add(self, child: ParserSpec):
        self.children.append(child)


class ParserLeaf(ParserSpec):
    def __init__(self, name: ty.Optional[str] = None, desc: ty.Optional[str] = None):
        super().__init__(name, desc)
        self.args: ty.List[Argument] = []

    def add(self, name: str, tpe: str, optional: bool, default: ty.Optional[ty.Any], desc: str):
        self.args.append(Argument(name, tpe, optional, default, desc))

    def get(self, name: str) -> ty.Optional[Argument]:
        for arg in self.args:
            if arg.name == name:
                return arg

        return None


def _create_from_function(obj: ty.Callable, is_method: bool) -> ParserLeaf:
    # args_spec.defaults should be right-aligned to have the same
    # dimension as args_spec.args has
    def align_right(xs: ty.List[ty.Any], n) -> ty.List:
        indent = [None] * (n - len(xs))
        return indent + xs

    args_spec = inspect.getfullargspec(obj)
    doc = parse(inspect.getdoc(obj))
    desc = doc.short_description
    spec = ParserLeaf(obj.__name__, desc)

    offset = 1 if is_method else 0
    defaults = align_right(list(args_spec.defaults), len(args_spec.args) - 1) \
        if args_spec.defaults is not None else [None] * len(args_spec.args[offset:])

    for index, (name, default) in enumerate(zip(args_spec.args[offset:], defaults)):
        tpe = str(args_spec.annotations[name])
        is_opt, in_type = _is_optional(tpe)
        spec.add(name.replace("_", "-"), in_type or _type(tpe), is_opt, default,
                 doc.params[index].description)

    return spec


def _create_from_object(obj: object) -> ParserNode:
    desc = parse(inspect.getdoc(obj)).short_description
    spec = ParserNode(obj.__class__.__name__.lower(), desc)

    for k, v in inspect.getmembers(obj):
        if inspect.ismethod(v) and k != "__init__":
            spec.add(_create_from_function(v, is_method=True))

    return spec


def _create_from_list(obj: list) -> ParserNode:
    spec = ParserNode()

    for child in obj:
        spec.add(_create_from_object(child))

    return spec


def create(obj: ty.Any) -> ParserSpec:
    if isinstance(obj, ty.Callable):
        return _create_from_function(obj, is_method=False)
    elif isinstance(obj, list):
        return _create_from_list(obj)
    elif isinstance(obj, object):
        return _create_from_object(obj)


def _is_optional(tpe: str) -> (bool, ty.Optional[str]):
    result = re.search(r"typing.Union\[(.+), NoneType]", tpe)
    return (True, result.group(1)) if result else (False, None)


def _is_bool(tpe: str) -> bool:
    return tpe == "<class 'bool'>"


def _type(tpe: str) -> str:
    result = re.search(r"<class '(.+)'", tpe)
    return result.group(1) if result else tpe
