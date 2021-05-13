import unittest

from disctools import CCmd, Command, inject

from .utils import dummy as _dummy


class CMDTest(unittest.TestCase):
    def test_inject(self):
        class dummy:
            main = _dummy
            @inject()
            class test(Command):
                main = _dummy
        self.assertIsInstance(dummy.test, Command)

    def test_cmd(self):
        @inject()
        class test(Command):
            main = _dummy

        self.assertEqual(test.name, "test")
        self.assertEqual(test.main, test.callback)

    def test_ccmd(self):
        class testCCmd(CCmd):
            main = _dummy
            @inject()
            class dummy(Command):
                main = _dummy

        self.assertIsInstance(testCCmd().dummy, Command)

if __name__ == "__main__":
    unittest.main()
