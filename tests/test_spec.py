import typing as ty
import unittest

import typedparse.spec as spec
from typedparse import options


class TestParserSpec(unittest.TestCase):
    def test_positional_and_optional_args(self):
        # note: param5 is positional bool with default value, but param6 is optional bool
        def add(param1: str = "default", param2: int = 10, param3: ty.Optional[int] = 1,
                param4: ty.Optional[str] = None, param5: bool = False, param6: ty.Optional[bool] = None,
                param7: ty.Optional[int] = None):
            """Create a new profile

            Args:
                param1: do something 1
                param2: do something 2
                param3: do something 3
                param4: do something 4
                param5: do something 5
                param6: do something 6
                param7: do something 7
            """
            pass

        s = spec.create(add)

        self.assertTrue(isinstance(s, spec.ParserLeaf))

        s = ty.cast(spec.ParserLeaf, s)

        self.assertEqual("add", s.name)

        self.assertEqual("Create a new profile", s.desc)

        self.assertEqual(spec.Argument(name="param1", tpe="str", optional=False,
                                       default="default", desc="do something 1"), s.get("param1"))

        self.assertEqual(spec.Argument(name="param2", tpe="int", optional=False,
                                       default=10, desc="do something 2"), s.get("param2"))

        self.assertEqual(spec.Argument(name="param3", tpe="int", optional=True,
                                       default=1, desc="do something 3"), s.get("param3"))

        self.assertEqual(spec.Argument(name="param4", tpe="str", optional=True,
                                       default=None, desc="do something 4"), s.get("param4"))

        self.assertEqual(spec.Argument(name="param5", tpe="bool", optional=False,
                                       default=False, desc="do something 5"), s.get("param5"))

        self.assertEqual(spec.Argument(name="param6", tpe="bool", optional=True,
                                       default=None, desc="do something 6"), s.get("param6"))

        self.assertEqual(spec.Argument(name="param7", tpe="int", optional=True,
                                       default=None, desc="do something 7"), s.get("param7"))

    def test_list_args(self):
        def test(files: ty.List[str]):
            """Test files

            Args:
                files: list of files
            """
            pass

        s = spec.create(test)
        s = ty.cast(spec.ParserLeaf, s)
        self.assertEqual(spec.Argument(name="files", tpe="typing.List[str]", optional=False,
                                       default=None, desc="list of files"), s.get("files"))

    def test_spec_from_list_class_or_object(self):
        class CLI:
            def command1(self, filename: str, number: ty.Optional[int] = 0):
                """My command1

                Args:
                    filename: file path
                    number: number of lines
                """
                pass

            def command2(self, test: bool = False, key: ty.Optional[str] = "xxx"):
                """My command2

                Args:
                    test: test mode
                    key: just a key
                """
                pass

        def command1(filename: str, number: ty.Optional[int] = 0):
            """My command1

            Args:
                filename: file path
                number: number of lines
            """
            pass

        def command2(test: bool = False, key: ty.Optional[str] = "xxx"):
            """My command2

            Args:
                test: test mode
                key: just a key
            """
            pass

        def check_spec(s: spec.ParserSpec):
            self.assertTrue(isinstance(s, spec.ParserNode))

            s = ty.cast(spec.ParserNode, s)
            self.assertEqual(2, len(s.children))

            s1 = s.children[0]
            s2 = s.children[1]

            self.assertTrue(isinstance(s1, spec.ParserLeaf))
            self.assertTrue(isinstance(s2, spec.ParserLeaf))

            self.assertEqual("command1", s1.name)
            self.assertEqual("command2", s2.name)

            s1 = ty.cast(spec.ParserLeaf, s1)
            s2 = ty.cast(spec.ParserLeaf, s2)

            self.assertEqual(spec.Argument(name="filename", tpe="str", optional=False,
                                           default=None, desc="file path"), s1.get("filename"))

            self.assertEqual(spec.Argument(name="number", tpe="int", optional=True,
                                           default=0, desc="number of lines"), s1.get("number"))

            self.assertEqual(spec.Argument(name="test", tpe="bool", optional=False,
                                           default=False, desc="test mode"), s2.get("test"))

            self.assertEqual(spec.Argument(name="key", tpe="str", optional=True,
                                           default="xxx", desc="just a key"), s2.get("key"))

        check_spec(spec.create(CLI()))
        check_spec(spec.create(CLI))
        check_spec(spec.create([command1, command2]))

    def test_short(self):
        @options(number="n")
        def my_func(filename: str, number: ty.Optional[int] = 0):
            """My command1

            Args:
                filename: file path
                number: number of lines
            """
            pass

        s = spec.create(my_func)
        s = ty.cast(spec.ParserLeaf, s)

        self.assertEqual(spec.Argument(name="number", tpe="int", optional=True,
                                       default=0, desc="number of lines", options="n"), s.get("number"))
