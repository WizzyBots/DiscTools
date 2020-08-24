import unittest
from disctools import Command, CCmd, ICCmd, ICommand, inject, inject_cmd

class CMDTest(unittest.TestCase):
    def test_inject(self):
        class dummy:
            @inject()
            class test(Command): pass
        self.assertIsInstance(dummy.test, Command)

    def test_inject_cmd(self):
        class dummy:
            @inject_cmd(Command())
            async def Dummy(self): pass

        self.assertIsInstance(dummy.Dummy, Command)

    def test_cmd(self):
        @inject()
        class test(Command): pass

        self.assertEqual(test.name, "test")
        self.assertEqual(test.main, test.callback)

    def test_ccmd(self):
        class testCCmd(CCmd):
            @inject()
            class dummy(Command): pass

        self.assertIsInstance(testCCmd().dummy, Command)

    def test_ICommand(self):
        class Inst(ICommand): pass

        self.assertIsInstance(Inst, Command)
    
    def test_ICCmd(self):
        class Inst(ICCmd): pass

        self.assertIsInstance(Inst, CCmd)

if __name__ == "__main__":
    unittest.main()