import unittest
import typing as ty

import typedparse.spec as spec


class TestParserSpec(unittest.TestCase):
    def test_positional_and_optional_args(self):
        def add(param1: str = "default", param2: ty.Optional[str] = None, param3: ty.Optional[str] = None,
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

        self.assertEqual(spec.Argument(name="param2", tpe="str", optional=True,
                                       default=None, desc="do something 2"), s.get("param2"))

        self.assertEqual(spec.Argument(name="param3", tpe="str", optional=True,
                                       default=None, desc="do something 3"), s.get("param3"))

        self.assertEqual(spec.Argument(name="param4", tpe="str", optional=True,
                                       default=None, desc="do something 4"), s.get("param4"))

        self.assertEqual(spec.Argument(name="param5", tpe="bool", optional=True,
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
