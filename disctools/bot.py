# MIT License

# Copyright (c) 2020-present WizzyGeek

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

from typing import Callable, Type, TypeVar

from discord.ext.commands import AutoShardedBot as _AS
from discord.ext.commands import Bot as _Bot
from discord.ext.commands import GroupMixin as _GM
from discord.ext.commands import Command as _C

T = TypeVar("T", bound=_C)

class InjectableBotMixin(_GM):
    def inject(self, **kwargs) -> Callable[[Type[T]], T]:
        """
        Inject a command class into the Bot.

        This is a decorator.
        """
        def decorator(cls: Type[T]) -> T:
            result = cls(**kwargs)
            self.add_command(result)
            return result

        return decorator

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
