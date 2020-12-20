import abc
import string
import typing as ty
from argparse import ArgumentParser, Namespace

import typedparse.spec as spec
from typedparse.parser import Parser, ParserFactory


class AbstractArgParser(abc.ABC, Parser):
    def __init__(self, parser: ArgumentParser):
        self._parser = parser

    def parse(self, args: ty.Optional[ty.List[str]] = None):
        args = self._parser.parse_args(args)
        args.func(args)


class ArgParserLeaf(AbstractArgParser):
    def __init__(self, parser: ArgumentParser, sp: spec.ParserLeaf, generate_short_flags: bool):
        super().__init__(parser)

        used_short_flags = []

        def to_bool(s: str) -> bool:
            if s.lower() in ['yes', 'true', 't', 'y', '1']:
                return True
            elif s.lower() in ['no', 'false', 'f', 'n', '0']:
                return False
            else:
                raise ValueError(f"Boolean required but found {s}")

        def func(args: Namespace):
            args = vars(args)
            actual_args = [args[a.name if a.tpe == "bool" or a.optional else a.get_metavar()] for a in sp.args]
            sp.func(*actual_args)

        def generate_short(long_flag: str) -> str:
            index = 2
            while index < len(long_flag) and long_flag[index] in used_short_flags:
                index += 1

            if index == len(long_flag):
                alpha = string.ascii_lowercase
                index = 0
                while index < len(alpha) and alpha[index] in used_short_flags:
                    index += 1

                if index == len(alpha):
                    raise ValueError(f"No more short flag candidates for {long_flag}")
                else:
                    return alpha[index]
            else:
                return long_flag[index]

        for arg in sp.args:
            is_list, in_type = arg.is_list()

            kwargs = {}

            if is_list:
                tpe = in_type
                kwargs.update(nargs=arg.get_option("nargs") or "+")
            else:
                tpe = arg.tpe

            if arg.default is not None or arg.optional:
                if not is_list and tpe != "bool":
                    kwargs.update(nargs="?")

                kwargs.update(default=arg.default)

            metavar = arg.get_metavar()
            metavar = metavar.upper() if arg.optional else metavar

            type_func = arg.get_option("type")

            if tpe == "bool":
                if arg.optional:
                    if arg.default:
                        kwargs.update(action="store_false")
                    else:
                        kwargs.update(action="store_true")
                else:
                    kwargs.update(type=type_func or to_bool)

                    if arg.default:
                        kwargs.update(nargs="?")
            else:
                kwargs.update(type=type_func or spec.get_class(tpe))
                kwargs.update(metavar=metavar)

            if arg.optional:
                kwargs.update(dest=arg.name)

            flags = arg.get_flags()

            if len(flags) == 1 and arg.optional and generate_short_flags:
                if len(flags[0]) > 2:
                    short = generate_short(flags[0])
                    flags.append(f"-{short}")

            for flag in flags:
                if len(flag) == 2:
                    used_short_flags.append(flag[1:])

            self._parser.add_argument(*flags, help=arg.desc, **kwargs)

        self._parser.set_defaults(func=func)


class ArgParserNode(AbstractArgParser):
    def __init__(self, parser: ArgumentParser, sp: spec.ParserNode, generate_short_flags: bool):
        super().__init__(parser)
        sub = self._parser.add_subparsers()
        for child in sp.children:
            parser = sub.add_parser(child.name)
            factory = ArgParserFactory(parser, generate_short_flags)
            factory.create(child)


class ArgParserFactory(ParserFactory):
    def __init__(self, parser: ty.Optional[ArgumentParser] = None, generate_short_flags: bool = False):
        self._parser = parser or ArgumentParser()
        self._generate_short_flags = generate_short_flags

    def create(self, obj: ty.Any) -> Parser:
        if not isinstance(obj, spec.ParserSpec):
            obj = spec.create(obj)

        if isinstance(obj, spec.ParserLeaf):
            return ArgParserLeaf(self._parser, obj, self._generate_short_flags)
        elif isinstance(obj, spec.ParserNode):
            return ArgParserNode(self._parser, obj, self._generate_short_flags)
        else:
            raise ValueError(obj)
