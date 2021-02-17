import unittest

from disctools import CCmd, Command, ICCmd, ICommand, inject, inject_cmd

from .utils import dummy as _dummy


class CMDTest(unittest.TestCase):
    def test_inject(self):
        class dummy:
            main = _dummy
            @inject()
            class test(Command):
                main = _dummy
        self.assertIsInstance(dummy.test, Command)

    def test_inject_cmd(self):
        class dummy:
            @inject_cmd(Command(func=_dummy))
            async def Dummy(self): pass

        self.assertIsInstance(dummy.Dummy, Command)

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

    def test_ICommand(self):
        class Inst(ICommand):
            main = _dummy

        self.assertIsInstance(Inst, Command)

    def test_ICCmd(self):
        class Inst(ICCmd):
            main = _dummy

        self.assertIsInstance(Inst, CCmd)

if __name__ == "__main__":
    unittest.main()
