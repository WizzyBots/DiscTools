import unittest

from disctools import AutoShardedBot as _AS
from disctools import Bot, Command

from .utils import dummy


class BotTest(unittest.TestCase):
    def setUp(self):
        self.bot = Bot("~")
        self.ABot = _AS("~")

    def test_inject(self):
        class TestCMD(Command):
            main = dummy

        AInst = self.ABot.inject(name="test2")(TestCMD)
        inst = self.bot.inject(name="test2")(TestCMD)

        self.assertIn(AInst, self.ABot.all_commands.values())
        self.assertIn(inst, self.bot.all_commands.values())

if __name__ == "__main__":
    unittest.main()
