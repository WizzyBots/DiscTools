# Quality: Shit, !!TODO:: <Try other implementation>

import subprocess
import sys

class Installer:
    """A callable which installs packages

    The installations might be partial on some versions of pip
    """

    def __init__(self, bot, Dir):
        self.bot = bot
        self.Dir = Dir

        if not hasattr(self.bot, "alive_popen"):
            bot.alive_popen = []

    async def __call__(self, package: str):
        """Install a package at a path using pip

        This creates a subprocess.Popen Object, which is appended to bot.alive_popen
        to be later(on exit) on cleaned up using `Popen.wait <https://docs.python.org/3/library/subprocess.html#subprocess.Popen.wait/>`_ or any other method.
        """
        bot.alive_popen.append(subprocess.Popen([sys.executable, "-m", "pip", "install", package, "-t", self.Dir, "-U"]))
