import abc
import typing as ty
from argparse import ArgumentParser, Namespace

import typedparse.spec as spec
from typedparse.parser import Parser, ParserFactory


class AbstractArgParser(abc.ABC, Parser):
    def __init__(self, parser: ArgumentParser):
        self.parser = parser

    def parse(self, args: ty.Optional[ty.List[str]] = None):
        args = self.parser.parse_args(args)
        args.func(args)


class ArgParserLeaf(AbstractArgParser):
    def __init__(self, parser: ArgumentParser, sp: spec.ParserLeaf):
        super().__init__(parser)

        def to_bool(s: str) -> bool:
            if s.lower() in ['yes', 'true', 't', 'y', '1']:
                return True
            elif s.lower() in ['no', 'false', 'f', 'n', '0']:
                return False
            else:
                raise ValueError(f"Boolean required but found {s}")

        def func(args: Namespace):
            args = vars(args)
            actual_args = [args[a.name if a.tpe == "bool" else a.get_metavar()] for a in sp.args]
            sp.func(*actual_args)

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

            if tpe == "bool":
                if arg.optional:
                    if arg.default:
                        kwargs.update(action="store_false")
                    else:
                        kwargs.update(action="store_true")
                else:
                    kwargs.update(type=to_bool)

                    if arg.default:
                        kwargs.update(nargs="?")
            else:
                kwargs.update(type=spec.get_class(tpe))
                kwargs.update(metavar=metavar)

            if arg.optional:
                kwargs.update(dest=arg.name)

            flags = arg.get_flags()

            self.parser.add_argument(*flags, help=arg.desc, **kwargs)

        self.parser.set_defaults(func=func)


class ArgParserNode(AbstractArgParser):
    def __init__(self, parser: ArgumentParser, sp: spec.ParserNode):
        super().__init__(parser)
        sub = self.parser.add_subparsers()
        for child in sp.children:
            parser = sub.add_parser(child.name)
            factory = ArgParserFactory(parser)
            factory.create(child)


class ArgParserFactory(ParserFactory):
    def __init__(self, parser: ty.Optional[ArgumentParser] = None):
        self.parser = parser or ArgumentParser()

    def create(self, obj: ty.Any) -> Parser:
        if not isinstance(obj, spec.ParserSpec):
            obj = spec.create(obj)

        if isinstance(obj, spec.ParserLeaf):
            return ArgParserLeaf(self.parser, obj)
        elif isinstance(obj, spec.ParserNode):
            return ArgParserNode(self.parser, obj)
        else:
            raise ValueError(obj)
