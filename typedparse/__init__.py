import typing as ty

from typedparse.argparse import ArgParserFactory
from typedparse.parser import Parser


def parse(obj: ty.Any):
    return ArgParserFactory().create(obj).parse()
