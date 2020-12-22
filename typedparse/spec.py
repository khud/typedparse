import abc
import inspect
import re
import typing as ty
from dataclasses import dataclass

from docstring_parser import parse


@dataclass
class Argument(object):
    name: str
    tpe: str
    optional: bool
    default: ty.Optional[ty.Any]
    desc: str
    options: ty.Optional[ty.Any] = None

    def is_list(self) -> (bool, ty.Optional[str]):
        result = re.search(r"typing.List\[(.+)]", self.tpe)
        return (True, result.group(1)) if result else (False, None)

    def get_flags(self) -> ty.List[str]:
        flags_opt = self.get_option("flags")

        if flags_opt:
            return self._get_flags(flags_opt)
        else:
            return self._get_flags(self.options)

    def _get_flags(self, options: ty.Optional[ty.Dict]) -> ty.List[str]:
        name = f"--{self.name}" if self.optional else self.name

        if options:
            if isinstance(options, list):
                return options
            elif isinstance(options, str):
                return [name, options]

        return [name]

    def get_option(self, key: str) -> ty.Optional[ty.Any]:
        if self.options and isinstance(self.options, ty.Dict):
            return self.options.get(key, None)
        else:
            return None

    def get_metavar(self) -> str:
        this = self

        def remove_dashes(long_flag: str) -> str:
            return long_flag[2:] if this.optional else long_flag

        metavar = self.get_option("metavar")

        if metavar:
            return metavar

        flags = self.get_flags()

        if len(flags) == 1:
            if len(flags[0]) == 1:
                return self.name
            else:
                long = flags[0]
                return remove_dashes(long)

        if len(flags) == 2:
            long = flags[0] if len(flags[1]) == 1 else flags[1]
            return remove_dashes(long)


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
    def __init__(self, func: ty.Callable, name: ty.Optional[str] = None, desc: ty.Optional[str] = None):
        super().__init__(name, desc)
        self.func = func
        self.args: ty.List[Argument] = []

    def add(self, arg):
        self.args.append(arg)

    def get(self, name: str) -> ty.Optional[Argument]:
        for arg in self.args:
            if arg.name == name:
                return arg

        return None


def _create_from_function(func: ty.Callable) -> ParserLeaf:
    args_spec = inspect.signature(func)
    doc = parse(inspect.getdoc(func))
    desc = doc.short_description
    spec = ParserLeaf(func, func.__name__, desc)

    for index, name in enumerate(args_spec.parameters):
        tpe = str(args_spec.parameters[name].annotation)
        default = args_spec.parameters[name].default
        default = default if default != args_spec.empty else None
        is_opt, in_type = _is_optional(tpe)
        options = func.__options__.get(name, None) if hasattr(func, "__options__") else None
        spec.add(Argument(name=name,
                          tpe=in_type or _type(tpe),
                          optional=is_opt,
                          default=default,
                          desc=doc.params[index].description,
                          options=options
                          ))

    return spec


def _create_from_object(obj: object) -> ParserNode:
    desc = parse(inspect.getdoc(obj)).short_description
    spec = ParserNode(obj.__class__.__name__.lower(), desc)

    for k, v in inspect.getmembers(obj):
        if inspect.ismethod(v) and k != "__init__":
            spec.add(_create_from_function(v))

    return spec


def _create_from_list(obj: list) -> ParserNode:
    spec = ParserNode()

    for child in obj:
        if isinstance(child, ty.Callable):
            spec.add(_create_from_function(child))
        elif isinstance(child, object):
            spec.add(_create_from_object(child))

    return spec


def create(obj: ty.Any) -> ParserSpec:
    if isinstance(obj, ty.Callable):
        return _create_from_function(obj)
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


def get_class(class_name):
    parts = class_name.split('.')
    module = ".".join(parts[:-1])
    if module:
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m
    elif class_name == "int":
        return int
    elif class_name == "float":
        return float
    elif class_name == "bool":
        return bool
    elif class_name == "str":
        return str
    else:
        return globals()[class_name]
