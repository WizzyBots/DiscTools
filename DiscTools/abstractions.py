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

from discord.ext.commands import Cog as _Cog, Bot as _Bot, AutoShardedBot as _ABot
from typing import Union

# Saves me a few characters
class Cog(_Cog):
    """An abstracted cog subclass

    This has the normal __init__(self, bot) method.

    Attributes
    ----------
    bot : Union[:class:`discord.ext.commands.Bot`, :class:`discord.ext.commands.AutoShardedBot`]
        The bot instance.
    """
    def __init__(self, bot: Union[_Bot, _ABot]):
        self.bot = bot

# class _(str):
#     """A string subclass for future i18n"""
#     pass