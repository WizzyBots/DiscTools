import unittest

from disctools import Bot, AutoShardedBot as _AS, Command

class BotTest(unittest.TestCase):
    def setUp(self):
        self.bot = Bot("~")
        self.ABot = _AS("~")
        self.cmd = Command(name="test")
    
    def test_inject_cmd(self):
        self.ABot.inject_cmd(self.cmd)
        self.bot.inject_cmd(self.cmd)
        self.assertIn(self.cmd, self.ABot.all_commands.values())
        self.assertIn(self.cmd, self.bot.all_commands.values())

    def test_inject(self):
        class TestCMD(Command):
            pass

        AInst = self.ABot.inject(name="test2")(TestCMD)
        inst = self.bot.inject(name="test2")(TestCMD)

        self.assertIn(AInst, self.ABot.all_commands.values())
        self.assertIn(inst, self.bot.all_commands.values())

if __name__ == "__main__":
    unittest.main()