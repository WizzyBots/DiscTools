"""Custom context class for discord."""

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

from typing import Sequence, Optional, Union

import aiohttp
import discord
from discord.ext.commands import Context as _Context

def _compare(value, expr, Iter: Sequence):
    """Compare an Sequence with a single object to see if every element of Sequence satifies expression."""
    for element in Iter:
        if not expr(value, element):
            return element
        else:
            pass
    else:
        return True
    

class Context(_Context):
    """The over-rided context class.
    """

    def __init__(self, **kwargs):
        """Salt and peppa."""
        super().__init__(**kwargs)
        self._target = None
        self.target = self.message.mentions
    
    @property
    def target(self):
        """Sequence[:class:`discord.Member`] : A list of Members that were mentioned, this shall be set on invoke.
        By default it is set to a list of mentions in the message"""
        return self._target

    @target.setter
    def target(self, user: Sequence[discord.Member]) -> None:
        if not isinstance(user, Sequence):
            self._target = [user]
        else:
            self._target = user

    def is_author_target(self, user: discord.Member = None) -> bool:
        """Check if the target is the author

        Parameters
        ----------
        user : Optional[:class:`discord.Member`]
            The user to check, if None then ctx.authour is used. By default None

        Returns
        -------
        bool
            True if the user is the author, else False
        """
        if user is None:
            return self.author in self.target

        return self.author == user

    def is_above(self, user: discord.Member = None) -> bool:
        """Check if author is above target.

        Parameters
        ----------
        user : Optional[:class:`discord.Member`]
            The user to check if none, then first mentioned user is used, by default None

        Returns
        -------
        bool
            True if user above target else False
        """
        if user == self.author:
            return False # REASON:: [1>1 is False]
        if user is None:
            user = self.target[0]
        if self.author == self.guild.owner:
            return True
        if user is not None:
            x = lambda z, y: z > y.top_role
            return _compare(self.author.top_role, x, user)


    async def whisper(self, user: Union[discord.Member, Sequence[discord.Member]] = None, *args, **kwargs) -> None:
        """|coro|
        DM all targets of a command.

        Parameters
        ----------
        user : Optional(Union[:class:`discord.Member`, List[discord.Member]])
            The member(s) to DM. Defaults to self.target.
        args
            The positional arguments that should be used to message the targets.
        kwargs
            The Key-word arguments that should be used to message the targets.

        Returns
        -------
            NoneType
        """                      
        if user is None:
            user = self.target
        if not isinstance(user, Sequence):
            return await user.send(*args, **kwargs)
        else:
            for target in user:
                target.send(*args, **kwargs)

    # async def send(self, content=None, **kwargs) -> discord.Message:
    #     """Convert all messages outbound from the bot to Blurple Embed."""
    #     if content is not None and kwargs.pop("embed", None) is None:
    #         embed = embed = discord.Embed(description=content, colour=discord.Colour.blue())
    #         return await super().send(embed=embed, **kwargs)
    #     else:
    #         return await super().send(content=content, **kwargs)

    async def send_embed(self, *args, **kwargs) -> discord.Message:
        """|coro|
        Send an embed

        This is a shorthand to creating an :class:`discord.Embed` and sending it.
        All arguments are passed to :class:`discord.Embed`.


        Returns
        -------
        :class:`discord.Message`
            The message that was sent.
        """        
        return await self.send(embed=discord.Embed(*args, **kwargs))

    async def web_request(self, url: str) -> aiohttp.ClientResponse:
        """|coro|
        Make a http rquest with aiohttp

        Parameters
        ----------
        url : str
            The url to send the http request

        Returns
        -------
        :class:`aiohttp.ClientResponse`
            The requests response
        """        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                return r