# MIT License

# Copyright (c) 2020 TEEN-BOOM

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from discord.ext.commands.bot import BotBase as _Base
from discord.ext.commands import Bot as _Bot, AutoShardedBot as _AS, GroupMixin as _GM

class InjectableBotMixin(_GM):
    def inject(self, **kwargs):
        """Inject a command class into the Bot.

        This is a decorator.
        """
        def decorator(cls):
            kwargs.setdefault('parent', self)
            result = cls(**kwargs)
            self.add_command(result)
            return result

        return decorator
    
    def inject_cmd(self, inst) -> None:
        """Inject a command instance into the Bot.

        This is not a decorator, but a method.
        Useful when you want to inject an imported command,
        but don't want to subclass it to inject

        """
        return self.add_command(inst)

class Bot(InjectableBotMixin, _Bot):
    """Represents a discord bot.

    This class is a subclass of :class:`discord.ext.commands.Bot`
    """
    pass

class AutoShardedBot(InjectableBotMixin, _AS):
    """This is similar to :class:`.Bot` except that it has inherited from
    :class:`discord.ext.commands.AutoShardedBot` instead.
    """
    pass
