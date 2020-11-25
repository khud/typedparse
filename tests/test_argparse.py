import unittest
import typing as ty

from typedparse.argparse import ArgParserFactory


class TestParserSpec(unittest.TestCase):
    def test_simple_parser(self):
        def main(filename: str, number: ty.Optional[int]):
            """My brand-new cli

            Args:
                filename: file path
                number: number of lines
            """
            print(f"filename: {filename}")
            print(f"number: {number}")

        parser = ArgParserFactory().create(main)
        parser.parse(["--number", "4", "test.txt"])
        parser.parser.print_help()
